import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BillGuard — AI-Powered Financial Guardian",
  description:
    "Proactively manage recurring bills, monitor subscriptions, detect price hikes, and protect your personal cash flow.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
