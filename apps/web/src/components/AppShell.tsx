"use client";

import Link from "next/link";
import { useLocale } from "@/components/LocaleProvider";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { lang, toggle, t } = useLocale();
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand"><div className="brandMark">MP</div><div className="brandText">MediaPilot <span>AI</span></div></div>
        <nav className="nav">
          <Link href="/">{t("الرئيسية", "Home")}</Link>
          <Link href="/projects">{t("المشاريع", "Projects")}</Link>
          <Link href="/projects/new">{t("إنشاء مشروع", "Create Project")}</Link>
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <input className="search" placeholder={t("ابحث في المشاريع والملفات والأشخاص…", "Search projects, files and people…")} aria-label={t("البحث", "Search")} />
          <div className="actions">
            <button className="button" onClick={toggle}>{lang === "ar" ? "EN" : "AR"}</button>
            <Link className="button buttonPrimary" href="/projects/new">{t("مشروع جديد", "New Project")}</Link>
          </div>
        </header>
        {children}
      </main>

      <aside className="assistant">
        <div className="assistantHead"><strong>MediaPilot Assistant</strong><div className="assistantStatus">{t("جاهز للعمل", "Ready")}</div></div>
        <div className="chatBody"><div className="chatBubble">{t("يمكنك إنشاء مشروع بالكلام الطبيعي أو بالنموذج. تنفيذ الأوامر الفعلي يتم عبر Core API وليس داخل المتصفح.", "Create projects in natural language or through the form. Real actions are executed by the Core API, not browser-only mock logic.")}</div></div>
        <div className="chatComposer"><input placeholder={t("اكتب طلبك…", "Type your request…")} /><button className="button buttonPrimary">↑</button></div>
      </aside>
    </div>
  );
}
