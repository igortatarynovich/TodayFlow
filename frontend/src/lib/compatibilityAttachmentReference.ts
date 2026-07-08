/** Attachment reference slice from compatibility API (CD lens, not diagnosis). */

export type AttachmentStyleHint = {
  code: string;
  label: string;
  summary: string;
  score?: number;
  evidence_blocks?: string[];
  confirmation_required?: boolean;
  knowledge_type?: string;
};

export type AttachmentReference = {
  contract_version?: string;
  deep_block_order?: string[];
  attachment_style_hints?: AttachmentStyleHint[];
  trigger_blocks?: string[];
  reference_status?: string;
};

export function primaryAttachmentHint(
  ref: AttachmentReference | null | undefined,
): AttachmentStyleHint | null {
  const hints = ref?.attachment_style_hints;
  if (!hints?.length) return null;
  return hints[0] ?? null;
}

export function attachmentLensKnowledgeId(code: string): string {
  return `inf-attachment-lens-${code.trim().toLowerCase().replace(/\s+/g, "_")}`;
}
