export type AlertType =
  | "DUE_DATE_REMINDER"
  | "PRICE_HIKE"
  | "UNUSUAL_EXPENSE"
  | "SUBSCRIPTION_RENEWAL";

export type AlertChannel = "EMAIL" | "TELEGRAM" | "IN_APP";
export type AlertStatus = "PENDING" | "SENT" | "FAILED" | "READ";

export interface Alert {
  id: string;
  user_id: string;
  bill_id?: string | null;
  subscription_id?: string | null;
  alert_type: AlertType;
  title: string;
  message: string;
  channel: AlertChannel;
  status: AlertStatus;
  scheduled_for: string;
  sent_at?: string | null;
  created_at: string;
}
