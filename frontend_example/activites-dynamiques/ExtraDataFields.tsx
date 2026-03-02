"use client";

import React from "react";
import type { ChampActiviteTemplate, OptionChoice } from "./types";

const styles: Record<string, React.CSSProperties> = {
  field: { marginBottom: "1rem" },
  label: { display: "block", fontWeight: 600, marginBottom: "0.35rem", fontSize: "0.9rem" },
  input: { width: "100%", maxWidth: 400, padding: "0.5rem", fontSize: "1rem" },
  checkbox: { width: "auto", marginRight: "0.5rem" },
};

interface ExtraDataFieldsProps {
  champs: ChampActiviteTemplate[];
  value: Record<string, unknown>;
  onChange: (value: Record<string, unknown>) => void;
  disabled?: boolean;
}

export function ExtraDataFields({ champs, value, onChange, disabled }: ExtraDataFieldsProps) {
  const update = (nom: string, val: unknown) => {
    onChange({ ...value, [nom]: val });
  };

  if (!champs.length) return null;

  return (
    <div style={{ marginTop: "1rem" }}>
      <strong style={{ display: "block", marginBottom: "0.75rem" }}>Champs personnalisés</strong>
      {champs.map((champ) => {
        const val = value[champ.nom];
        const required = champ.required;
        const label = required ? `${champ.label} *` : champ.label;

        switch (champ.type_champ) {
          case "text":
            return (
              <div key={champ.nom} style={styles.field}>
                <label style={styles.label} htmlFor={`extra-${champ.nom}`}>
                  {label}
                </label>
                <input
                  id={`extra-${champ.nom}`}
                  type="text"
                  value={typeof val === "string" ? val : ""}
                  onChange={(e) => update(champ.nom, e.target.value)}
                  disabled={disabled}
                  style={styles.input}
                />
              </div>
            );
          case "textarea":
            return (
              <div key={champ.nom} style={styles.field}>
                <label style={styles.label} htmlFor={`extra-${champ.nom}`}>
                  {label}
                </label>
                <textarea
                  id={`extra-${champ.nom}`}
                  value={typeof val === "string" ? val : ""}
                  onChange={(e) => update(champ.nom, e.target.value)}
                  disabled={disabled}
                  rows={3}
                  style={{ ...styles.input, minHeight: 80 }}
                />
              </div>
            );
          case "number":
            return (
              <div key={champ.nom} style={styles.field}>
                <label style={styles.label} htmlFor={`extra-${champ.nom}`}>
                  {label}
                </label>
                <input
                  id={`extra-${champ.nom}`}
                  type="number"
                  value={val !== undefined && val !== null && val !== "" ? String(val) : ""}
                  onChange={(e) => {
                    const v = e.target.value;
                    update(champ.nom, v === "" ? "" : Number(v));
                  }}
                  disabled={disabled}
                  style={styles.input}
                />
              </div>
            );
          case "date":
            return (
              <div key={champ.nom} style={styles.field}>
                <label style={styles.label} htmlFor={`extra-${champ.nom}`}>
                  {label}
                </label>
                <input
                  id={`extra-${champ.nom}`}
                  type="date"
                  value={typeof val === "string" ? val.slice(0, 10) : ""}
                  onChange={(e) => update(champ.nom, e.target.value)}
                  disabled={disabled}
                  style={styles.input}
                />
              </div>
            );
          case "datetime":
            return (
              <div key={champ.nom} style={styles.field}>
                <label style={styles.label} htmlFor={`extra-${champ.nom}`}>
                  {label}
                </label>
                <input
                  id={`extra-${champ.nom}`}
                  type="datetime-local"
                  value={typeof val === "string" ? val.slice(0, 16) : ""}
                  onChange={(e) => update(champ.nom, e.target.value ? `${e.target.value}:00` : "")}
                  disabled={disabled}
                  style={styles.input}
                />
              </div>
            );
          case "boolean":
            return (
              <div key={champ.nom} style={styles.field}>
                <label style={{ display: "flex", alignItems: "center", cursor: disabled ? "default" : "pointer" }}>
                  <input
                    type="checkbox"
                    checked={Boolean(val)}
                    onChange={(e) => update(champ.nom, e.target.checked)}
                    disabled={disabled}
                    style={styles.checkbox}
                  />
                  <span style={styles.label}>{label}</span>
                </label>
              </div>
            );
          case "choice": {
            const options = (champ.options || []) as OptionChoice[];
            return (
              <div key={champ.nom} style={styles.field}>
                <label style={styles.label} htmlFor={`extra-${champ.nom}`}>
                  {label}
                </label>
                <select
                  id={`extra-${champ.nom}`}
                  value={typeof val === "string" ? val : ""}
                  onChange={(e) => update(champ.nom, e.target.value || null)}
                  disabled={disabled}
                  style={styles.input}
                >
                  <option value="">— Choisir —</option>
                  {options.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label || opt.value}
                    </option>
                  ))}
                </select>
              </div>
            );
          }
          case "file":
            return (
              <div key={champ.nom} style={styles.field}>
                <label style={styles.label} htmlFor={`extra-${champ.nom}`}>
                  {label}
                </label>
                <input
                  id={`extra-${champ.nom}`}
                  type="text"
                  placeholder="Référence fichier (upload géré ailleurs)"
                  value={typeof val === "string" ? val : ""}
                  onChange={(e) => update(champ.nom, e.target.value)}
                  disabled={disabled}
                  style={styles.input}
                />
              </div>
            );
          default:
            return (
              <div key={champ.nom} style={styles.field}>
                <label style={styles.label} htmlFor={`extra-${champ.nom}`}>
                  {label}
                </label>
                <input
                  id={`extra-${champ.nom}`}
                  type="text"
                  value={val != null ? String(val) : ""}
                  onChange={(e) => update(champ.nom, e.target.value)}
                  disabled={disabled}
                  style={styles.input}
                />
              </div>
            );
        }
      })}
    </div>
  );
}
