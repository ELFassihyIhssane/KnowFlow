import "../styles/globals.css";
import type { Metadata } from "next";
import { AppShell } from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "KnowFlow",
  description: "Adaptive Knowledge-Driven Multi-Agent Orchestrator"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
