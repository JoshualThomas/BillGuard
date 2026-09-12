export interface CategorySpend {
  category_name: string;
  icon: string;
  color: string;
  total_amount: number;
  percentage: number;
}

export interface DashboardSummary {
  total_monthly_recurring: number;
  pending_bills_count: int;
  pending_bills_total: number;
  active_subscriptions_count: number;
  next_critical_due_date?: string | null;
  category_breakdown: CategorySpend[];
}

export interface FinancialInsight {
  monthly_outlook: string;
  actionable_tips: string[];
}
