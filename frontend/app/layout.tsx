import "../styles/globals.css";
import type { Metadata } from "next";
import { Lexend } from "next/font/google";
import { AppShell } from "@/components/layout/AppShell";

/* ---------------- FONT ---------------- */
const lexend = Lexend({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

/* ---------------- METADATA ---------------- */
export const metadata: Metadata = {
  title: "KnowFlow",
  description: "Adaptive Knowledge-Driven Multi-Agent Orchestrator",
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={lexend.variable}>
      <body className="font-sans antialiased bg-brand-navy text-white">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
