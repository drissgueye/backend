/**
 * Types pour les activités dynamiques (modèles d'activité + activités sur requêtes).
 * Alignés sur l'API backend Django/DRF.
 */

export const TYPE_CHAMP_ACTIVITE = [
  "text",
  "textarea",
  "number",
  "date",
  "datetime",
  "boolean",
  "file",
  "choice",
] as const;
export type TypeChampActivite = (typeof TYPE_CHAMP_ACTIVITE)[number];

export interface OptionChoice {
  value: string;
  label: string;
}

export interface ChampActiviteTemplate {
  id?: number;
  nom: string;
  label: string;
  type_champ: TypeChampActivite;
  type_champ_display?: string;
  required: boolean;
  ordre: number;
  options: OptionChoice[];
  is_active: boolean;
}

export interface ActiviteTemplate {
  id: number;
  nom: string;
  code: string;
  description: string;
  is_active: boolean;
  ordre: number;
  champs: ChampActiviteTemplate[];
  pole_ids: number[];
  created_at?: string;
  updated_at?: string;
}

export interface ActiviteTemplateListe {
  id: number;
  nom: string;
  code: string;
  is_active: boolean;
  ordre: number;
  pole_ids: number[];
}

export interface ActiviteRequete {
  id: number;
  requete: string;
  requete_id?: number;
  activite_template?: ActiviteTemplateListe | null;
  activite_template_id?: number | null;
  type_activite: string;
  type_activite_display: string;
  titre: string;
  description: string;
  date_planifiee: string;
  statut: string;
  date_realisation?: string | null;
  commentaire: string;
  piece_jointe_compte_rendu?: string | null;
  extra_data: Record<string, unknown>;
  created_by?: string;
  created_by_id?: number;
  created_at: string;
}

export interface PayloadActiviteTemplate {
  nom: string;
  code: string;
  description?: string;
  is_active?: boolean;
  ordre?: number;
  champs: Partial<ChampActiviteTemplate>[];
  pole_ids: number[];
}

export interface PayloadActiviteRequete {
  requete_id: number;
  activite_template_id?: number | null;
  type_activite?: string;
  titre: string;
  description?: string;
  date_planifiee: string;
  extra_data?: Record<string, unknown>;
}
