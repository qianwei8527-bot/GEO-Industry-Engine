'''V10.5 intake service: upload, transparent local analysis, owner confirmation.

The analyzer only records what can be tied to a source snippet. Missing
information stays '待补充' and is never invented. owner confirmation only
means the profile may be used for operations, not verification.
'''

import csv
import hashlib
import io
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evidence import Evidence
from app.models.intake import ClientIntake, IntakeAnalysis
from app.models.realm import RealmDataAuthorization, RealmRegistry
from app.services.governance import get_governance_service
from app.services.intake_rate_limiter import INTAKE_RATE_LIMITS, get_intake_rate_limiter
from app.services.observation_network import validate_url
from app.services.positioning_service import get_positioning_service
from app.services.realm_service import get_realm_service

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.csv', '.txt', '.md', '.png', '.jpg', '.jpeg'}
MAX_FILES = 5
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = MAX_FILES * MAX_FILE_BYTES
MAX_EXTRACTED_CHARS = 300000

FIELD_DEFS = [
    ('enterprise_entity', '企业主体', ['企业主体', '主体']),
    ('brand_name', '品牌名称', ['试点品牌', '品牌名称', '品牌']),
    ('relationship', '域主与品牌关系', ['关系', '附属关系']),
    ('product_service', '核心产品或服务', ['产品', '核心产品', '服务']),
    ('industry_track', '所属行业与细分赛道', ['行业', '赛道', '细分']),
    ('target_customer', '目标客户', ['客户', '目标客户', '受众']),
    ('service_region', '主要服务地区', ['地区', '区域', '城市']),
    ('policy_region', '适用政策地区', ['政策地区', '适用地区']),
    ('existing_channels', '现有渠道', ['渠道']),
    ('competitors', '竞争对象', ['竞争', '竞品']),
    ('business_stage', '当前经营阶段', ['阶段', '起步', '从零']),
    ('client_problem', '客户希望解决的问题', ['问题']),
    ('conversion_goals', '主要转化目标', ['转化目标', '目标']),
    ('industry_position', '当前行业位置', ['行业位置', '位置']),
    ('advantages', '优势', ['优势']),
    ('gaps', '缺口', ['缺口']),
    ('risks', '风险', ['风险']),
]

CITY_NAMES = ['深圳', '北京', '上海', '广州', '杭州', '成都', '重庆', '武汉', '南京', '苏州', '西安', '长沙', '天津', '东莞', '佛山']

PUBLIC_INTAKE_SCOPE = 'intake_submission'
PUBLIC_INTAKE_GRANTEE = 'anonymous_intake'
PUBLIC_DUPLICATE_WINDOW_SECONDS = 86400
PUBLIC_POLICY_VERSION = '2026-08-11.v1'


class IntakeTokenError(Exception):
    def __init__(self, message: str, code: str = 'token_invalid', http_status: int = 401):
        super().__init__(message)
        self.code = code
        self.http_status = http_status


class IntakeRateLimitError(IntakeTokenError):
    def __init__(self, message: str = 'too many submissions, please retry later'):
        super().__init__(message, 'rate_limited', 429)


class IntakeDuplicateError(IntakeTokenError):
    def __init__(self, message: str = 'duplicate submission'):
        super().__init__(message, 'duplicate_submission', 409)


class IntakeFileTooLargeError(Exception):
    pass


class IntakeStateTransitionError(Exception):
    pass


class IntakeService:
    def __init__(self):
        self.realm_service = get_realm_service()
        self.gov = get_governance_service()
        self.rate_limiter = get_intake_rate_limiter()

    async def _control(self, db: AsyncSession, user, realm_id) -> bool:
        registry = await self.realm_service.resolve_registry(db, realm_id)
        if not registry:
            raise ValueError('realm not found')
        return await self.realm_service._control(db, user, str(registry.entity_id))

    async def _audit(self, db, user, action, target_type, target_id, reason=None, metadata=None, commit: bool = True):
        await self.gov.audit(
            db, user.id, action, target_type, target_id,
            reason=reason, actor_label=user.name, metadata=metadata,
            commit=commit,
        )

    async def create_intake(self, db, user, realm_id, payload: Dict) -> Dict:
        if not await self._control(db, user, realm_id):
            raise PermissionError('realm owner/editor permission required')
        registry = await self.realm_service.resolve_registry(db, realm_id)
        if not registry:
            raise ValueError('realm not found')
        intake = ClientIntake(
            intake_code=f'INTK-{uuid.uuid4().hex[:12].upper()}',
            realm_id=registry.id,
            realm_entity_id=registry.entity_id,
            status='uploaded',
            relationship=(payload.get('relationship') or '').strip() or None,
            pasted_text=(payload.get('pasted_text') or '').strip() or None,
            supplemental_notes=(payload.get('supplemental_notes') or '').strip() or None,
            file_manifest=[],
            source_truth_status='observed',
            created_by=user.id,
        )
        db.add(intake)
        await db.flush()
        await db.refresh(intake)
        manifest = await self._save_files(registry.id, intake.id, payload.get('files') or [])
        intake.file_manifest = manifest
        usable = any(item.get('parse_status') == 'parsed' and item.get('extracted_text') for item in manifest)
        usable = usable or bool(intake.pasted_text)
        intake.status = 'uploaded' if usable else 'analysis_failed'
        await db.commit()
        await db.refresh(intake)
        await self._audit(
            db, user, 'intake_created', 'client_intake', str(intake.id),
            reason=f'{len(manifest)} files, usable={usable}',
        )
        return self._intake_dict(intake)

    async def _save_files(
        self,
        realm_id: uuid.UUID,
        intake_id: uuid.UUID,
        files: List[Dict],
        existing_manifest: List[Dict] = None,
    ) -> List[Dict]:
        existing = list(existing_manifest or [])
        if len(existing) + len(files) > MAX_FILES:
            raise ValueError(f'upload exceeds maximum of {MAX_FILES} files')
        existing_total = sum(int(item.get('size') or 0) for item in existing)
        incoming_total = sum(len(file_payload.get('content') or b'') for file_payload in files)
        if existing_total + incoming_total > MAX_TOTAL_BYTES:
            raise ValueError('upload exceeds cumulative size limit')
        root = self._upload_root(str(realm_id), str(intake_id))
        root.mkdir(parents=True, exist_ok=True)
        manifest = []
        for file_payload in files:
            filename = (file_payload.get('filename') or '').strip()
            content = file_payload.get('content') or b''
            ext = Path(filename).suffix.lower()
            entry = {
                'file_id': uuid.uuid4().hex,
                'file_name': Path(filename).name or 'unnamed',
                'ext': ext,
                'content_type': file_payload.get('content_type') or '',
                'size': len(content),
                'sha256': hashlib.sha256(content).hexdigest(),
                'parse_status': 'parsed',
                'parse_error': None,
                'extracted_text': '',
            }
            if ext not in ALLOWED_EXTENSIONS:
                entry['parse_status'] = 'rejected'
                entry['parse_error'] = 'unsupported_type'
            elif len(content) > MAX_FILE_BYTES:
                entry['parse_status'] = 'rejected'
                entry['parse_error'] = 'file_too_large'
            else:
                safety_error = self._safety_error(content, ext)
                if safety_error:
                    entry['parse_status'] = 'rejected'
                    entry['parse_error'] = safety_error
                else:
                    file_id = entry['file_id']
                    file_path = root / f'{file_id}{ext}'
                    file_path.write_bytes(content)
                    text, parse_status, parse_error = self._extract_text(file_path, ext)
                    entry['parse_status'] = parse_status
                    entry['parse_error'] = parse_error
                    entry['extracted_text'] = text
                    entry['snippet'] = self._first_snippet(text)
            manifest.append(entry)
        return manifest

    @staticmethod
    def _upload_root(realm_id: str, intake_id: str) -> Path:
        base = Path(__file__).resolve().parents[3] / 'backend' / 'uploads' / 'intakes'
        return base / realm_id / intake_id

    @staticmethod
    def _safety_error(content: bytes, ext: str) -> Optional[str]:
        if ext == '.pdf' and not content.startswith(b'%PDF-'):
            return 'magic_mismatch'
        if ext in ('.docx', '.xlsx') and not content.startswith(b'PK\x03\x04'):
            return 'magic_mismatch'
        if ext == '.png' and not content.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'magic_mismatch'
        if ext in ('.jpg', '.jpeg') and not content.startswith(b'\xff\xd8\xff'):
            return 'magic_mismatch'
        if ext in ('.txt', '.md', '.csv') and b'\x00' in content[:4096]:
            return 'binary_content_mismatch'
        return None

    @staticmethod
    def _extract_text(path: Path, ext: str):
        try:
            if ext == '.pdf':
                from pypdf import PdfReader
                reader = PdfReader(str(path))
                text = '\n'.join((page.extract_text() or '') for page in reader.pages)
            elif ext == '.docx':
                from docx import Document
                doc = Document(str(path))
                parts = [p.text for p in doc.paragraphs]
                for table in doc.tables:
                    for row in table.rows:
                        parts.append(' | '.join(cell.text for cell in row.cells))
                text = '\n'.join(parts)
            elif ext == '.xlsx':
                from openpyxl import load_workbook
                wb = load_workbook(str(path), read_only=True, data_only=True)
                rows = []
                for ws in wb.worksheets:
                    rows.append(f'[sheet: {ws.title}]')
                    for row in ws.iter_rows(values_only=True):
                        rows.append(' | '.join('' if v is None else str(v) for v in row))
                text = '\n'.join(rows)
            elif ext == '.csv':
                raw = path.read_text(encoding='utf-8', errors='replace')
                try:
                    parsed = list(csv.reader(io.StringIO(raw)))
                    text = '\n'.join(' | '.join(row) for row in parsed)
                except Exception:
                    text = raw
            elif ext in ('.txt', '.md'):
                text = path.read_text(encoding='utf-8', errors='replace')
            else:
                return '', 'stored_without_ocr', 'image stored; OCR not configured'
            return text[:MAX_EXTRACTED_CHARS], 'parsed', None
        except Exception as exc:
            return '', 'parse_failed', str(exc)[:300]

    @staticmethod
    def _first_snippet(text: str) -> str:
        for line in (text or '').splitlines():
            line = line.strip()
            if line:
                return line[:160]
        return ''

    async def analyze_intake(self, db, user, intake_id) -> Dict:
        intake = await self._require_intake(db, intake_id)
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        combined = self._combined_text(intake)
        if not combined.strip():
            intake.status = 'analysis_failed'
            await db.commit()
            await self._audit(db, user, 'intake_analysis_failed', 'client_intake', str(intake.id), reason='no usable source text')
            return self._intake_dict(intake)
        analysis = self._build_analysis(combined, intake)
        row = IntakeAnalysis(
            intake_id=intake.id,
            realm_id=intake.realm_id,
            version=1,
            status='draft',
            analysis_json=analysis,
            summary=analysis.get('summary'),
            suggested_next_steps=analysis.get('suggested_next_steps'),
            analysis_mode='local_heuristic',
            model_name='geo-intake-local-v1',
            created_by=user.id,
        )
        db.add(row)
        intake.status = 'needs_confirmation'
        await db.commit()
        await db.refresh(row)
        await db.refresh(intake)
        await self._audit(
            db, user, 'intake_analysis_created', 'intake_analysis', str(row.id),
            reason='local transparent analysis, no facts invented',
        )
        return self._intake_dict(intake)

    @staticmethod
    def _combined_text(intake: ClientIntake) -> str:
        parts = []
        for item in intake.file_manifest or []:
            text = item.get('extracted_text') or ''
            if text:
                file_name = item.get('file_name')
                parts.append(f'[文件: {file_name}]\n{text}')
        if intake.pasted_text:
            parts.append(f'[粘贴文字]\n{intake.pasted_text}')
        if intake.supplemental_notes:
            parts.append(f'[补充说明]\n{intake.supplemental_notes}')
        return '\n\n'.join(parts)

    def _build_analysis(self, text: str, intake: ClientIntake) -> Dict:
        fields = []
        for key, label, hints in FIELD_DEFS:
            fields.append(self._extract_field(key, label, hints, text))
        unknown = [f for f in fields if f['status'] == 'unknown']
        known = [f for f in fields if f['status'] in ('observed', 'inferred')]
        summary = f'已从资料提取 {len(known)} 项，{len(unknown)} 项待补充；AI 未补造任何事实。'
        next_steps = []
        if unknown:
            next_steps.append('补齐待补充项后重新分析')
        next_steps.append('确认客户档案')
        next_steps.append('根据确认结果建立执行项目')
        next_steps.append('生成 AI 执行计划并开始第一步')
        return {
            'fields': fields,
            'summary': summary,
            'suggested_next_steps': next_steps,
            'generated_at': datetime.now(timezone.utc).isoformat(),
        }

    def _extract_field(self, key: str, label: str, hints: List[str], text: str) -> Dict:
        for hint in hints:
            pattern = re.compile(r'(?:^|\n)\s*' + re.escape(hint) + r'\s*[:：]\s*([^\n]{1,200})', re.IGNORECASE)
            match = pattern.search(text)
            if match:
                value = match.group(1).strip()
                return {
                    'key': key,
                    'label': label,
                    'value': value,
                    'status': 'observed',
                    'confidence': 0.9,
                    'source_file': self._source_label(text, match.start()),
                    'source_snippet': match.group(0).strip()[:200],
                    'notes': '从资料中直接提取',
                }
        heuristic = self._heuristic_value(key, text)
        if heuristic:
            value, snippet = heuristic
            return {
                'key': key,
                'label': label,
                'value': value,
                'status': 'inferred',
                'confidence': 0.6,
                'source_file': self._source_label(text, text.find(snippet)),
                'source_snippet': snippet[:200],
                'notes': 'AI 依据资料上下文推断，待域主确认',
            }
        return {
            'key': key,
            'label': label,
            'value': '待补充',
            'status': 'unknown',
            'confidence': 0.0,
            'source_file': None,
            'source_snippet': None,
            'notes': '资料中未发现，不补造',
        }

    def _heuristic_value(self, key: str, text: str):
        if key == 'enterprise_entity':
            match = re.search(r'([\u4e00-\u9fa5A-Za-z0-9]{2,40}(?:有限公司|有限责任公司|股份有限公司))', text)
            if match:
                return match.group(1), match.group(0)
        if key == 'service_region':
            for city in CITY_NAMES:
                if city in text:
                    return city, city
        if key == 'business_stage':
            if '从零开始' in text or '新公司' in text:
                return '从零开始', '从零开始' if '从零开始' in text else '新公司'
        if key == 'client_problem':
            if '从零开始' in text or '无渠道' in text or '没有渠道' in text:
                return '从零开始，需要建立 GEO 认知、渠道与转化路径', ('从零开始' if '从零开始' in text else ('无渠道' if '无渠道' in text else '没有渠道'))
        if key == 'conversion_goals':
            if '转化' in text:
                match = re.search(r'[^\n]{0,20}转化目标[^\n]{0,80}', text)
                if match:
                    return match.group(0).strip(), match.group(0)
        return None

    @staticmethod
    def _source_label(text: str, position: int) -> str:
        if position < 0:
            return None
        before = text[:position]
        file_markers = list(re.finditer(r'\[文件: ([^\]]+)\]', before))
        if file_markers:
            return file_markers[-1].group(1)
        return '粘贴文字'

    async def confirm_intake(self, db, user, intake_id, edits: Dict) -> Dict:
        intake = await self._require_intake(db, intake_id)
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        latest = await self._latest_analysis(db, intake.id)
        if not latest:
            raise ValueError('请先完成 AI 分析再确认')
        fields = list((latest.analysis_json or {}).get('fields') or [])
        for field in fields:
            key = field.get('key')
            if key and key in edits:
                value = str(edits[key]).strip()
                field['value'] = value or '待补充'
                field['status'] = 'observed' if value else 'unknown'
                field['confidence'] = 1.0 if value else 0.0
                field['notes'] = '域主确认修改'
        analysis_json = dict(latest.analysis_json or {})
        analysis_json['fields'] = fields
        new_row = IntakeAnalysis(
            intake_id=intake.id,
            realm_id=intake.realm_id,
            version=(latest.version or 1) + 1,
            status='confirmed',
            analysis_json=analysis_json,
            summary=analysis_json.get('summary') or latest.summary,
            suggested_next_steps=analysis_json.get('suggested_next_steps') or latest.suggested_next_steps,
            analysis_mode=latest.analysis_mode,
            model_name=latest.model_name,
            created_by=user.id,
            confirmed_by=user.id,
            confirmed_at=datetime.now(timezone.utc),
        )
        db.add(new_row)
        intake.status = 'owner_confirmed'
        intake.confirmed_by = user.id
        intake.confirmed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(new_row)
        await self._write_confirmed_evidence(db, user, intake, fields)
        await self._audit(
            db, user, 'intake_confirmed', 'client_intake', str(intake.id),
            reason='owner confirmed profile for operations; not verified',
        )
        return self._intake_dict(intake)

    async def _write_confirmed_evidence(self, db, user, intake: ClientIntake, fields: List[Dict]):
        if not intake.realm_entity_id:
            return
        source_url = f'urn:geo-intake:{intake.intake_code}'
        existing = (await db.execute(
            select(Evidence).where(Evidence.source_url == source_url).limit(1)
        )).scalars().first()
        if existing:
            return
        known = [f for f in fields if f.get('status') == 'observed' and f.get('value') and f.get('value') != '待补充']
        claim = '；'.join(str(f.get('label')) + '：' + str(f.get('value')) for f in known) or '域主确认客户档案'
        await self.realm_service.create_evidence(db, user, str(intake.realm_entity_id), {
            'claim': claim,
            'source_url': source_url,
            'source_name': '域主确认客户档案',
            'source_type': 'intake_owner_confirmed',
            'truth_status': 'observed',
            'excerpt': claim[:500],
        })

    @staticmethod
    def _flow_status(intake: ClientIntake) -> str:
        meta = intake.metadata_json or {}
        if meta.get('flow_status'):
            return meta['flow_status']
        return {
            'uploaded': 'awaiting_review',
            'needs_confirmation': 'awaiting_review',
            'owner_confirmed': 'profile_confirmed',
            'needs_changes': 'needs_supplement',
            'analysis_failed': 'awaiting_review',
        }.get(intake.status, 'awaiting_review')

    @staticmethod
    def _assert_transition(current: str, allowed: set, action: str):
        if current not in allowed:
            raise IntakeStateTransitionError(
                f"invalid_state_transition: {current} -> {action}"
            )

    async def start_review(self, db, user, intake_id) -> Dict:
        intake = await self._require_intake(db, intake_id, lock=True)
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        self._assert_transition(
            self._flow_status(intake), {'awaiting_review', 'needs_supplement'}, 'under_review'
        )
        intake.metadata_json = {
            **(intake.metadata_json or {}),
            'flow_status': 'under_review',
        }
        await db.commit()
        await db.refresh(intake)
        await self._audit(db, user, 'customer_review_started', 'client_intake', str(intake.id))
        return self._intake_dict(intake)

    async def update_profile(
        self, db, user, intake_id, edits: Dict, expected_version: int = None
    ) -> Dict:
        intake = await self._require_intake(db, intake_id)
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        intake = await self._require_intake(db, intake_id, lock=True)
        self._assert_transition(
            self._flow_status(intake), {'under_review', 'needs_supplement'}, 'profile_update'
        )
        latest = await self._latest_analysis(db, intake.id)
        if not latest:
            raise ValueError('请先完成本地结构化提取')
        if expected_version is not None and (latest.version or 1) != expected_version:
            raise ValueError('档案版本已变化，请刷新后重试')
        fields = list((latest.analysis_json or {}).get('fields') or [])
        changed = []
        for field in fields:
            key = field.get('key')
            if key and key in edits:
                value = str(edits[key]).strip()
                field['value'] = value or '待补充'
                field['status'] = 'observed' if value else 'unknown'
                field['confidence'] = 1.0 if value else 0.0
                field['notes'] = '域主修改'
                changed.append(key)
        if not changed:
            raise ValueError('未发现可修改字段')
        version = (latest.version or 1) + 1
        row = IntakeAnalysis(
            intake_id=intake.id,
            realm_id=intake.realm_id,
            version=version,
            status='profile_draft',
            analysis_json={**(latest.analysis_json or {}), 'fields': fields},
            summary=latest.summary,
            suggested_next_steps=latest.suggested_next_steps,
            analysis_mode='owner_edit',
            model_name=latest.model_name,
            created_by=user.id,
            metadata_json={
                'profile_version': version,
                'changed_fields': changed,
                'changed_by': str(user.id),
                'changed_at': datetime.now(timezone.utc).isoformat(),
            },
        )
        db.add(row)
        intake.metadata_json = {
            **(intake.metadata_json or {}),
            'flow_status': 'under_review',
            'profile_version': version,
        }
        await db.commit()
        await db.refresh(row)
        await self._audit(
            db, user, 'customer_profile_updated', 'client_intake', str(intake.id),
            reason=f'profile version {version}',
            metadata={'version': version, 'changed_fields': changed},
        )
        return self._analysis_dict(row)

    async def confirm_profile(
        self, db, user, intake_id, edits: Dict = None, expected_version: int = None
    ) -> Dict:
        intake = await self._require_intake(db, intake_id, lock=True)
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        self._assert_transition(
            self._flow_status(intake), {'under_review', 'needs_supplement'}, 'profile_confirmed'
        )
        latest = await self._latest_analysis(db, intake.id)
        if not latest:
            raise ValueError('请先完成本地结构化提取')
        if expected_version is not None and (latest.version or 1) != expected_version:
            raise ValueError('档案版本已变化，请刷新后重试')
        fields = list((latest.analysis_json or {}).get('fields') or [])
        changed = []
        if edits:
            for field in fields:
                key = field.get('key')
                if key and key in edits:
                    value = str(edits[key]).strip()
                    field['value'] = value or '待补充'
                    field['status'] = 'observed' if value else 'unknown'
                    field['confidence'] = 1.0 if value else 0.0
                    field['notes'] = '域主确认修改'
                    changed.append(key)
        version = (latest.version or 1) + 1
        row = IntakeAnalysis(
            intake_id=intake.id,
            realm_id=intake.realm_id,
            version=version,
            status='confirmed',
            analysis_json={**(latest.analysis_json or {}), 'fields': fields},
            summary=latest.summary,
            suggested_next_steps=latest.suggested_next_steps,
            analysis_mode=latest.analysis_mode,
            model_name=latest.model_name,
            created_by=user.id,
            confirmed_by=user.id,
            confirmed_at=datetime.now(timezone.utc),
            metadata_json={
                'profile_version': version,
                'confirmed_by': str(user.id),
                'confirmed_at': datetime.now(timezone.utc).isoformat(),
                'changed_fields': changed,
            },
        )
        db.add(row)
        intake.status = 'owner_confirmed'
        intake.confirmed_by = user.id
        intake.confirmed_at = datetime.now(timezone.utc)
        intake.metadata_json = {
            **(intake.metadata_json or {}),
            'flow_status': 'profile_confirmed',
            'profile_version': version,
        }
        await db.commit()
        await db.refresh(row)
        await self._write_confirmed_evidence(db, user, intake, fields)
        await self._audit(
            db, user, 'customer_profile_confirmed', 'client_intake', str(intake.id),
            reason='profile confirmed for operations; not verified',
            metadata={'version': version, 'changed_fields': changed},
        )
        return self._intake_dict(intake)

    async def request_supplement(self, db, user, intake_id, reason: str) -> Dict:
        intake = await self._require_intake(db, intake_id, lock=True)
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        self._assert_transition(
            self._flow_status(intake), {'under_review'}, 'needs_supplement'
        )
        latest = await self._latest_analysis(db, intake.id)
        version = (latest.version or 1) + 1 if latest else 1
        row = IntakeAnalysis(
            intake_id=intake.id,
            realm_id=intake.realm_id,
            version=version,
            status='supplement_requested',
            analysis_json=latest.analysis_json if latest else None,
            summary=latest.summary if latest else None,
            suggested_next_steps=latest.suggested_next_steps if latest else [],
            analysis_mode='owner_supplement',
            created_by=user.id,
            metadata_json={
                'reason': reason,
                'requested_by': str(user.id),
                'requested_at': datetime.now(timezone.utc).isoformat(),
            },
        )
        db.add(row)
        intake.status = 'needs_changes'
        intake.metadata_json = {
            **(intake.metadata_json or {}),
            'flow_status': 'needs_supplement',
        }
        await db.commit()
        await db.refresh(intake)
        await self._audit(
            db, user, 'customer_supplement_requested', 'client_intake', str(intake.id),
            reason='supplement requested',
            metadata={'version': version, 'reason': reason[:200]},
        )
        return self._intake_dict(intake)

    async def generate_positioning(self, db, user, intake_id) -> Dict:
        intake = await self._require_intake(db, intake_id, lock=True)
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        self._assert_transition(
            self._flow_status(intake), {'profile_confirmed'}, 'positioning_draft'
        )
        latest = await self._latest_analysis(db, intake.id)
        if not latest:
            raise ValueError('请先完成本地结构化提取')
        fields = list((latest.analysis_json or {}).get('fields') or [])
        positioning = get_positioning_service().generate(fields)
        version = (latest.version or 1) + 1
        row = IntakeAnalysis(
            intake_id=intake.id,
            realm_id=intake.realm_id,
            version=version,
            status='positioning_draft',
            analysis_json={
                **(latest.analysis_json or {}),
                'positioning': positioning,
            },
            summary='定位草稿已生成',
            suggested_next_steps=['域主审核并确认定位', '确认后显式创建项目'],
            analysis_mode='local_positioning',
            model_name='geo-positioning-local-v1',
            created_by=user.id,
            metadata_json={
                'positioning_status': 'draft',
                'positioning_version': version,
                'rule_version': positioning.get('rule_version'),
                'config_hash': positioning.get('config_hash'),
            },
        )
        db.add(row)
        intake.metadata_json = {
            **(intake.metadata_json or {}),
            'flow_status': 'positioning_draft',
            'positioning_status': 'draft',
            'positioning_version': version,
        }
        await db.commit()
        await db.refresh(row)
        await self._audit(
            db, user, 'positioning_draft_generated', 'client_intake', str(intake.id),
            reason='local deterministic draft; owner must confirm',
            metadata={
                'version': version,
                'rule_version': positioning.get('rule_version'),
                'config_hash': positioning.get('config_hash'),
            },
        )
        return self._analysis_dict(row)

    async def confirm_positioning(
        self, db, user, intake_id, edits: Dict = None, expected_version: int = None
    ) -> Dict:
        intake = await self._require_intake(db, intake_id, lock=True)
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        self._assert_transition(
            self._flow_status(intake), {'positioning_draft'}, 'positioning_confirmed'
        )
        latest = await self._latest_analysis(db, intake.id)
        if not latest or (latest.analysis_json or {}).get('positioning') is None:
            raise ValueError('请先生成定位草稿')
        if expected_version is not None and (latest.version or 1) != expected_version:
            raise ValueError('定位版本已变化，请刷新后重试')
        positioning = dict((latest.analysis_json or {}).get('positioning') or {})
        if edits:
            positioning['owner_edits'] = edits
        version = (latest.version or 1) + 1
        row = IntakeAnalysis(
            intake_id=intake.id,
            realm_id=intake.realm_id,
            version=version,
            status='positioning_confirmed',
            analysis_json={
                **(latest.analysis_json or {}),
                'positioning': positioning,
            },
            summary='定位已由域主确认',
            suggested_next_steps=['基于此定位显式创建项目'],
            analysis_mode='owner_confirmed_positioning',
            model_name=latest.model_name,
            created_by=user.id,
            confirmed_by=user.id,
            confirmed_at=datetime.now(timezone.utc),
            metadata_json={
                'positioning_status': 'confirmed',
                'positioning_version': version,
                'rule_version': positioning.get('rule_version'),
                'config_hash': positioning.get('config_hash'),
                'confirmed_by': str(user.id),
                'confirmed_at': datetime.now(timezone.utc).isoformat(),
            },
        )
        db.add(row)
        intake.metadata_json = {
            **(intake.metadata_json or {}),
            'flow_status': 'positioning_confirmed',
            'positioning_status': 'confirmed',
            'positioning_version': version,
        }
        await db.commit()
        await db.refresh(row)
        await self._audit(
            db, user, 'positioning_confirmed', 'client_intake', str(intake.id),
            reason='owner confirmed positioning; not verified and no reputation change',
            metadata={
                'version': version,
                'rule_version': positioning.get('rule_version'),
                'config_hash': positioning.get('config_hash'),
            },
        )
        return self._analysis_dict(row)

    async def get_workbench(self, db, user, intake_id) -> Dict:
        intake = await self._require_intake(db, intake_id)
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        result = self._intake_dict(intake)
        result['flow_status'] = self._flow_status(intake)
        result['analyses'] = [
            self._analysis_dict(a)
            for a in (await db.execute(
                select(IntakeAnalysis)
                .where(IntakeAnalysis.intake_id == intake.id)
                .order_by(IntakeAnalysis.version.desc())
            )).scalars().all()
        ]
        result['project_id'] = (intake.metadata_json or {}).get('project_id')
        return result

    async def request_changes(self, db, user, intake_id, reason: str) -> Dict:
        intake = await self._require_intake(db, intake_id)
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        intake.status = 'needs_changes'
        await db.commit()
        await db.refresh(intake)
        await self._audit(db, user, 'intake_changes_requested', 'client_intake', str(intake.id), reason=reason or 'owner requested changes')
        return self._intake_dict(intake)

    async def list_intakes(self, db, user, realm_id) -> List[Dict]:
        if not await self._control(db, user, realm_id):
            raise PermissionError('realm owner/editor permission required')
        registry = await self.realm_service.resolve_registry(db, realm_id)
        if not registry:
            raise ValueError('realm not found')
        rows = (await db.execute(
            select(ClientIntake)
            .where(ClientIntake.realm_id == registry.id)
            .order_by(ClientIntake.created_at.desc())
        )).scalars().all()
        result = []
        for intake in rows:
            item = self._intake_dict(intake)
            latest = await self._latest_analysis(db, intake.id)
            item['latest_analysis'] = self._analysis_dict(latest) if latest else None
            result.append(item)
        return result

    async def get_intake(self, db, user, intake_id) -> Dict:
        intake = await self._require_intake(db, intake_id)
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        result = self._intake_dict(intake)
        analyses = (await db.execute(
            select(IntakeAnalysis)
            .where(IntakeAnalysis.intake_id == intake.id)
            .order_by(IntakeAnalysis.version.desc())
        )).scalars().all()
        result['analyses'] = [self._analysis_dict(a) for a in analyses]
        return result

    async def get_file_path(self, db, user, intake_id, file_id) -> Optional[Path]:
        intake = await self._require_intake(db, intake_id)
        if not await self._control(db, user, str(intake.realm_id)):
            raise PermissionError('realm owner/editor permission required')
        for item in intake.file_manifest or []:
            if item.get('file_id') == file_id:
                ext = item.get('ext') or ''
                path = self._upload_root(str(intake.realm_id), str(intake.id)) / f'{file_id}{ext}'
                return path if path.exists() else None
        return None

    # ── V10.6-R1 public secure intake protocol ──

    @staticmethod
    def _external_ai_ready() -> bool:
        return bool(
            os.getenv('OPENAI_API_KEY')
            or os.getenv('ANTHROPIC_API_KEY')
            or os.getenv('GEMINI_API_KEY')
            or os.getenv('DEEPSEEK_API_KEY')
            or os.getenv('DOUBAO_API_KEY')
        )

    async def _resolve_public_token(self, db, token: str, lock: bool = False):
        code = (token or '').strip()
        if not code:
            raise IntakeTokenError('intake token required', 'token_missing', 401)
        stmt = select(RealmDataAuthorization).where(
            RealmDataAuthorization.authorization_code == code
        )
        if lock:
            stmt = stmt.with_for_update()
        auth = (await db.execute(stmt)).scalars().first()
        if not auth:
            raise IntakeTokenError('intake token invalid', 'token_invalid', 401)
        now = datetime.now(timezone.utc)
        if auth.status != 'active':
            raise IntakeTokenError('intake token revoked', 'token_revoked', 403)
        if auth.valid_from:
            valid_from = auth.valid_from
            if valid_from.tzinfo is None:
                valid_from = valid_from.replace(tzinfo=timezone.utc)
            if valid_from > now:
                raise IntakeTokenError('intake token not yet valid', 'token_not_yet_valid', 403)
        if auth.valid_until:
            valid_until = auth.valid_until
            if valid_until.tzinfo is None:
                valid_until = valid_until.replace(tzinfo=timezone.utc)
            if valid_until < now:
                raise IntakeTokenError('intake token expired', 'token_expired', 410)
        if auth.use_scope != PUBLIC_INTAKE_SCOPE or auth.grantee_type != PUBLIC_INTAKE_GRANTEE:
            raise IntakeTokenError('intake token scope mismatch', 'token_scope_mismatch', 403)
        registry = await self.realm_service.resolve_registry(db, str(auth.entity_id))
        if not registry:
            raise IntakeTokenError('realm not found for intake token', 'realm_not_found', 403)
        return auth, registry

    async def _token_intakes(self, db, registry_id, token_id) -> List[ClientIntake]:
        rows = (await db.execute(
            select(ClientIntake).where(ClientIntake.realm_id == registry_id)
        )).scalars().all()
        return [
            row for row in rows
            if str((row.metadata_json or {}).get('submission_token_id')) == str(token_id)
        ]

    async def check_public_rate(self, db, scope: str, token: str, client_ip: str = None):
        limit, window_seconds = INTAKE_RATE_LIMITS.get(scope, INTAKE_RATE_LIMITS['context'])
        await self.rate_limiter.check_ip(
            scope, client_ip or 'local', limit, window_seconds
        )
        auth, _ = await self._resolve_public_token(db, token)
        await self.rate_limiter.check_token(scope, str(auth.id), limit, window_seconds)

    async def _reject_duplicate_submission(self, db, registry, auth, dedup_hash: str):
        rows = await self._token_intakes(db, registry.id, auth.id)
        cutoff = datetime.utcnow() - timedelta(seconds=PUBLIC_DUPLICATE_WINDOW_SECONDS)
        for row in rows:
            at = row.created_at
            if at is None:
                continue
            if getattr(at, 'tzinfo', None):
                at = at.replace(tzinfo=None)
            if at >= cutoff and (row.metadata_json or {}).get('deduplication_hash') == dedup_hash:
                raise IntakeDuplicateError('duplicate submission already received')

    @staticmethod
    def _public_metadata(payload: Dict, auth: RealmDataAuthorization) -> Dict:
        return {
            'submission_token_id': str(auth.id),
            'submitter_scope': 'anonymous_intake',
            'enterprise_name': (payload.get('enterprise_name') or '').strip(),
            'brand_name': (payload.get('brand_name') or '').strip(),
            'product_or_project_name': (payload.get('product_or_project_name') or '').strip(),
            'relationship': (payload.get('relationship') or '').strip(),
            'problem': (payload.get('problem') or '').strip(),
            'website_url': (payload.get('website_url') or '').strip(),
            'consent_data_analysis': bool(payload.get('consent_data_analysis')),
            'consent_use_authorization': bool(payload.get('consent_use_authorization')),
            'server_staging_consent': bool(payload.get('server_staging_consent')),
            'consent_at': payload.get('consent_at') or datetime.now(timezone.utc).isoformat(),
            'policy_version': PUBLIC_POLICY_VERSION,
        }

    @staticmethod
    def _public_audit_metadata(payload: Dict, auth: RealmDataAuthorization) -> Dict:
        return {
            'submission_token_id': str(auth.id),
            'submitter_scope': 'anonymous_intake',
            'consent_data_analysis': bool(payload.get('consent_data_analysis')),
            'consent_use_authorization': bool(payload.get('consent_use_authorization')),
            'server_staging_consent': bool(payload.get('server_staging_consent')),
            'consent_at': payload.get('consent_at') or datetime.now(timezone.utc).isoformat(),
            'policy_version': PUBLIC_POLICY_VERSION,
        }

    @staticmethod
    def _public_form_dict(intake: ClientIntake) -> Dict:
        meta = intake.metadata_json or {}
        return {
            'enterprise_name': meta.get('enterprise_name', ''),
            'brand_name': meta.get('brand_name', ''),
            'product_or_project_name': meta.get('product_or_project_name', ''),
            'relationship': meta.get('relationship', '') or intake.relationship or '',
            'problem': meta.get('problem', ''),
            'website_url': meta.get('website_url', ''),
            'pasted_text': intake.pasted_text or '',
            'supplemental_notes': intake.supplemental_notes or '',
            'consent_data_analysis': bool(meta.get('consent_data_analysis')),
            'consent_use_authorization': bool(meta.get('consent_use_authorization')),
            'server_staging_consent': bool(meta.get('server_staging_consent')),
            'consent_at': meta.get('consent_at'),
            'policy_version': meta.get('policy_version'),
        }

    @staticmethod
    def _public_file_dict(file: Dict) -> Dict:
        return {
            key: file.get(key)
            for key in (
                'file_id', 'file_name', 'ext', 'content_type', 'size',
                'parse_status', 'parse_error', 'snippet',
            )
        }

    @staticmethod
    def _public_analysis_dict(analysis: Optional[IntakeAnalysis]) -> Optional[Dict]:
        if not analysis:
            return None
        fields = []
        for field in (analysis.analysis_json or {}).get('fields') or []:
            fields.append({
                key: field.get(key)
                for key in ('key', 'label', 'value', 'status', 'confidence', 'source_file', 'notes')
            })
        return {
            'id': str(analysis.id),
            'version': analysis.version,
            'status': analysis.status,
            'summary': analysis.summary,
            'suggested_next_steps': analysis.suggested_next_steps or [],
            'analysis_mode': analysis.analysis_mode,
            'model_name': analysis.model_name,
            'confirmed_at': analysis.confirmed_at.isoformat() if analysis.confirmed_at else None,
            'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
            'fields': fields,
        }

    def _public_intake_dict(self, intake: ClientIntake) -> Dict:
        meta = intake.metadata_json or {}
        return {
            'id': str(intake.id),
            'intake_code': intake.intake_code,
            'status': intake.status,
            'relationship': intake.relationship,
            'pasted_text': intake.pasted_text,
            'supplemental_notes': intake.supplemental_notes,
            'file_manifest': [self._public_file_dict(item) for item in (intake.file_manifest or [])],
            'source_truth_status': intake.source_truth_status,
            'confirmed_at': intake.confirmed_at.isoformat() if intake.confirmed_at else None,
            'created_at': intake.created_at.isoformat() if intake.created_at else None,
            'updated_at': intake.updated_at.isoformat() if intake.updated_at else None,
            'form': self._public_form_dict(intake),
            'processing_status': meta.get('processing_status'),
        }

    @staticmethod
    def _public_form_text(payload: Dict) -> str:
        lines = []
        mapping = [
            ('enterprise_name', '企业主体'),
            ('brand_name', '品牌名称'),
            ('product_or_project_name', '核心产品或服务'),
            ('relationship', '关系'),
            ('problem', '客户希望解决的问题'),
            ('website_url', '主要渠道'),
        ]
        for key, label in mapping:
            value = (payload.get(key) or '').strip()
            if value:
                lines.append(f'{label}：{value}')
        pasted = (payload.get('pasted_text') or '').strip()
        if pasted:
            lines.append(pasted)
        return '\n'.join(lines)

    @staticmethod
    def _public_dedup_hash(auth, payload: Dict, files: List[Dict]) -> str:
        names = [
            str(payload.get(key) or '').strip().lower()
            for key in ('enterprise_name', 'brand_name', 'product_or_project_name', 'relationship', 'problem', 'website_url')
        ]
        file_hashes = '|'.join(sorted(str(item.get('sha256') or '') for item in files))
        consent = (
            f"{bool(payload.get('consent_data_analysis'))}|"
            f"{bool(payload.get('consent_use_authorization'))}|"
            f"{bool(payload.get('server_staging_consent'))}"
        )
        raw = f"{auth.id}|{'|'.join(names)}|{file_hashes}|{consent}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    async def get_public_context(self, db, token: str, client_ip: str = None) -> Dict:
        if client_ip:
            await self.check_public_rate(db, 'context', token, client_ip)
        auth, registry = await self._resolve_public_token(db, token)
        rows = await self._token_intakes(db, registry.id, auth.id)
        ordered = sorted(rows, key=lambda row: row.created_at or datetime.min, reverse=True)
        draft = next((row for row in ordered if row.status == 'draft'), None)
        submission = next((row for row in ordered if row.status != 'draft'), None)
        submission_payload = self._public_intake_dict(submission) if submission else None
        if submission_payload:
            latest = await self._latest_analysis(db, submission.id)
            submission_payload['latest_analysis'] = self._public_analysis_dict(latest)
        return {
            'token_status': 'valid',
            'realm': {
                'realm_code': registry.realm_code,
                'realm_type': registry.realm_type,
                'display_name': registry.display_name,
            },
            'allowed_file_types': sorted(ALLOWED_EXTENSIONS),
            'max_files': MAX_FILES,
            'max_file_bytes': MAX_FILE_BYTES,
            'analysis': {
                'external_ai_ready': self._external_ai_ready(),
                'mode': 'local_heuristic',
                'notice': '未配置外部 AI Key 时只运行真实本地结构化提取，不生成模拟 AI 分析。',
            },
            'latest_draft': self._public_intake_dict(draft) if draft else None,
            'latest_submission': submission_payload,
            'audit': {
                'scope': 'anonymous_intake',
                'token_kind': 'public_intake_submission',
            },
        }

    async def save_public_draft(
        self, db, token: str, payload: Dict, files: List[Dict], client_ip: str = None
    ) -> Dict:
        if client_ip:
            await self.check_public_rate(db, 'draft', token, client_ip)
        auth, registry = await self._resolve_public_token(db, token)
        if not payload.get('server_staging_consent'):
            raise ValueError('服务器暂存授权为必填，未授权前不得保存草稿到服务器')
        rows = await self._token_intakes(db, registry.id, auth.id)
        draft = next((row for row in rows if row.status == 'draft'), None)
        metadata = self._public_metadata(payload, auth)
        if draft:
            intake = draft
            intake.relationship = (payload.get('relationship') or '').strip() or None
            intake.pasted_text = (payload.get('pasted_text') or '').strip() or None
            intake.supplemental_notes = (payload.get('supplemental_notes') or '').strip() or None
            intake.metadata_json = metadata
        else:
            intake = ClientIntake(
                intake_code=f'INTK-{uuid.uuid4().hex[:12].upper()}',
                realm_id=registry.id,
                realm_entity_id=registry.entity_id,
                status='draft',
                relationship=metadata['relationship'] or None,
                pasted_text=(payload.get('pasted_text') or '').strip() or None,
                supplemental_notes=(payload.get('supplemental_notes') or '').strip() or None,
                file_manifest=[],
                source_truth_status='observed',
                created_by=None,
                metadata_json=metadata,
            )
            db.add(intake)
            await db.flush()
            await db.refresh(intake)
        if files:
            new_manifest = await self._save_files(
                registry.id, intake.id, files, existing_manifest=intake.file_manifest or []
            )
            intake.file_manifest = list(intake.file_manifest or []) + new_manifest
        await db.commit()
        await db.refresh(intake)
        audit_metadata = self._public_audit_metadata(payload, auth)
        await self.gov.audit(
            db, None, 'public_intake_draft_saved', 'client_intake', str(intake.id),
            actor_label=f'intake_authorization:{str(auth.id)}',
            reason='anonymous secure token draft',
            metadata=audit_metadata,
        )
        return self._public_intake_dict(intake)

    async def submit_public_intake(
        self, db, token: str, payload: Dict, files: List[Dict], client_ip: str = None
    ) -> Dict:
        if client_ip:
            await self.check_public_rate(db, 'submit', token, client_ip)
        auth, registry = await self._resolve_public_token(db, token, lock=True)
        dedup_hash = self._public_dedup_hash(auth, payload, files)
        await self._reject_duplicate_submission(db, registry, auth, dedup_hash)
        rows = await self._token_intakes(db, registry.id, auth.id)
        if any(row.status != 'draft' for row in rows):
            raise IntakeDuplicateError('intake already submitted for this token')

        enterprise_name = (payload.get('enterprise_name') or '').strip()
        brand_name = (payload.get('brand_name') or '').strip()
        product_or_project_name = (payload.get('product_or_project_name') or '').strip()
        relationship = (payload.get('relationship') or '').strip()
        problem = (payload.get('problem') or '').strip()
        website_url = (payload.get('website_url') or '').strip()
        if not (enterprise_name or brand_name or product_or_project_name):
            raise ValueError('请填写企业、品牌、产品或项目名称')
        if not relationship:
            raise ValueError('请填写与项目的关系')
        if not problem:
            raise ValueError('请填写最想解决的问题')
        if website_url:
            validate_url(website_url)
        if not payload.get('consent_data_analysis') or not payload.get('consent_use_authorization'):
            raise ValueError('数据分析和使用授权为必填')
        if not payload.get('server_staging_consent'):
            raise ValueError('服务器暂存授权为必填')

        metadata = self._public_metadata(payload, auth)
        metadata['deduplication_hash'] = dedup_hash
        metadata['processing_status'] = 'processing'
        audit_metadata = self._public_audit_metadata(payload, auth)
        draft = next((row for row in rows if row.status == 'draft'), None)
        if draft:
            intake = draft
        else:
            intake = ClientIntake(
                intake_code=f'INTK-{uuid.uuid4().hex[:12].upper()}',
                realm_id=registry.id,
                realm_entity_id=registry.entity_id,
                status='uploaded',
                relationship=relationship,
                pasted_text=self._public_form_text(payload),
                supplemental_notes=(payload.get('supplemental_notes') or '').strip() or None,
                file_manifest=[],
                source_truth_status='observed',
                created_by=None,
                metadata_json=metadata,
            )
            db.add(intake)
            await db.flush()
            await db.refresh(intake)

        intake.relationship = relationship
        intake.supplemental_notes = (payload.get('supplemental_notes') or '').strip() or None
        intake.pasted_text = self._public_form_text(payload)
        intake.metadata_json = metadata
        if files:
            new_manifest = await self._save_files(
                registry.id, intake.id, files, existing_manifest=intake.file_manifest or []
            )
            intake.file_manifest = list(intake.file_manifest or []) + new_manifest

        combined = self._combined_text(intake)
        if not combined.strip():
            intake.status = 'analysis_failed'
            intake.metadata_json['processing_status'] = 'failed'
            await db.commit()
            await db.refresh(intake)
            await self.gov.audit(
                db, None, 'public_intake_submission_failed', 'client_intake', str(intake.id),
                actor_label=f'intake_authorization:{str(auth.id)}',
                reason='no usable source text',
                metadata=audit_metadata,
            )
            return self._public_intake_dict(intake)

        analysis = self._build_analysis(combined, intake)
        row = IntakeAnalysis(
            intake_id=intake.id,
            realm_id=intake.realm_id,
            version=1,
            status='draft',
            analysis_json=analysis,
            summary=analysis.get('summary'),
            suggested_next_steps=analysis.get('suggested_next_steps'),
            analysis_mode='local_heuristic',
            model_name='geo-intake-local-v1',
            created_by=None,
            metadata_json={
                'processing_status': 'completed',
                'external_ai_used': False,
                'external_ai_ready': self._external_ai_ready(),
            },
        )
        db.add(row)
        intake.status = 'needs_confirmation'
        intake.metadata_json['processing_status'] = 'completed'
        await db.commit()
        await db.refresh(row)
        await db.refresh(intake)
        result = self._public_intake_dict(intake)
        result['latest_analysis'] = self._public_analysis_dict(row)
        await self.gov.audit(
            db, None, 'public_intake_submission_created', 'client_intake', str(intake.id),
            actor_label=f'intake_authorization:{str(auth.id)}',
            reason='public secure token submission; local extraction completed, waiting owner confirmation',
            metadata=audit_metadata,
        )
        return result

    async def _latest_analysis(self, db, intake_id) -> Optional[IntakeAnalysis]:
        return (await db.execute(
            select(IntakeAnalysis)
            .where(IntakeAnalysis.intake_id == intake_id)
            .order_by(IntakeAnalysis.version.desc())
            .limit(1)
        )).scalars().first()

    async def _require_intake(self, db, intake_id, lock: bool = False) -> ClientIntake:
        try:
            intake_uuid = uuid.UUID(str(intake_id))
        except (ValueError, TypeError):
            raise ValueError('intake_id must be a valid UUID')
        if lock:
            rows = (await db.execute(
                select(ClientIntake)
                .where(ClientIntake.id == intake_uuid)
                .with_for_update()
            )).scalars().all()
            intake = rows[0] if rows else None
        else:
            intake = await db.get(ClientIntake, intake_uuid)
        if not intake:
            raise ValueError('intake not found')
        return intake

    def _intake_dict(self, intake: ClientIntake) -> Dict:
        meta = intake.metadata_json or {}
        return {
            'id': str(intake.id),
            'intake_code': intake.intake_code,
            'realm_id': str(intake.realm_id),
            'realm_entity_id': str(intake.realm_entity_id) if intake.realm_entity_id else None,
            'status': intake.status,
            'relationship': intake.relationship,
            'pasted_text': intake.pasted_text,
            'supplemental_notes': intake.supplemental_notes,
            'file_manifest': intake.file_manifest or [],
            'source_truth_status': intake.source_truth_status,
            'created_by': str(intake.created_by) if intake.created_by else None,
            'confirmed_by': str(intake.confirmed_by) if intake.confirmed_by else None,
            'confirmed_at': intake.confirmed_at.isoformat() if intake.confirmed_at else None,
            'created_at': intake.created_at.isoformat() if intake.created_at else None,
            'updated_at': intake.updated_at.isoformat() if intake.updated_at else None,
            'metadata_json': intake.metadata_json or {},
            'flow_status': self._flow_status(intake),
            'profile_version': meta.get('profile_version'),
            'positioning_status': meta.get('positioning_status'),
            'positioning_version': meta.get('positioning_version'),
            'project_id': meta.get('project_id'),
        }

    def _analysis_dict(self, analysis: IntakeAnalysis) -> Dict:
        return {
            'id': str(analysis.id),
            'intake_id': str(analysis.intake_id),
            'realm_id': str(analysis.realm_id),
            'version': analysis.version,
            'status': analysis.status,
            'analysis_json': analysis.analysis_json,
            'summary': analysis.summary,
            'suggested_next_steps': analysis.suggested_next_steps or [],
            'analysis_mode': analysis.analysis_mode,
            'model_name': analysis.model_name,
            'created_by': str(analysis.created_by) if analysis.created_by else None,
            'confirmed_by': str(analysis.confirmed_by) if analysis.confirmed_by else None,
            'confirmed_at': analysis.confirmed_at.isoformat() if analysis.confirmed_at else None,
            'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
            'metadata_json': analysis.metadata_json or {},
        }


def get_intake_service() -> IntakeService:
    return IntakeService()
