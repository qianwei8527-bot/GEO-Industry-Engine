'''V10.5 client intake API.'''

from typing import List

from fastapi import APIRouter, Depends, Form, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.intake_service import (
    MAX_FILE_BYTES,
    MAX_FILES,
    IntakeFileTooLargeError,
    IntakeStateTransitionError,
    IntakeTokenError,
    get_intake_service,
)
from app.services.geo_project_service import get_geo_project_service
from app.services.intake_rate_limiter import RateLimitBackendUnavailable

router = APIRouter(prefix='/api/v1/intakes', tags=['intakes'])


def _handle(e: Exception) -> HTTPException:
    if isinstance(e, IntakeTokenError):
        return HTTPException(e.http_status, f"{e.code}: {e}")
    if isinstance(e, RateLimitBackendUnavailable):
        return HTTPException(503, str(e))
    if isinstance(e, IntakeFileTooLargeError):
        return HTTPException(413, str(e))
    if isinstance(e, PermissionError):
        return HTTPException(404, "resource not found")
    if isinstance(e, IntakeStateTransitionError):
        return HTTPException(409, str(e))
    if isinstance(e, ValueError):
        if str(e) in (
            "intake not found",
            "intake_id must be a valid UUID",
            "project not found",
            "project_id must be a valid UUID",
        ):
            return HTTPException(404, "resource not found")
        return HTTPException(400, str(e))
    return HTTPException(500, str(e))


def _bool_form(value: str) -> bool:
    return str(value or '').strip().lower() in ('1', 'true', 'yes', 'on')


async def _read_upload_limited(file: UploadFile, max_bytes: int) -> bytes:
    chunks = []
    total = 0
    while True:
        chunk = await file.read(65536)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise IntakeFileTooLargeError(f'file exceeds maximum size of {max_bytes} bytes')
        chunks.append(chunk)
    return b''.join(chunks)


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else 'local'


@router.post('')
async def create_intake(
    realm_id: str = Form(...),
    relationship: str = Form(''),
    pasted_text: str = Form(''),
    supplemental_notes: str = Form(''),
    files: List[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if len(files) > MAX_FILES:
            raise ValueError(f'too many files, max {MAX_FILES}')
        payload_files = []
        for file in files:
            content = await _read_upload_limited(file, MAX_FILE_BYTES)
            payload_files.append({
                'filename': file.filename or '',
                'content_type': file.content_type or '',
                'content': content,
            })
        return await get_intake_service().create_intake(
            db, current_user, realm_id, {
                'relationship': relationship,
                'pasted_text': pasted_text,
                'supplemental_notes': supplemental_notes,
                'files': payload_files,
            },
        )
    except Exception as e:
        raise _handle(e)


@router.get('/public/{secure_token}')
async def get_public_intake_context(
    secure_token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await get_intake_service().get_public_context(
            db, secure_token, client_ip=_client_ip(request)
        )
    except Exception as e:
        raise _handle(e)


@router.post('/public/{secure_token}/draft')
async def save_public_intake_draft(
    secure_token: str,
    request: Request,
    enterprise_name: str = Form(''),
    brand_name: str = Form(''),
    product_or_project_name: str = Form(''),
    relationship: str = Form(''),
    problem: str = Form(''),
    website_url: str = Form(''),
    pasted_text: str = Form(''),
    supplemental_notes: str = Form(''),
    consent_data_analysis: str = Form(''),
    consent_use_authorization: str = Form(''),
    server_staging_consent: str = Form(''),
    files: List[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
):
    try:
        if len(files) > MAX_FILES:
            raise ValueError(f'too many files, max {MAX_FILES}')
        payload_files = []
        for file in files:
            content = await _read_upload_limited(file, MAX_FILE_BYTES)
            payload_files.append({
                'filename': file.filename or '',
                'content_type': file.content_type or '',
                'content': content,
            })
        return await get_intake_service().save_public_draft(
            db, secure_token, {
                'enterprise_name': enterprise_name,
                'brand_name': brand_name,
                'product_or_project_name': product_or_project_name,
                'relationship': relationship,
                'problem': problem,
                'website_url': website_url,
                'pasted_text': pasted_text,
                'supplemental_notes': supplemental_notes,
                'consent_data_analysis': _bool_form(consent_data_analysis),
                'consent_use_authorization': _bool_form(consent_use_authorization),
                'server_staging_consent': _bool_form(server_staging_consent),
                'files': payload_files,
            },
            payload_files,
            client_ip=_client_ip(request),
        )
    except Exception as e:
        raise _handle(e)


@router.post('/public/{secure_token}/submissions')
async def submit_public_intake(
    secure_token: str,
    request: Request,
    enterprise_name: str = Form(''),
    brand_name: str = Form(''),
    product_or_project_name: str = Form(''),
    relationship: str = Form(''),
    problem: str = Form(''),
    website_url: str = Form(''),
    pasted_text: str = Form(''),
    supplemental_notes: str = Form(''),
    consent_data_analysis: str = Form(''),
    consent_use_authorization: str = Form(''),
    server_staging_consent: str = Form(''),
    files: List[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
):
    try:
        if len(files) > MAX_FILES:
            raise ValueError(f'too many files, max {MAX_FILES}')
        payload_files = []
        for file in files:
            content = await _read_upload_limited(file, MAX_FILE_BYTES)
            payload_files.append({
                'filename': file.filename or '',
                'content_type': file.content_type or '',
                'content': content,
            })
        return await get_intake_service().submit_public_intake(
            db, secure_token, {
                'enterprise_name': enterprise_name,
                'brand_name': brand_name,
                'product_or_project_name': product_or_project_name,
                'relationship': relationship,
                'problem': problem,
                'website_url': website_url,
                'pasted_text': pasted_text,
                'supplemental_notes': supplemental_notes,
                'consent_data_analysis': _bool_form(consent_data_analysis),
                'consent_use_authorization': _bool_form(consent_use_authorization),
                'server_staging_consent': _bool_form(server_staging_consent),
                'files': payload_files,
            },
            payload_files,
            client_ip=_client_ip(request),
        )
    except Exception as e:
        raise _handle(e)


@router.get('')
async def list_intakes(realm_id: str, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    try:
        return {'intakes': await get_intake_service().list_intakes(db, current_user, realm_id)}
    except Exception as e:
        raise _handle(e)


@router.get('/{intake_id}')
async def get_intake(intake_id: str, db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    try:
        return await get_intake_service().get_intake(db, current_user, intake_id)
    except Exception as e:
        raise _handle(e)


@router.get('/{intake_id}/workbench')
async def get_intake_workbench(intake_id: str, db: AsyncSession = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    try:
        return await get_intake_service().get_workbench(db, current_user, intake_id)
    except Exception as e:
        raise _handle(e)


@router.post('/{intake_id}/review/start')
async def start_intake_review(intake_id: str, db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    try:
        return await get_intake_service().start_review(db, current_user, intake_id)
    except Exception as e:
        raise _handle(e)


@router.post('/{intake_id}/profile')
async def update_intake_profile(intake_id: str, data: dict, db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    try:
        return await get_intake_service().update_profile(
            db, current_user, intake_id,
            data.get('edits') or {},
            expected_version=data.get('expected_version'),
        )
    except Exception as e:
        raise _handle(e)


@router.post('/{intake_id}/profile/confirm')
async def confirm_intake_profile(intake_id: str, data: dict, db: AsyncSession = Depends(get_db),
                                 current_user: User = Depends(get_current_user)):
    try:
        return await get_intake_service().confirm_profile(
            db, current_user, intake_id,
            data.get('edits') or {},
            expected_version=data.get('expected_version'),
        )
    except Exception as e:
        raise _handle(e)


@router.post('/{intake_id}/supplement')
async def request_intake_supplement(intake_id: str, data: dict, db: AsyncSession = Depends(get_db),
                                    current_user: User = Depends(get_current_user)):
    try:
        return await get_intake_service().request_supplement(
            db, current_user, intake_id, data.get('reason') or ''
        )
    except Exception as e:
        raise _handle(e)


@router.post('/{intake_id}/positioning/generate')
async def generate_intake_positioning(intake_id: str, db: AsyncSession = Depends(get_db),
                                      current_user: User = Depends(get_current_user)):
    try:
        return await get_intake_service().generate_positioning(db, current_user, intake_id)
    except Exception as e:
        raise _handle(e)


@router.post('/{intake_id}/positioning/confirm')
async def confirm_intake_positioning(intake_id: str, data: dict, db: AsyncSession = Depends(get_db),
                                     current_user: User = Depends(get_current_user)):
    try:
        return await get_intake_service().confirm_positioning(
            db, current_user, intake_id,
            data.get('edits') or {},
            expected_version=data.get('expected_version'),
        )
    except Exception as e:
        raise _handle(e)


@router.post('/{intake_id}/project')
async def create_intake_project(intake_id: str, data: dict, db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    try:
        return await get_geo_project_service().create_project_from_positioning(
            db, current_user, intake_id,
            confirmed=bool(data.get('confirmed', False)),
            expected_position_version=data.get('expected_position_version'),
        )
    except Exception as e:
        raise _handle(e)


@router.post('/{intake_id}/analyze')
async def analyze_intake(intake_id: str, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    try:
        return await get_intake_service().analyze_intake(db, current_user, intake_id)
    except Exception as e:
        raise _handle(e)


@router.post('/{intake_id}/confirm')
async def confirm_intake(intake_id: str, data: dict, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    try:
        return await get_intake_service().confirm_intake(
            db, current_user, intake_id, data.get('edits') or {},
        )
    except Exception as e:
        raise _handle(e)


@router.post('/{intake_id}/request-changes')
async def request_changes(intake_id: str, data: dict, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    try:
        return await get_intake_service().request_changes(
            db, current_user, intake_id, data.get('reason') or '',
        )
    except Exception as e:
        raise _handle(e)


@router.get('/{intake_id}/files/{file_id}')
async def download_file(intake_id: str, file_id: str, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    try:
        path = await get_intake_service().get_file_path(db, current_user, intake_id, file_id)
    except Exception as e:
        raise _handle(e)
    if not path:
        raise HTTPException(404, 'file not found')
    return FileResponse(str(path), filename=path.name)
