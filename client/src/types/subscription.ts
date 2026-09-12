import { Category } from "./bill";

export type BillingFrequency = "MONTHLY" | "YEARLY" | "QUARTERLY" | "WEEKLY";
export type SubscriptionStatus = "ACTIVE" | "PAUSED" | "CANCELLED";

export interface Subscription {
  id: string;
  user_id: string;
  category_id?: string | null;
  service_name: string;
  plan_name?: string | null;
  cost: number;
  currency: string;
  billing_frequency: BillingFrequency;
  next_renewal_date: string; // YYYY-MM-DD
  status: SubscriptionStatus;
  trial_end_date?: string | null;
  cancellation_url?: string | null;
  created_at: string;
  updated_at: string;
  category?: Category | null;
}

export interface CreateSubscriptionPayload {
  service_name: string;
  plan_name?: string;
  cost: number;
  currency?: string;
  billing_frequency?: BillingFrequency;
  next_renewal_date: string;
  category_id?: string;
  trial_end_date?: string;
  cancellation_url?: string;
}
