"use client";

import React from "react";
import type { ChampActiviteTemplate, TypeChampActivite, OptionChoice } from "./types";
import { TYPE_CHAMP_ACTIVITE } from "./types";

const styles: Record<string, React.CSSProperties> = {
  row: { display: "grid", gridTemplateColumns: "1fr 1fr 120px 80px 1fr auto", gap: "0.5rem", alignItems: "start", marginBottom: "0.5rem" },
  input: { padding: "0.4rem", fontSize: "0.9rem" },
  select: { padding: "0.4rem", fontSize: "0.9rem" },
  checkbox: { marginTop: "0.5rem" },
  btn: { padding: "0.4rem 0.75rem", cursor: "pointer", fontSize: "0.9rem" },
};

interface ChampActiviteTemplateFormProps {
  champ: Partial<ChampActiviteTemplate>;
  index: number;
  onChange: (index: number, data: Partial<ChampActiviteTemplate>) => void;
  onRemove: (index: number) => void;
}

export function ChampActiviteTemplateForm({ champ, index, onChange, onRemove }: ChampActiviteTemplateFormProps) {
  const options = (champ.options || []) as OptionChoice[];
  const addOption = () => {
    const next = [...options, { value: "", label: "" }];
    onChange(index, { ...champ, options: next });
  };
  const updateOption = (i: number, key: "value" | "label", val: string) => {
    const next = options.map((o, j) => (j === i ? { ...o, [key]: val } : o));
    onChange(index, { ...champ, options: next });
  };
  const removeOption = (i: number) => {
    const next = options.filter((_, j) => j !== i);
    onChange(index, { ...champ, options: next });
  };

  return (
    <div style={{ border: "1px solid #ddd", padding: "0.75rem", borderRadius: 6, marginBottom: "0.75rem", background: "#fff" }}>
      <div style={styles.row}>
        <input
          placeholder="Nom (slug)"
          value={champ.nom ?? ""}
          onChange={(e) => onChange(index, { ...champ, nom: e.target.value })}
          style={styles.input}
        />
        <input
          placeholder="Label"
          value={champ.label ?? ""}
          onChange={(e) => onChange(index, { ...champ, label: e.target.value })}
          style={styles.input}
        />
        <select
          value={champ.type_champ ?? "text"}
          onChange={(e) => onChange(index, { ...champ, type_champ: e.target.value as TypeChampActivite })}
          style={styles.select}
        >
          {TYPE_CHAMP_ACTIVITE.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <label style={{ display: "flex", alignItems: "center", paddingTop: "0.5rem" }}>
          <input
            type="checkbox"
            checked={champ.required ?? false}
            onChange={(e) => onChange(index, { ...champ, required: e.target.checked })}
            style={styles.checkbox}
          />
          <span style={{ marginLeft: "0.25rem", fontSize: "0.85rem" }}>Requis</span>
        </label>
        <input
          type="number"
          placeholder="Ordre"
          value={champ.ordre ?? index}
          onChange={(e) => onChange(index, { ...champ, ordre: parseInt(e.target.value, 10) || 0 })}
          style={styles.input}
          min={0}
        />
        <button type="button" style={styles.btn} onClick={() => onRemove(index)}>
          Suppr.
        </button>
      </div>
      {champ.type_champ === "choice" && (
        <div style={{ marginTop: "0.5rem", paddingTop: "0.5rem", borderTop: "1px solid #eee" }}>
          <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Options (value / label)</span>
          {options.map((opt, i) => (
            <div key={i} style={{ display: "flex", gap: "0.5rem", marginTop: "0.35rem" }}>
              <input
                placeholder="value"
                value={opt.value}
                onChange={(e) => updateOption(i, "value", e.target.value)}
                style={{ ...styles.input, flex: 1 }}
              />
              <input
                placeholder="label"
                value={opt.label}
                onChange={(e) => updateOption(i, "label", e.target.value)}
                style={{ ...styles.input, flex: 1 }}
              />
              <button type="button" style={styles.btn} onClick={() => removeOption(i)}>−</button>
            </div>
          ))}
          <button type="button" style={{ ...styles.btn, marginTop: "0.35rem" }} onClick={addOption}>
            + Option
          </button>
        </div>
      )}
    </div>
  );
}
