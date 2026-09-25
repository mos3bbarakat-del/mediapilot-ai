import type { Metadata } from "next";
import "./globals.css";
import { LocaleProvider } from "../components/LocaleProvider";

export const metadata: Metadata = {
  title: "MediaPilot AI",
  description: "Enterprise AI operating system for media organizations",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ar" dir="rtl">
      <body><LocaleProvider>{children}</LocaleProvider></body>
    </html>
  );
}
