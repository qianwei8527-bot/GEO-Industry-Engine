import type { PublicIntakeContext, PublicIntakeFormValues } from "./types";

export const EMPTY_PUBLIC_INTAKE_FORM: PublicIntakeFormValues = {
  enterpriseName: "",
  brandName: "",
  productOrProjectName: "",
  relationship: "",
  problem: "",
  websiteUrl: "",
  pastedText: "",
  supplementalNotes: "",
  consentDataAnalysis: false,
  consentUseAuthorization: false,
  serverStagingConsent: false,
};

export function validatePublicIntake(
  form: PublicIntakeFormValues,
  context: Pick<PublicIntakeContext, "max_files" | "max_file_bytes" | "allowed_file_types">,
  files: File[],
): Record<string, string> {
  const errors: Record<string, string> = {};
  if (!form.enterpriseName.trim() && !form.brandName.trim() && !form.productOrProjectName.trim()) {
    errors.names = "请填写企业、品牌、产品或项目名称中的至少一项";
  }
  if (!form.relationship.trim()) errors.relationship = "请填写与项目的关系";
  if (!form.problem.trim()) errors.problem = "请填写最想解决的问题";
  if (form.websiteUrl.trim() && !/^https?:\/\/[^\s/$.?#].[^\s]*$/i.test(form.websiteUrl.trim())) {
    errors.websiteUrl = "请输入有效的 http/https 链接";
  }
  if (!form.consentDataAnalysis || !form.consentUseAuthorization || !form.serverStagingConsent) {
    errors.consent = "必须同意数据分析、使用授权和服务器暂存";
  }
  if (files.length > context.max_files) {
    errors.files = `最多上传 ${context.max_files} 个文件`;
  }
  for (const file of files) {
    const ext = "." + (file.name.split(".").pop() || "").toLowerCase();
    if (!context.allowed_file_types.includes(ext)) {
      errors.files = `不支持文件类型：${file.name}`;
      break;
    }
    if (file.size > context.max_file_bytes) {
      errors.files = `文件超过大小限制：${file.name}`;
      break;
    }
  }
  return errors;
}

export function formatFileSize(bytes: number): string {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** index;
  return `${value >= 10 || index === 0 ? value.toFixed(0) : value.toFixed(1)} ${units[index]}`;
}
