export type Project = {
  id: string;
  name: string;
  description: string | null;
  client_name: string | null;
  production_category: string | null;
  production_type: string | null;
  status: string;
  intake_mode: "chat" | "form" | "hybrid";
  created_at: string;
};

export type CreateProjectInput = {
  intake_mode: "chat" | "form" | "hybrid";
  natural_language?: string;
  name?: string;
  description?: string;
  client_name?: string;
  production_category?: string;
  production_type?: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function headers(): Record<string, string> {
  const result: Record<string, string> = { "Content-Type": "application/json" };
  if (process.env.NEXT_PUBLIC_DEV_AUTH === "true") {
    result["X-Organization-ID"] = "11111111-1111-4111-8111-111111111111";
    result["X-Subject"] = "local-admin";
  }
  return result;
}

export async function listProjects(): Promise<Project[]> {
  const response = await fetch(`${API_URL}/v1/projects`, {
    headers: headers(),
    cache: "no-store",
  });
  if (!response.ok) throw new Error(`Failed to load projects (${response.status})`);
  return response.json();
}

export async function createProject(input: CreateProjectInput): Promise<Project> {
  const response = await fetch(`${API_URL}/v1/projects`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Failed to create project (${response.status})`);
  }
  return response.json();
}

export async function getProject(id: string): Promise<Project> {
  const response = await fetch(`${API_URL}/v1/projects/${id}`, { headers: headers(), cache: "no-store" });
  if (!response.ok) throw new Error(`Failed to load project (${response.status})`);
  return response.json();
}
