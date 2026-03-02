"use client";

import React, { useState, useEffect } from "react";
import { fetchPoles, createActiviteTemplate, updateActiviteTemplate, fetchActiviteTemplate } from "./api";
import { ChampActiviteTemplateForm } from "./ChampActiviteTemplateForm";
import type { ActiviteTemplate, ChampActiviteTemplate, PayloadActiviteTemplate } from "./types";

const styles: Record<string, React.CSSProperties> = {
  form: { maxWidth: 720, padding: "1.25rem", border: "1px solid #ddd", borderRadius: 8, background: "#fafafa" },
  field: { marginBottom: "1rem" },
  label: { display: "block", fontWeight: 600, marginBottom: "0.35rem", fontSize: "0.9rem" },
  input: { width: "100%", padding: "0.5rem", fontSize: "1rem" },
  select: { width: "100%", padding: "0.5rem", fontSize: "1rem", minHeight: 100 },
  row: { display: "flex", gap: "1rem", flexWrap: "wrap" },
  button: { padding: "0.5rem 1rem", cursor: "pointer", fontSize: "1rem" },
  error: { color: "crimson", marginBottom: "0.5rem", fontSize: "0.9rem" },
};

interface ActiviteTemplateFormProps {
  templateId?: number | null;
  onSuccess: () => void;
  onCancel?: () => void;
}

export function ActiviteTemplateForm({ templateId, onSuccess, onCancel }: ActiviteTemplateFormProps) {
  const [poles, setPoles] = useState<{ id: number; nom: string }[]>([]);
  const [nom, setNom] = useState("");
  const [code, setCode] = useState("");
  const [description, setDescription] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [ordre, setOrdre] = useState(0);
  const [poleIds, setPoleIds] = useState<number[]>([]);
  const [champs, setChamps] = useState<Partial<ChampActiviteTemplate>[]>([]);
  const [loading, setLoading] = useState(!!templateId);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPoles().then(setPoles).catch(() => setPoles([]));
  }, []);

  useEffect(() => {
    if (!templateId) return;
    setLoading(true);
    fetchActiviteTemplate(templateId)
      .then((t) => {
        setNom(t.nom);
        setCode(t.code);
        setDescription(t.description ?? "");
        setIsActive(t.is_active);
        setOrdre(t.ordre);
        setPoleIds(t.pole_ids ?? []);
        setChamps(
          (t.champs ?? []).map((c) => ({
            id: c.id,
            nom: c.nom,
            label: c.label,
            type_champ: c.type_champ,
            required: c.required,
            ordre: c.ordre,
            options: c.options ?? [],
            is_active: c.is_active ?? true,
          }))
        );
      })
      .catch(() => setError("Impossible de charger le modèle"))
      .finally(() => setLoading(false));
  }, [templateId]);

  const updateChamp = (index: number, data: Partial<ChampActiviteTemplate>) => {
    setChamps((prev) => prev.map((c, i) => (i === index ? { ...c, ...data } : c)));
  };
  const removeChamp = (index: number) => {
    setChamps((prev) => prev.filter((_, i) => i !== index));
  };
  const addChamp = () => {
    setChamps((prev) => [...prev, { nom: "", label: "", type_champ: "text", required: false, ordre: prev.length, options: [], is_active: true }]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const slug = code.trim() || nom.trim().toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");
    const payload: PayloadActiviteTemplate = {
      nom: nom.trim(),
      code: slug,
      description: description.trim(),
      is_active: isActive,
      ordre,
      pole_ids: poleIds,
      champs: champs.map((c, i) => ({
        nom: c.nom,
        label: c.label,
        type_champ: c.type_champ ?? "text",
        required: c.required ?? false,
        ordre: c.ordre ?? i,
        options: (c.options ?? []) as { value: string; label: string }[],
        is_active: c.is_active ?? true,
      })),
    };
    setSubmitting(true);
    try {
      if (templateId) {
        await updateActiviteTemplate(templateId, payload);
      } else {
        await createActiviteTemplate(payload);
      }
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <p>Chargement…</p>;

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <h3 style={{ marginTop: 0, marginBottom: "1rem" }}>
        {templateId ? "Modifier le modèle d'activité" : "Nouveau modèle d'activité"}
      </h3>
      {error && <div style={styles.error}>{error}</div>}

      <div style={styles.field}>
        <label style={styles.label} htmlFor="tpl-nom">Nom *</label>
        <input id="tpl-nom" type="text" value={nom} onChange={(e) => setNom(e.target.value)} required style={styles.input} />
      </div>
      <div style={styles.field}>
        <label style={styles.label} htmlFor="tpl-code">Code (slug, unique) *</label>
        <input
          id="tpl-code"
          type="text"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="ex: evaluation_grille"
          required
          style={styles.input}
          readOnly={!!templateId}
        />
      </div>
      <div style={styles.field}>
        <label style={styles.label} htmlFor="tpl-desc">Description</label>
        <textarea id="tpl-desc" value={description} onChange={(e) => setDescription(e.target.value)} rows={2} style={styles.input} />
      </div>
      <div style={{ ...styles.row, ...styles.field }}>
        <label style={{ display: "flex", alignItems: "center", cursor: "pointer" }}>
          <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
          <span style={{ marginLeft: "0.5rem" }}>Actif</span>
        </label>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <label style={styles.label}>Ordre</label>
          <input type="number" value={ordre} onChange={(e) => setOrdre(parseInt(e.target.value, 10) || 0)} min={0} style={{ ...styles.input, width: 80 }} />
        </div>
      </div>
      <div style={styles.field}>
        <label style={styles.label}>Pôles assignés</label>
        <select
          multiple
          value={poleIds.map(String)}
          onChange={(e) => {
            const selected = Array.from(e.target.selectedOptions, (o) => Number(o.value));
            setPoleIds(selected);
          }}
          style={styles.select}
        >
          {poles.map((p) => (
            <option key={p.id} value={p.id}>{p.nom}</option>
          ))}
        </select>
        <span style={{ fontSize: "0.85rem", color: "#666" }}>Maintenir Ctrl/Cmd pour sélectionner plusieurs pôles.</span>
      </div>

      <div style={styles.field}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
          <label style={styles.label}>Champs personnalisés</label>
          <button type="button" style={styles.button} onClick={addChamp}>+ Champ</button>
        </div>
        {champs.map((champ, i) => (
          <ChampActiviteTemplateForm
            key={i}
            champ={champ}
            index={i}
            onChange={updateChamp}
            onRemove={removeChamp}
          />
        ))}
      </div>

      <div style={{ ...styles.row, marginTop: "1.25rem", gap: "0.5rem" }}>
        <button type="submit" style={styles.button} disabled={submitting}>
          {submitting ? "Enregistrement…" : templateId ? "Enregistrer" : "Créer"}
        </button>
        {onCancel && (
          <button type="button" style={styles.button} onClick={onCancel}>Annuler</button>
        )}
      </div>
    </form>
  );
}
