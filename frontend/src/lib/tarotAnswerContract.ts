export type TarotUnresolvedCard = {
  card_id: number;
  position_id?: string;
  reason?: string;
};

export type TarotChoiceStory = {
  option_a_summary?: string;
  option_a_gain?: string;
  option_a_risk?: string;
  option_b_summary?: string;
  option_b_gain?: string;
  option_b_risk?: string;
  hidden_tension?: string;
  recommended_next_step?: string;
  confidence_note?: string;
};

export type TarotAnswerV1 = {
  contract_version: string;
  question_text?: string;
  concern_domain?: string;
  spread_id?: string;
  main_answer: string;
  story_narrative?: string;
  new_angle?: string;
  hidden_factor?: string;
  risk?: string;
  attention?: string;
  next_step?: string;
  today_suggestion?: string;
  insights?: {
    holding?: string;
    shifting?: string;
    attention?: string;
  };
  follow_up_prompt?: string;
  follow_up_chips?: Array<{ id: string; label: string }>;
  generation_id?: string;
  synthesis_mode?: string;
  synthesis_status?: "ok" | "unresolved_cards" | string;
  unresolved_cards?: TarotUnresolvedCard[];
  choice_story?: TarotChoiceStory | null;
  profile_lens?: string | null;
  profile_lens_applied?: boolean;
};
