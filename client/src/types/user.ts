export interface User {
  id: string;
  email: string;
  full_name: string;
  currency: string;
  telegram_chat_id?: string | null;
  email_notifications_enabled: boolean;
  telegram_notifications_enabled: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
