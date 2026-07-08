/**
 * Conversation-first structure — launch path turn order.
 * Copy lives in screen components; this file defines **turn roles** only.
 */

export type ConversationTurnRole =
  | "practitioner_speech"
  | "user_response"
  | "deepen_optional"
  | "session_close";

export type LaunchConversationTurn = {
  id: string;
  screen: string;
  role: ConversationTurnRole;
  /** Learning / analytics hook */
  eventSurface?: string;
};

/** Value-first onboarding → First Today → evening → save */
export const LAUNCH_CONVERSATION_SCRIPT: LaunchConversationTurn[] = [
  { id: "welcome_name", screen: "/onboarding/welcome", role: "practitioner_speech", eventSurface: "onboarding_welcome" },
  { id: "welcome_name_reply", screen: "/onboarding/welcome", role: "user_response" },
  { id: "birth_date", screen: "/onboarding/birth", role: "practitioner_speech", eventSurface: "onboarding_birth" },
  { id: "birth_date_reply", screen: "/onboarding/birth", role: "user_response" },
  { id: "preview_recognition", screen: "/onboarding/preview", role: "practitioner_speech", eventSurface: "onboarding_preview" },
  { id: "preview_deepen", screen: "/onboarding/preview", role: "deepen_optional" },
  { id: "preview_next", screen: "/onboarding/preview", role: "user_response" },
  { id: "refine_optional", screen: "/onboarding/refine", role: "deepen_optional" },
  { id: "today_opening", screen: "/today?first=1", role: "practitioner_speech", eventSurface: "first_today_open" },
  { id: "today_checkin", screen: "/today?first=1", role: "user_response" },
  { id: "today_focus", screen: "/today?first=1", role: "practitioner_speech" },
  { id: "today_ritual", screen: "/today?first=1", role: "user_response" },
  { id: "today_close", screen: "/today?first=1", role: "session_close", eventSurface: "first_today_evening" },
  { id: "save_invite", screen: "/onboarding/save", role: "practitioner_speech", eventSurface: "onboarding_save" },
  { id: "save_email", screen: "/onboarding/save", role: "user_response" },
];
