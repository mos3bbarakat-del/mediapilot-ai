"use client";

import Link from "next/link";
import { AppShell } from "../components/AppShell";
import { useLocale } from "../components/LocaleProvider";

export default function HomePage() {
  const { t } = useLocale();
  const modules = [
    ["🎬", "Production AI", t("إدارة إنتاج الفيديو والبرامج والوثائقيات والإنتاج الضخم.", "Video, programs, documentaries and high-production workflows.")],
    ["✍️", "Content & Creative AI", t("البحث والإلهام والكتابة والتطوير الإبداعي.", "Research, inspiration, writing and creative development.")],
    ["🎨", "Design AI", t("التصميم والهوية والعروض والمواد البصرية.", "Design, identity, presentations and visual assets.")],
    ["🤝", "Client AI", t("التواصل مع العملاء والمتابعة والاعتمادات.", "Client communication, follow-up and approvals.")],
    ["📣", "Campaign AI", t("تخطيط الحملات وربط المحتوى والتصميم والإنتاج.", "Campaign planning across content, design and production.")],
    ["🎪", "Events AI", t("تخطيط وإدارة الفعاليات من الفكرة إلى التنفيذ.", "Plan and manage events from concept to execution.")],
  ];

  return (
    <AppShell>
      <div className="page">
        <div className="hero">
          <section className="card heroCard">
            <div className="eyebrow">MEDIAPILOT AI</div>
            <h1>{t("نظام تشغيل ذكي لشركات الإعلام والقنوات والجهات الكبيرة.", "An AI operating system for media companies, broadcasters and large organizations.")}</h1>
            <p className="muted">{t("تحدث إلى MediaPilot لإطلاق المشاريع وإدارة مراحل العمل من مساحة موحدة، مع بنية مؤسسية قابلة للتوسع والأتمتة.", "Talk to MediaPilot to launch projects and manage workflows from one workspace, built on an enterprise architecture designed for scale and automation.")}</p>
            <div className="actions" style={{ marginTop: 18 }}>
              <Link className="button buttonPrimary" href="/projects/new">{t("إنشاء مشروع", "Create Project")}</Link>
              <Link className="button" href="/projects">{t("عرض المشاريع", "View Projects")}</Link>
            </div>
          </section>
          <section className="card heroCard">
            <div className="eyebrow">{t("مساحة العمل", "WORKSPACE")}</div>
            <h3>{t("جاهزة لبدء مشروعك الأول.", "Ready for your first project.")}</h3>
            <p className="muted">{t("أنشئ المشروع بالشات أو بالنموذج، وسيظهر مباشرة داخل مساحة المشاريع.", "Create a project through chat or the form and it will appear immediately in your project workspace.")}</p>
          </section>
        </div>

        <div className="sectionTitle"><h2>{t("نماذج MediaPilot AI", "MediaPilot AI Models")}</h2></div>
        <div className="grid">
          {modules.map(([icon, title, body]) => (
            <article className="moduleCard" key={title}>
              <div className="moduleIcon">{icon}</div>
              <h3>{title}</h3>
              <p className="muted">{body}</p>
            </article>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
