import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = { title: "SAT-SA | Local system status", description: "Supervisory Analytics Tool for SOC Assessment — Phase 1 foundation" };
export default function Layout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
