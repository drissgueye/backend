# Activités dynamiques — Frontend Next.js

Module réutilisable pour gérer les **modèles d'activité** (admin) et les **activités sur les requêtes** (workflow) avec champs personnalisés, aligné sur l’API backend Django/DRF.

## Où accéder — Liens à créer dans votre app

Aucun lien n'existe par défaut : il faut **créer les routes** puis **ajouter les liens** dans votre menu ou layout.

| Ce que vous voulez faire | URL à créer (exemple) | Où mettre le lien |
|--------------------------|------------------------|-------------------|
| **Gérer les modèles d'activité** (admin) | `/admin/activite-templates` | Menu admin ou sidebar : « Modèles d'activité » → cette URL |
| **Voir / ajouter les activités d'une requête** | `/requetes/[id]` (détail requête) | La section activités s'affiche **dans** la page détail requête (pas une URL à part) |

### 1. Lien « Modèles d'activité » (admin)

- **Route** : page qui rend `<ActiviteTemplateList />`, ex. `app/admin/activite-templates/page.tsx`.
- **URL** : `http://localhost:3000/admin/activite-templates`
- **Dans le menu** : ajoutez un lien (ex. dans le layout admin) : `<Link href="/admin/activite-templates">Modèles d'activité</Link>`

### 2. Activités d'une requête

- Pas d'URL dédiée : les activités sont **dans la page détail requête**.
- **URL** : `http://localhost:3000/requetes/42` (id = 42). Affichez `<SectionRequeteActivites />` sur cette page.
- L'utilisateur y accède en cliquant sur une requête dans la liste.

Voir aussi **LIENS_ACCES.md** dans ce dossier pour le détail.

---

## Prérequis

- `NEXT_PUBLIC_API_URL` pointant vers l’API (ex. `http://localhost:8000/api`)
- Token JWT dans `localStorage` sous la clé `access_token` après connexion

## Fichiers

| Fichier | Rôle |
|--------|------|
| `types.ts` | Types (ActiviteTemplate, ChampActiviteTemplate, ActiviteRequete, payloads) |
| `api.ts` | Client API (templates, activites-disponibles, activités requête, pôles) |
| `ExtraDataFields.tsx` | Champs dynamiques selon le template (text, date, choice, etc.) |
| `ActiviteRequeteForm.tsx` | Formulaire « Ajouter une activité » (modèle ou type legacy + extra_data) |
| `ChampActiviteTemplateForm.tsx` | Ligne de champ dans le formulaire admin (nom, type, options) |
| `ActiviteTemplateForm.tsx` | Formulaire create/edit d’un modèle d’activité (champs + pôles) |
| `ActiviteTemplateList.tsx` | Liste des modèles + créer / modifier / désactiver |
| `SectionRequeteActivites.tsx` | Bloc « Activités planifiées » pour une requête (liste + formulaire) |
| `page-admin-templates.tsx` | Exemple de page admin modèles d’activité |

## Intégration dans votre app Next.js

### 1. Copier le module

Copiez le dossier `activites-dynamiques` dans votre projet (par ex. `src/components/activites-dynamiques` ou `app/_components/activites-dynamiques`).

### 2. Page admin (modèles d’activité)

Créer une page réservée aux admins, par exemple :

- **App Router** : `app/admin/activite-templates/page.tsx`

```tsx
"use client";
import { ActiviteTemplateList } from "@/components/activites-dynamiques/ActiviteTemplateList";

export default function AdminActiviteTemplatesPage() {
  return (
    <div className="container py-6">
      <h1>Modèles d'activité</h1>
      <ActiviteTemplateList />
    </div>
  );
}
```

Protéger la route (layout ou middleware) pour que seuls les rôles admin y aient accès.

### 3. Détail d’une requête (activités)

Sur la page de détail d’une requête, afficher la section activités avec le formulaire dynamique :

- **App Router** : `app/requetes/[id]/page.tsx` (ou équivalent)

```tsx
"use client";
import { SectionRequeteActivites } from "@/components/activites-dynamiques/SectionRequeteActivites";

// Dans votre composant, une fois que vous avez requete.id et requete.pole (ou requete.pole_id) :
<SectionRequeteActivites
  requeteId={requete.id}
  poleId={requete.pole ?? requete.pole_id}
  onRefreshRequete={() => refetchRequete()}
/>
```

Le formulaire « Ajouter une activité » utilise automatiquement `GET /api/poles/<poleId>/activites-disponibles/` pour n’afficher que les modèles assignés au pôle de la requête, puis envoie `activite_template_id` et `extra_data` à `POST /api/requetes/<id>/activites/`.

### 4. Types et API

Si vous centralisez vos types ou votre client API, vous pouvez réexporter ou fusionner :

- `types.ts` → à garder aligné avec l’API (ActiviteTemplate, champs, ActiviteRequete, payloads).
- `api.ts` → à adapter si vous utilisez un client global (axios, fetch wrapper avec intercepteur auth).

## Workflow côté front

1. **Admin** : Création/édition de modèles d’activité (nom, code, champs personnalisés, pôles assignés).
2. **Requête** : Pour une requête d’un pôle donné, appel à `GET /poles/<poleId>/activites-disponibles/` pour obtenir les modèles disponibles.
3. **Création d’activité** : L’utilisateur choisit un modèle (ou un type legacy), remplit titre, date, et les champs personnalisés ; envoi de `activite_template_id` + `extra_data` (ou `type_activite` pour le legacy).
4. **Affichage** : Les activités existantes affichent `type_activite_display` et `extra_data` ; la section « Activités planifiées » permet de marquer terminée ou d’annuler.

## Dépendances

Aucune dépendance spécifique : React, `fetch`, et le reste du projet Next.js suffisent.
