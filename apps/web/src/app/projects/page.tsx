"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "../../components/AppShell";
import { useLocale } from "../../components/LocaleProvider";
import { listProjects, type Project } from "../../lib/api";

export default function ProjectsPage() {
  const { t } = useLocale();
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listProjects().then(setProjects).catch((e: Error) => setError(e.message)).finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <div className="page">
        <div className="sectionTitle">
          <div><div className="eyebrow">PROJECTS</div><h1>{t("المشاريع", "Projects")}</h1></div>
          <Link className="button buttonPrimary" href="/projects/new">{t("إنشاء مشروع", "Create Project")}</Link>
        </div>
        {loading && <div className="empty"><div><h3>{t("جارٍ تحميل المشاريع…", "Loading projects…")}</h3></div></div>}
        {!loading && error && <div className="empty"><div><h3>{t("تعذر الاتصال بخدمة المشاريع.", "Could not connect to the project service.")}</h3><p className="muted">{error}</p></div></div>}
        {!loading && !error && projects.length === 0 && (
          <div className="empty"><div><h3>{t("لا توجد مشاريع حتى الآن", "No projects yet")}</h3><p className="muted">{t("أنشئ أول مشروع بالشات أو بالنموذج.", "Create your first project through chat or the form.")}</p><Link className="button buttonPrimary" href="/projects/new">{t("إنشاء مشروع جديد", "Create New Project")}</Link></div></div>
        )}
        {!loading && !error && projects.length > 0 && (
          <div className="grid">
            {projects.map((project) => (
              <Link href={`/projects/${project.id}`} className="projectCard" key={project.id}>
                <div className="eyebrow">{project.production_category ?? "PROJECT"}</div>
                <h3>{project.name}</h3>
                <p className="muted">{project.client_name ?? t("بدون عميل محدد", "No client specified")}</p>
                <p className="muted">{t("الحالة", "Status")}: {project.status}</p>
              </Link>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
