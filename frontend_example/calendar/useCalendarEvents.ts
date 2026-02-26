"use client";

import { useState, useEffect, useCallback } from "react";
import type { CalendarEvent } from "./types";

const defaultApiUrl = "http://localhost:8000/api";

function getApiUrl(): string {
  if (typeof window !== "undefined" && (process.env.NEXT_PUBLIC_API_URL as string)) {
    return (process.env.NEXT_PUBLIC_API_URL as string).replace(/\/$/, "");
  }
  return defaultApiUrl;
}

function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

/**
 * Hook pour récupérer les événements du calendrier (activités des requêtes + réunions).
 * À utiliser dans votre page /calendar.
 */
export function useCalendarEvents(
  range: { start: Date; end: Date },
  options?: { eventType?: "activite" | "reunion" }
) {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEvents = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setError("Non authentifié");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    const startStr = range.start.toISOString();
    const endStr = range.end.toISOString();
    const params = new URLSearchParams({
      start: startStr,
      end: endStr,
    });
    if (options?.eventType) {
      params.set("event_type", options.eventType);
    }

    try {
      const res = await fetch(
        `${getApiUrl()}/reunions/calendar-events/?${params.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!res.ok) {
        if (res.status === 401) {
          setError("Session expirée. Veuillez vous reconnecter.");
        } else {
          setError(`Erreur ${res.status}`);
        }
        setEvents([]);
        return;
      }

      const data = await res.json();
      setEvents(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur réseau");
      setEvents([]);
    } finally {
      setLoading(false);
    }
  }, [range.start.toISOString(), range.end.toISOString(), options?.eventType]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  return { events, loading, error, refetch: fetchEvents };
}

/**
 * Convertit les événements API au format FullCalendar (si vous utilisez @fullcalendar/react).
 */
export function toFullCalendarEvents(events: CalendarEvent[]) {
  return events.map((e) => ({
    id: e.id,
    title: e.title,
    start: e.start,
    end: e.end,
    extendedProps: {
      event_type: e.event_type,
      ...(e.event_type === "activite"
        ? {
            numero_reference: (e as import("./types").CalendarEventActivite).numero_reference,
            requete_id: (e as import("./types").CalendarEventActivite).requete_id,
            activite_id: (e as import("./types").CalendarEventActivite).activite_id,
            type_activite_display: (e as import("./types").CalendarEventActivite).type_activite_display,
            statut_display: (e as import("./types").CalendarEventActivite).statut_display,
          }
        : {}),
    },
  }));
}
