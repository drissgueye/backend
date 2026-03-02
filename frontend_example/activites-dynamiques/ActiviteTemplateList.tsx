"use client";

import React, { useState, useEffect } from "react";
import { fetchActiviteTemplates, deleteActiviteTemplate } from "./api";
import { ActiviteTemplateForm } from "./ActiviteTemplateForm";
import type { ActiviteTemplateListe } from "./types";

const styles: Record<string, React.CSSProperties> = {
  list: { listStyle: "none", padding: 0, margin: 0 },
  item: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.75rem 1rem", border: "1px solid #ddd", borderRadius: 8, marginBottom: "0.5rem", background: "#fff" },
  itemInactive: { opacity: 0.7, background: "#f5f5f5" },
  actions: { display: "flex", gap: "0.5rem" },
  btn: { padding: "0.35rem 0.75rem", cursor: "pointer", fontSize: "0.9rem" },
};

export function ActiviteTemplateList() {
  const [templates, setTemplates] = useState<ActiviteTemplateListe[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [creating, setCreating] = useState(false);

  const load = () => {
    setLoading(true);
    fetchActiviteTemplates()
      .then((data) => setTemplates(Array.isArray(data) ? data : []))
      .catch(() => setTemplates([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm("Désactiver ce modèle ? Les activités déjà créées resteront visibles.")) return;
    try {
      await deleteActiviteTemplate(id);
      load();
      if (editingId === id) setEditingId(null);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Erreur");
    }
  };

  if (loading) return <p>Chargement des modèles d'activité…</p>;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h2 style={{ margin: 0 }}>Modèles d'activité</h2>
        <button
          type="button"
          style={styles.btn}
          onClick={() => { setCreating(true); setEditingId(null); }}
        >
          + Nouveau modèle
        </button>
      </div>

      {creating && (
        <div style={{ marginBottom: "1.5rem" }}>
          <ActiviteTemplateForm
            onSuccess={() => { setCreating(false); load(); }}
            onCancel={() => setCreating(false)}
          />
        </div>
      )}

      {editingId && !creating && (
        <div style={{ marginBottom: "1.5rem" }}>
          <ActiviteTemplateForm
            templateId={editingId}
            onSuccess={() => { setEditingId(null); load(); }}
            onCancel={() => setEditingId(null)}
          />
        </div>
      )}

      <ul style={styles.list}>
        {templates.map((t) => (
          <li
            key={t.id}
            style={{
              ...styles.item,
              ...(t.is_active ? {} : styles.itemInactive),
            }}
          >
            <span>
              <strong>{t.nom}</strong>
              <span style={{ marginLeft: "0.5rem", color: "#666", fontSize: "0.9rem" }}>
                {t.code}
                {t.pole_ids?.length ? ` · ${t.pole_ids.length} pôle(s)` : ""}
              </span>
            </span>
            <div style={styles.actions}>
              <button type="button" style={styles.btn} onClick={() => { setEditingId(t.id); setCreating(false); }}>
                Modifier
              </button>
              {t.is_active && (
                <button type="button" style={styles.btn} onClick={() => handleDelete(t.id)}>
                  Désactiver
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
      {!templates.length && !creating && <p style={{ color: "#666" }}>Aucun modèle d'activité. Créez-en un (réservé aux administrateurs).</p>}
    </div>
  );
}
