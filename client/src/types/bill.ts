export type BillingCycle = "MONTHLY" | "QUARTERLY" | "ANNUALLY" | "ONE_TIME";
export type BillStatus = "PENDING" | "PAID" | "OVERDUE";

export interface Category {
  id: string;
  name: string;
  icon: string;
  color: string;
  is_default: boolean;
}

export interface Bill {
  id: string;
  user_id: string;
  category_id?: string | null;
  biller_name: string;
  amount: number;
  currency: string;
  due_date: string; // YYYY-MM-DD
  billing_cycle: BillingCycle;
  status: BillStatus;
  is_recurring: boolean;
  auto_pay: boolean;
  notes?: string | null;
  receipt_url?: string | null;
  created_at: string;
  updated_at: string;
  category?: Category | null;
}

export interface CreateBillPayload {
  biller_name: string;
  amount: number;
  currency?: string;
  due_date: string;
  billing_cycle?: BillingCycle;
  category_id?: string;
  is_recurring?: boolean;
  auto_pay?: boolean;
  notes?: string;
}
