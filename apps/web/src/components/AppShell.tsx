"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { useLocale } from "./LocaleProvider";
import { createProject } from "../lib/api";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { lang, toggle, t } = useLocale();
  const router = useRouter();
  const [command, setCommand] = useState("");
  const [busy, setBusy] = useState(false);
  const [assistantError, setAssistantError] = useState<string | null>(null);

  async function submitProjectCommand(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = command.trim();
    if (!text || busy) return;
    setBusy(true);
    setAssistantError(null);
    try {
      const project = await createProject({ intake_mode: "chat", natural_language: text });
      setCommand("");
      router.push(`/projects/${project.id}`);
      router.refresh();
    } catch (error) {
      setAssistantError(error instanceof Error ? error.message : t("تعذر تنفيذ الطلب.", "Could not execute the request."));
    } finally {
      setBusy(false);
    }
  }

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
        <div className="chatBody">
          <div className="chatBubble">{t("صف مشروعًا جديدًا بلغتك الطبيعية، وسينشئ MediaPilot مساحة المشروع ويبدأ مسار العمل مباشرة.", "Describe a new project naturally. MediaPilot will create its workspace and start the workflow immediately.")}</div>
          {assistantError && <div className="error">{assistantError}</div>}
        </div>
        <form className="chatComposer" onSubmit={submitProjectCommand}>
          <input value={command} onChange={(event) => setCommand(event.target.value)} placeholder={t("صف المشروع الجديد…", "Describe the new project…")} aria-label={t("وصف المشروع", "Project description")} />
          <button className="button buttonPrimary" type="submit" disabled={busy || !command.trim()} aria-label={t("إنشاء المشروع", "Create project")}>{busy ? "…" : "↑"}</button>
        </form>
      </aside>
    </div>
  );
}
