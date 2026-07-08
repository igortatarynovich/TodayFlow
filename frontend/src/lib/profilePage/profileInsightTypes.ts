import type { ProfileInsightLayer } from "./profileInsightBudget";

export type ProfileInsightSourceKind = "reference" | "llm" | "template" | "computed";

export type ProfileTaxonomyInsightSlot = {
  layer: ProfileInsightLayer;
  categoryId: string;
  text: string;
  sourceKind: ProfileInsightSourceKind;
  sourceKey: string;
};

export type ProfileInsightAuditStatus = "unique" | "duplicate" | "weak" | "missing";

export type ProfileInsightAuditRow = {
  layer: ProfileInsightLayer;
  categoryId: string;
  text: string | null;
  source: string | null;
  status: ProfileInsightAuditStatus;
  duplicateOf?: string;
};

export type ProfileInsightCoverageReport = {
  profileLabel: string;
  rows: ProfileInsightAuditRow[];
  gaps: Array<{ layer: ProfileInsightLayer; categoryId: string }>;
  summary: {
    filled: number;
    missing: number;
    duplicate: number;
    weak: number;
    unique: number;
  };
};

export type ProfileLayerInsightPayload = {
  layer: ProfileInsightLayer;
  slots: ProfileTaxonomyInsightSlot[];
};

export type ProfileV0TaxonomyPayload = {
  layers: ProfileLayerInsightPayload[];
  allSlots: ProfileTaxonomyInsightSlot[];
};
