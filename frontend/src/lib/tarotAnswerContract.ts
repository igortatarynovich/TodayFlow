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
};
