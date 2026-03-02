/**
 * Client API pour les activités dynamiques.
 * Utilise NEXT_PUBLIC_API_URL et le token dans localStorage (clé "access_token").
 */

import type {
  ActiviteTemplate,
  ActiviteTemplateListe,
  ActiviteRequete,
  PayloadActiviteTemplate,
  PayloadActiviteRequete,
} from "./types";

const defaultApiUrl = "http://localhost:8000/api";

function getApiUrl(): string {
  if (typeof window !== "undefined" && (process.env.NEXT_PUBLIC_API_URL as string)) {
    return (process.env.NEXT_PUBLIC_API_URL as string).replace(/\/$/, "");
  }
  return defaultApiUrl;
}

function getHeaders(): HeadersInit {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    let message = `Erreur ${res.status}`;
    try {
      const data = JSON.parse(text);
      if (data.detail) message = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      else if (data.extra_data) message = Array.isArray(data.extra_data) ? data.extra_data.join(" ") : String(data.extra_data);
    } catch {
      if (text) message = text.slice(0, 200);
    }
    throw new Error(message);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

/** Liste des modèles d'activité (optionnel: filtrer par pôle). */
export async function fetchActiviteTemplates(params?: { pole_id?: number; is_active?: boolean }): Promise<ActiviteTemplateListe[] | ActiviteTemplate[]> {
  const url = new URL(`${getApiUrl()}/activite-templates/`);
  if (params?.pole_id) url.searchParams.set("pole", String(params.pole_id));
  if (params?.is_active !== undefined) url.searchParams.set("is_active", String(params.is_active));
  const res = await fetch(url.toString(), { headers: getHeaders() });
  return handleResponse(res);
}

/** Détail d'un modèle d'activité (avec champs). */
export async function fetchActiviteTemplate(id: number): Promise<ActiviteTemplate> {
  const res = await fetch(`${getApiUrl()}/activite-templates/${id}/`, { headers: getHeaders() });
  return handleResponse(res);
}

/** Activités disponibles pour un pôle (workflow). */
export async function fetchActivitesDisponibles(poleId: number): Promise<ActiviteTemplate[]> {
  const res = await fetch(`${getApiUrl()}/poles/${poleId}/activites-disponibles/`, { headers: getHeaders() });
  return handleResponse(res);
}

/** Créer un modèle d'activité (admin). */
export async function createActiviteTemplate(payload: PayloadActiviteTemplate): Promise<ActiviteTemplate> {
  const res = await fetch(`${getApiUrl()}/activite-templates/`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

/** Mettre à jour un modèle d'activité (admin). */
export async function updateActiviteTemplate(id: number, payload: Partial<PayloadActiviteTemplate>): Promise<ActiviteTemplate> {
  const res = await fetch(`${getApiUrl()}/activite-templates/${id}/`, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

/** Désactiver un modèle (soft delete, admin). */
export async function deleteActiviteTemplate(id: number): Promise<void> {
  const res = await fetch(`${getApiUrl()}/activite-templates/${id}/`, {
    method: "DELETE",
    headers: getHeaders(),
  });
  await handleResponse<void>(res);
}

/** Liste des activités d'une requête. */
export async function fetchActivitesRequete(requeteId: number): Promise<ActiviteRequete[]> {
  const res = await fetch(`${getApiUrl()}/requetes/${requeteId}/activites/`, { headers: getHeaders() });
  return handleResponse(res);
}

/** Créer une activité sur une requête. */
export async function createActiviteRequete(requeteId: number, payload: PayloadActiviteRequete): Promise<ActiviteRequete> {
  const body = { ...payload, requete_id: requeteId };
  const res = await fetch(`${getApiUrl()}/requetes/${requeteId}/activites/`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

/** Mettre à jour une activité (statut, commentaire, extra_data, etc.). */
export async function updateActiviteRequete(
  requeteId: number,
  activiteId: number,
  payload: Partial<Pick<ActiviteRequete, "statut" | "date_realisation" | "commentaire" | "titre" | "description" | "date_planifiee" | "extra_data">>
): Promise<ActiviteRequete> {
  const res = await fetch(`${getApiUrl()}/requetes/${requeteId}/activites/${activiteId}/`, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

/** Liste des pôles (pour les selects admin). */
export async function fetchPoles(): Promise<{ id: number; nom: string; description?: string }[]> {
  const res = await fetch(`${getApiUrl()}/poles/`, { headers: getHeaders() });
  const data = await handleResponse<{ id: number; nom: string; description?: string }[]>(res);
  return Array.isArray(data) ? data : [];
}
