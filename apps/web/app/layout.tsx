import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = { title: "SAT-SA | Supervisory workspace", description: "Supervisory Analytics Tool for SOC Assessment — evidence-led synthetic prototype" };
export default function Layout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
