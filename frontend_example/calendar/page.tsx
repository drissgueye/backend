"use client";

import { useState, useMemo } from "react";
import { useCalendarEvents } from "./useCalendarEvents";
import { isActiviteEvent } from "./types";

/**
 * Page calendrier – Affiche les activités des requêtes (et optionnellement les réunions).
 * À placer dans votre projet Next.js sous : app/calendar/page.tsx
 *
 * Prérequis :
 * - Variable d’environnement NEXT_PUBLIC_API_URL (ex. http://localhost:8000/api)
 * - Token JWT stocké dans localStorage sous la clé "access_token" après login
 *
 * Pour utiliser avec FullCalendar : installez @fullcalendar/react et remplacez
 * le rendu ci‑dessous par <FullCalendar events={toFullCalendarEvents(events)} ... />
 */

function getMonthRange(date: Date) {
  const start = new Date(date.getFullYear(), date.getMonth(), 1);
  const end = new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59, 999);
  return { start, end };
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("fr-FR", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function CalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(() => new Date());
  const [eventTypeFilter, setEventTypeFilter] = useState<"activite" | "reunion" | undefined>(undefined);

  const range = useMemo(() => getMonthRange(currentMonth), [currentMonth]);
  const { events, loading, error, refetch } = useCalendarEvents(range, {
    eventType: eventTypeFilter,
  });

  const activites = events.filter(isActiviteEvent);
  const reunions = events.filter((e) => e.event_type === "reunion");

  const goPrev = () => setCurrentMonth((d) => new Date(d.getFullYear(), d.getMonth() - 1));
  const goNext = () => setCurrentMonth((d) => new Date(d.getFullYear(), d.getMonth() + 1));
  const goToday = () => setCurrentMonth(new Date());

  const monthLabel = currentMonth.toLocaleDateString("fr-FR", { month: "long", year: "numeric" });

  return (
    <div style={{ padding: "1.5rem", maxWidth: 900, margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1rem" }}>Calendrier – Activités des requêtes</h1>

      <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap", marginBottom: "1rem" }}>
        <button type="button" onClick={goPrev}>← Mois précédent</button>
        <button type="button" onClick={goToday}>Aujourd’hui</button>
        <button type="button" onClick={goNext}>Mois suivant →</button>
        <span style={{ marginLeft: "0.5rem", fontWeight: 600 }}>{monthLabel}</span>
        <select
          value={eventTypeFilter ?? ""}
          onChange={(e) => setEventTypeFilter((e.target.value || undefined) as "activite" | "reunion" | undefined)}
          style={{ marginLeft: "auto" }}
        >
          <option value="">Tous (activités + réunions)</option>
          <option value="activite">Activités des requêtes uniquement</option>
          <option value="reunion">Réunions uniquement</option>
        </select>
        <button type="button" onClick={refetch} disabled={loading}>Rafraîchir</button>
      </div>

      {error && (
        <div style={{ color: "crimson", marginBottom: "1rem" }}>{error}</div>
      )}

      {loading ? (
        <p>Chargement des événements…</p>
      ) : (
        <>
          {activites.length > 0 && (
            <section style={{ marginBottom: "1.5rem" }}>
              <h2 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>
                Activités des requêtes ({activites.length})
              </h2>
              <ul style={{ listStyle: "none", padding: 0 }}>
                {activites.map((ev) => (
                  <li
                    key={ev.id}
                    style={{
                      border: "1px solid #ddd",
                      borderRadius: 8,
                      padding: "0.75rem 1rem",
                      marginBottom: "0.5rem",
                      background: "#fafafa",
                    }}
                  >
                    <strong>{ev.title}</strong>
                    <div style={{ fontSize: "0.9rem", color: "#555", marginTop: "0.25rem" }}>
                      {ev.numero_reference} · {ev.type_activite_display} · {ev.statut_display}
                    </div>
                    <div style={{ fontSize: "0.85rem", color: "#666", marginTop: "0.25rem" }}>
                      {formatDate(ev.start)}
                    </div>
                    {ev.description && (
                      <p style={{ marginTop: "0.5rem", fontSize: "0.9rem" }}>{ev.description}</p>
                    )}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {reunions.length > 0 && (
            <section>
              <h2 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>
                Réunions ({reunions.length})
              </h2>
              <ul style={{ listStyle: "none", padding: 0 }}>
                {reunions.map((ev) => (
                  <li
                    key={ev.id}
                    style={{
                      border: "1px solid #ddd",
                      borderRadius: 8,
                      padding: "0.75rem 1rem",
                      marginBottom: "0.5rem",
                      background: "#f0f7ff",
                    }}
                  >
                    <strong>{ev.title}</strong>
                    <div style={{ fontSize: "0.85rem", color: "#666", marginTop: "0.25rem" }}>
                      {formatDate(ev.start)}
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {events.length === 0 && !error && (
            <p style={{ color: "#666" }}>Aucun événement sur cette période.</p>
          )}
        </>
      )}
    </div>
  );
}
