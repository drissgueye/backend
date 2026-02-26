/**
 * Types pour les événements retournés par GET /api/reunions/calendar-events/
 * À copier dans votre projet Next.js (ex. types/calendar.ts).
 */

export type CalendarEventType = "activite" | "reunion";

export interface CalendarEventBase {
  id: string;
  event_type: CalendarEventType;
  title: string;
  start: string; // ISO datetime
  end: string;
}

export interface CalendarEventActivite extends CalendarEventBase {
  event_type: "activite";
  type_activite: string;
  type_activite_display: string;
  statut: string;
  statut_display: string;
  requete_id: number;
  numero_reference: string;
  description: string;
  activite_id: number;
}

export interface CalendarEventReunion extends CalendarEventBase {
  event_type: "reunion";
  dossier_id: number;
  dossier_numero: string;
  lieu: string;
  ordre_du_jour: string;
  reunion_id: number;
  type_reunion?: string;
  type_reunion_display?: string;
  statut?: string;
  statut_display?: string;
}

export type CalendarEvent = CalendarEventActivite | CalendarEventReunion;

export function isActiviteEvent(e: CalendarEvent): e is CalendarEventActivite {
  return e.event_type === "activite";
}
