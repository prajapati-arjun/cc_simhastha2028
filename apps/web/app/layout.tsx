import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Simhastha 2028 - Ujjain Digital Experience Platform",
  description:
    "Sprint 1 (Phase 1: Foundation) local development scaffold. Not a live deployment.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
