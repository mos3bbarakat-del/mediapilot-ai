"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "../../../components/AppShell";
import { useLocale } from "../../../components/LocaleProvider";
import { createProject } from "../../../lib/api";

type Mode = "chat" | "form";

export default function NewProjectPage() {
  const router = useRouter();
  const { t } = useLocale();
  const [mode, setMode] = useState<Mode>("chat");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    const data = new FormData(event.currentTarget);
    try {
      let project;
      if (mode === "chat") {
        const natural_language = String(data.get("natural_language") ?? "").trim();
        if (!natural_language) throw new Error(t("اكتب وصف المشروع أولًا.", "Describe the project first."));
        project = await createProject({ intake_mode: "chat", natural_language });
      } else {
        project = await createProject({
          intake_mode: "form",
          name: String(data.get("name") ?? "").trim(),
          client_name: String(data.get("client_name") ?? "").trim() || undefined,
          production_category: String(data.get("production_category") ?? "").trim() || undefined,
          production_type: String(data.get("production_type") ?? "").trim() || undefined,
          description: String(data.get("description") ?? "").trim() || undefined,
        });
      }
      router.push(`/projects/${project.id}`);
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("حدث خطأ غير متوقع.", "An unexpected error occurred."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <div className="page">
        <div className="eyebrow">NEW PROJECT</div>
        <h1>{t("إنشاء مشروع", "Create Project")}</h1>
        <p className="muted">{t("يمكنك وصف المشروع طبيعيًا، أو إدخال الحقول بنفسك. كلا المسارين ينشئان مشروعًا داخل Core API.", "Describe the project naturally or fill in the fields yourself. Both paths create a real project through the Core API.")}</p>

        <div className="tabs">
          <button type="button" className={`tab ${mode === "chat" ? "tabActive" : ""}`} onClick={() => setMode("chat")}>{t("بالشات", "Chat")}</button>
          <button type="button" className={`tab ${mode === "form" ? "tabActive" : ""}`} onClick={() => setMode("form")}>{t("بالنموذج", "Form")}</button>
        </div>

        <form className="card heroCard" onSubmit={submit}>
          {mode === "chat" ? (
            <div className="field">
              <label className="label" htmlFor="natural_language">{t("صف المشروع كما تتحدث عادةً", "Describe the project naturally")}</label>
              <textarea id="natural_language" name="natural_language" className="textarea" placeholder={t("نريد تنفيذ فيديو لجهة… سنقابل ثلاثة متخصصين يتحدثون عن…", "We need a video for a client… we will interview three specialists about…")} />
              <p className="muted">{t("يحفظ النظام الإدخال كما هو. وكيل Intake مسؤول عن استخراج العميل والنوع والمتطلبات بعد توصيل مزود الذكاء الاصطناعي.", "The input is stored exactly as provided. The Intake Agent extracts client, type and requirements once an AI provider is connected.")}</p>
            </div>
          ) : (
            <div className="formGrid">
              <div className="field"><label className="label" htmlFor="name">{t("اسم المشروع", "Project name")}</label><input className="input" id="name" name="name" required /></div>
              <div className="field"><label className="label" htmlFor="client_name">{t("العميل", "Client")}</label><input className="input" id="client_name" name="client_name" /></div>
              <div className="field"><label className="label" htmlFor="production_category">{t("التصنيف الرئيسي", "Main category")}</label><select className="select" id="production_category" name="production_category" defaultValue=""><option value="">{t("اختر…", "Select…")}</option><option value="standard-video">{t("فيديو عادي", "Standard Video")}</option><option value="program">{t("برنامج", "Program")}</option><option value="high-production">High Production</option><option value="documentary">{t("وثائقي", "Documentary")}</option></select></div>
              <div className="field"><label className="label" htmlFor="production_type">{t("النوع الفرعي", "Subtype")}</label><input className="input" id="production_type" name="production_type" placeholder={t("مقابلة، برومو، بودكاست، TVC…", "Interview, promo, podcast, TVC…")} /></div>
              <div className="field fieldFull"><label className="label" htmlFor="description">{t("وصف المشروع", "Project description")}</label><textarea className="textarea" id="description" name="description" /></div>
            </div>
          )}
          {error && <div className="error">{error}</div>}
          <div className="actions" style={{ marginTop: 18 }}><button className="button buttonPrimary" type="submit" disabled={busy}>{busy ? t("جارٍ الإنشاء…", "Creating…") : t("إنشاء المشروع", "Create Project")}</button></div>
        </form>
      </div>
    </AppShell>
  );
}
