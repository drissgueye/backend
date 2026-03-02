"use client";

import React, { useState, useEffect } from "react";
import { fetchActivitesDisponibles, createActiviteRequete } from "./api";
import { ExtraDataFields } from "./ExtraDataFields";
import type { ActiviteTemplate, PayloadActiviteRequete } from "./types";

const styles: Record<string, React.CSSProperties> = {
  form: { maxWidth: 520, padding: "1rem", border: "1px solid #ddd", borderRadius: 8, background: "#fafafa" },
  field: { marginBottom: "1rem" },
  label: { display: "block", fontWeight: 600, marginBottom: "0.35rem", fontSize: "0.9rem" },
  input: { width: "100%", padding: "0.5rem", fontSize: "1rem" },
  select: { width: "100%", padding: "0.5rem", fontSize: "1rem" },
  row: { display: "flex", gap: "1rem", flexWrap: "wrap" },
  button: { padding: "0.5rem 1rem", cursor: "pointer", fontSize: "1rem" },
  error: { color: "crimson", marginBottom: "0.5rem", fontSize: "0.9rem" },
};

interface ActiviteRequeteFormProps {
  requeteId: number;
  poleId: number;
  onSuccess: () => void;
  onCancel?: () => void;
}

export function ActiviteRequeteForm({
  requeteId,
  poleId,
  onSuccess,
  onCancel,
}: ActiviteRequeteFormProps) {
  const [templates, setTemplates] = useState<ActiviteTemplate[]>([]);
  const [loadingTemplates, setLoadingTemplates] = useState(true);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
  const [useLegacy, setUseLegacy] = useState(false);
  const [legacyType, setLegacyType] = useState("call");
  const [titre, setTitre] = useState("");
  const [description, setDescription] = useState("");
  const [datePlanifiee, setDatePlanifiee] = useState(() => {
    const d = new Date();
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().slice(0, 16);
  });
  const [extraData, setExtraData] = useState<Record<string, unknown>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoadingTemplates(true);
    fetchActivitesDisponibles(poleId)
      .then((data) => {
        if (!cancelled) setTemplates(data);
      })
      .catch(() => {
        if (!cancelled) setTemplates([]);
      })
      .finally(() => {
        if (!cancelled) setLoadingTemplates(false);
      });
    return () => {
      cancelled = true;
    };
  }, [poleId]);

  const selectedTemplate = templates.find((t) => t.id === selectedTemplateId);
  const champs = selectedTemplate?.champs ?? [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    const payload: PayloadActiviteRequete = {
      requete_id: requeteId,
      titre: titre.trim() || (selectedTemplate ? selectedTemplate.nom : "Activité"),
      date_planifiee: new Date(datePlanifiee).toISOString(),
    };
    if (description.trim()) payload.description = description.trim();
    if (useLegacy) {
      payload.type_activite = legacyType;
    } else if (selectedTemplateId) {
      payload.activite_template_id = selectedTemplateId;
      if (Object.keys(extraData).length) payload.extra_data = extraData;
    } else {
      setError("Veuillez choisir un type d'activité (modèle ou legacy).");
      setSubmitting(false);
      return;
    }
    try {
      await createActiviteRequete(requeteId, payload);
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de la création.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <h3 style={{ marginTop: 0, marginBottom: "1rem" }}>Ajouter une activité</h3>
      {error && <div style={styles.error}>{error}</div>}

      <div style={styles.field}>
        <label style={styles.label}>Type d'activité</label>
        <div style={{ ...styles.row, flexDirection: "column", gap: "0.5rem" }}>
          <label style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
            <input
              type="radio"
              checked={!useLegacy}
              onChange={() => { setUseLegacy(false); setSelectedTemplateId(null); setExtraData({}); }}
            />
            <span style={{ marginLeft: "0.5rem" }}>Modèles dynamiques (assignés à ce pôle)</span>
          </label>
          <label style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
            <input type="radio" checked={useLegacy} onChange={() => setUseLegacy(true)} />
            <span style={{ marginLeft: "0.5rem" }}>Types simples (appel, rendez-vous, note…)</span>
          </label>
        </div>
      </div>

      {!useLegacy && (
        <div style={styles.field}>
          <label style={styles.label}>Modèle d'activité *</label>
          <select
            value={selectedTemplateId ?? ""}
            onChange={(e) => {
              const id = e.target.value ? Number(e.target.value) : null;
              setSelectedTemplateId(id);
              setExtraData({});
            }}
            style={styles.select}
            disabled={loadingTemplates}
          >
            <option value="">— Choisir un modèle —</option>
            {templates.map((t) => (
              <option key={t.id} value={t.id}>
                {t.nom}
              </option>
            ))}
            {!loadingTemplates && !templates.length && (
              <option value="" disabled>Aucun modèle assigné à ce pôle</option>
            )}
          </select>
        </div>
      )}

      {useLegacy && (
        <div style={styles.field}>
          <label style={styles.label}>Type simple</label>
          <select value={legacyType} onChange={(e) => setLegacyType(e.target.value)} style={styles.select}>
            <option value="call">Appel téléphonique</option>
            <option value="meeting">Rendez-vous</option>
            <option value="document">Document à fournir</option>
            <option value="note">Note interne</option>
          </select>
        </div>
      )}

      <div style={styles.field}>
        <label style={styles.label} htmlFor="act-titre">Titre *</label>
        <input
          id="act-titre"
          type="text"
          value={titre}
          onChange={(e) => setTitre(e.target.value)}
          placeholder={selectedTemplate ? selectedTemplate.nom : "Titre de l'activité"}
          style={styles.input}
        />
      </div>
      <div style={styles.field}>
        <label style={styles.label} htmlFor="act-desc">Description</label>
        <textarea
          id="act-desc"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={2}
          style={styles.input}
        />
      </div>
      <div style={styles.field}>
        <label style={styles.label} htmlFor="act-date">Date planifiée *</label>
        <input
          id="act-date"
          type="datetime-local"
          value={datePlanifiee}
          onChange={(e) => setDatePlanifiee(e.target.value)}
          style={styles.input}
        />
      </div>

      {selectedTemplate && champs.length > 0 && (
        <ExtraDataFields champs={champs} value={extraData} onChange={setExtraData} />
      )}

      <div style={{ ...styles.row, marginTop: "1.25rem", gap: "0.5rem" }}>
        <button type="submit" style={styles.button} disabled={submitting}>
          {submitting ? "Création…" : "Créer l'activité"}
        </button>
        {onCancel && (
          <button type="button" style={styles.button} onClick={onCancel}>
            Annuler
          </button>
        )}
      </div>
    </form>
  );
}
