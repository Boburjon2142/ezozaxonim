export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type UserProfile = {
  id: string;
  email: string;
  full_name: string;
  timezone: string;
  preferred_work_hours: string;
  goals: string;
  push_enabled: boolean;
  is_premium: boolean;
};

export type PlanItem = {
  id?: string;
  title: string;
  status: "todo" | "done" | "partial" | "blocked";
  estimate_minutes: number;
  tags: string;
};

export type Plan = {
  id?: string;
  date: string;
  reflection: string;
  items: PlanItem[];
};

export type TimeSession = {
  id: string;
  started_at: string;
  ended_at: string | null;
  duration_minutes: number;
  tags: string;
  plan_item_id: string | null;
};

export type CheckIn = {
  id: string;
  date: string;
  energy: number;
  stress: number;
  mood: number;
  sleep: number;
  note: string;
};
