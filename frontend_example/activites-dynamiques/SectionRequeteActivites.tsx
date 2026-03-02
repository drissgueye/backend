"use client";

import React, { useState, useEffect } from "react";
import { fetchActivitesRequete, updateActiviteRequete } from "./api";
import { ActiviteRequeteForm } from "./ActiviteRequeteForm";
import type { ActiviteRequete } from "./types";

const styles: Record<string, React.CSSProperties> = {
  section: { marginTop: "1.5rem", padding: "1rem", border: "1px solid #ddd", borderRadius: 8, background: "#fafafa" },
  list: { listStyle: "none", padding: 0, margin: 0 },
  item: { padding: "0.75rem 1rem", border: "1px solid #eee", borderRadius: 6, marginBottom: "0.5rem", background: "#fff" },
  meta: { fontSize: "0.85rem", color: "#666", marginTop: "0.25rem" },
  extra: { fontSize: "0.85rem", marginTop: "0.5rem", color: "#444" },
  actions: { display: "flex", gap: "0.5rem", marginTop: "0.5rem" },
  btn: { padding: "0.35rem 0.75rem", cursor: "pointer", fontSize: "0.9rem" },
};

interface SectionRequeteActivitesProps {
  requeteId: number;
  poleId: number;
  onRefreshRequete?: () => void;
}

export function SectionRequeteActivites({ requeteId, poleId, onRefreshRequete }: SectionRequeteActivitesProps) {
  const [activites, setActivites] = useState<ActiviteRequete[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  const load = () => {
    setLoading(true);
    fetchActivitesRequete(requeteId)
      .then(setActivites)
      .catch(() => setActivites([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, [requeteId]);

  const handleMarkCompleted = async (activite: ActiviteRequete) => {
    try {
      await updateActiviteRequete(requeteId, activite.id, {
        statut: "completed",
        date_realisation: new Date().toISOString(),
      });
      load();
      onRefreshRequete?.();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Erreur");
    }
  };

  const handleCancel = async (activite: ActiviteRequete) => {
    if (!confirm("Annuler cette activité ?")) return;
    try {
      await updateActiviteRequete(requeteId, activite.id, { statut: "cancelled" });
      load();
      onRefreshRequete?.();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Erreur");
    }
  };

  return (
    <section style={styles.section}>
      <h3 style={{ marginTop: 0 }}>Activités planifiées</h3>
      {loading ? (
        <p>Chargement…</p>
      ) : (
        <>
          <ul style={styles.list}>
            {activites.map((act) => (
              <li key={act.id} style={styles.item}>
                <strong>{act.titre}</strong>
                <div style={styles.meta}>
                  {act.type_activite_display} · {act.statut}
                  {act.date_planifiee && (
                    <> · {new Date(act.date_planifiee).toLocaleString("fr-FR")}</>
                  )}
                </div>
                {act.description && <p style={{ margin: "0.35rem 0 0", fontSize: "0.9rem" }}>{act.description}</p>}
                {act.extra_data && Object.keys(act.extra_data).length > 0 && (
                  <div style={styles.extra}>
                    {Object.entries(act.extra_data).map(([k, v]) => (
                      <span key={k} style={{ marginRight: "1rem" }}>
                        <strong>{k}</strong>: {String(v)}
                      </span>
                    ))}
                  </div>
                )}
                {act.statut === "planned" && (
                  <div style={styles.actions}>
                    <button type="button" style={styles.btn} onClick={() => handleMarkCompleted(act)}>
                      Marquer terminée
                    </button>
                    <button type="button" style={styles.btn} onClick={() => handleCancel(act)}>
                      Annuler
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
          {!showForm ? (
            <button type="button" style={styles.btn} onClick={() => setShowForm(true)}>
              + Ajouter une activité
            </button>
          ) : (
            <ActiviteRequeteForm
              requeteId={requeteId}
              poleId={poleId}
              onSuccess={() => { setShowForm(false); load(); onRefreshRequete?.(); }}
              onCancel={() => setShowForm(false)}
            />
          )}
        </>
      )}
    </section>
  );
}
