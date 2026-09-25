"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "../../../components/AppShell";
import { useLocale } from "../../../components/LocaleProvider";
import { getProject, type Project } from "../../../lib/api";

const stages = ["Briefing", "Pre-Production", "Production", "Post-Production", "Delivery"];

export default function ProjectPage() {
  const params = useParams<{ id: string }>();
  const { t } = useLocale();
  const [project, setProject] = useState<Project | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProject(params.id).then(setProject).catch((e: Error) => setError(e.message));
  }, [params.id]);

  return (
    <AppShell>
      <div className="page">
        {error && <div className="empty"><div><h3>{t("تعذر تحميل المشروع", "Could not load project")}</h3><p className="muted">{error}</p></div></div>}
        {!error && !project && <div className="empty"><div><h3>{t("جارٍ تحميل المشروع…", "Loading project…")}</h3></div></div>}
        {project && (
          <>
            <div className="eyebrow">PRODUCTION AI</div>
            <h1>{project.name}</h1>
            <p className="muted">{project.client_name ?? t("لم يتم تحديد العميل بعد", "Client not specified yet")}</p>
            <div className="grid" style={{ gridTemplateColumns: "repeat(5,minmax(0,1fr))", marginTop: 20 }}>
              {stages.map((stage, index) => (
                <article className="moduleCard" key={stage}>
                  <div className="eyebrow">0{index + 1}</div>
                  <h3>{stage}</h3>
                  <p className="muted">{t("ستظهر بيانات هذه المرحلة من المشروع هنا.", "Project data for this stage will appear here.")}</p>
                </article>
              ))}
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
