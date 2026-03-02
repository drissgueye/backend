"use client";

import React from "react";
import { ActiviteTemplateList } from "./ActiviteTemplateList";

/**
 * Page admin : gestion des modèles d'activité (CRUD).
 * À placer dans votre app Next.js par exemple :
 *   app/admin/activite-templates/page.tsx
 * et protéger par un layout ou middleware (rôle admin).
 */
export default function PageAdminActiviteTemplates() {
  return (
    <div style={{ padding: "1.5rem", maxWidth: 900, margin: "0 auto" }}>
      <h1 style={{ marginBottom: "1rem" }}>Modèles d'activité (admin)</h1>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        Créez des modèles d'activité avec champs personnalisés et assignez-les aux pôles.
        Lors du traitement d'une requête, seules les activités assignées au pôle de la requête seront proposées.
      </p>
      <ActiviteTemplateList />
    </div>
  );
}
