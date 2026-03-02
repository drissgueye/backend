# Intégrer le module activités dynamiques dans le projet Next.js « cnts »

Votre projet **cnts** existe déjà. Ce guide décrit quoi copier et où ajouter les liens pour avoir le calendrier, les modèles d’activité et les activités sur les requêtes.

---

## 1. Emplacement des fichiers dans « cnts »

À partir de la racine de votre projet **cnts** (là où se trouve `package.json`), créez ou copiez comme suit.

### Option A – Tout dans `src/` (si vous avez un dossier `src/`)

```
cnts/
  src/
    app/                    # ou pages/ selon votre structure
      admin/
        activite-templates/
          page.tsx          # → voir section 2
      calendar/
        page.tsx            # → voir section 2
      requetes/
        [id]/
          page.tsx          # → ajouter SectionRequeteActivites (section 3)
    components/
      activites-dynamiques/ # → copier tout le dossier frontend_example/activites-dynamiques
    lib/
      calendar/             # → copier types.ts + useCalendarEvents.ts (frontend_example/calendar)
        types.ts
        useCalendarEvents.ts
```

### Option B – Sans `src/` (App Router à la racine)

```
cnts/
  app/
    admin/
      activite-templates/
        page.tsx
    calendar/
      page.tsx
    requetes/
      [id]/
        page.tsx
  components/
    activites-dynamiques/   # copier tout le dossier
  lib/
    calendar/
      types.ts
      useCalendarEvents.ts
```

**À copier depuis ce dépôt (backendCnts) :**

- Dossier **`frontend_example/activites-dynamiques/`**  
  → en entier dans **`cnts/components/activites-dynamiques/`** (ou `cnts/src/components/activites-dynamiques/`).

- Fichiers **`frontend_example/calendar/types.ts`** et **`frontend_example/calendar/useCalendarEvents.ts`**  
  → dans **`cnts/lib/calendar/`** (ou `cnts/src/lib/calendar/`).

- Contenu de **`frontend_example/calendar/page.tsx`**  
  → pour créer la page **`cnts/app/calendar/page.tsx`** (ou `cnts/src/app/calendar/page.tsx`) en adaptant les imports (voir section 2).

---

## 2. Créer les pages dans « cnts »

### Page Calendrier – `app/calendar/page.tsx` (ou `src/app/calendar/page.tsx`)

Créez la page et utilisez le contenu de `frontend_example/calendar/page.tsx` en modifiant les imports :

- `import { useCalendarEvents } from "./useCalendarEvents"`  
  → `import { useCalendarEvents } from "@/lib/calendar/useCalendarEvents";`  
  (ou `@/src/lib/calendar/useCalendarEvents` selon votre `tsconfig`)

- `import { isActiviteEvent } from "./types"`  
  → `import { isActiviteEvent } from "@/lib/calendar/types";`

### Page Admin – Modèles d’activité – `app/admin/activite-templates/page.tsx`

```tsx
"use client";

import { ActiviteTemplateList } from "@/components/activites-dynamiques/ActiviteTemplateList";

export default function AdminActiviteTemplatesPage() {
  return (
    <div className="container py-6">
      <h1>Modèles d&apos;activité</h1>
      <ActiviteTemplateList />
    </div>
  );
}
```

(Adaptez `@/components/` si vos composants sont dans `src/components/`.)

---

## 3. Page détail requête – `app/requetes/[id]/page.tsx`

Dans la page où vous affichez une requête (détail), ajoutez la section activités. Vous devez avoir l’**id** de la requête et le **pole_id** (ou `requete.pole`).

Exemple si vous chargez déjà la requête :

```tsx
import { SectionRequeteActivites } from "@/components/activites-dynamiques/SectionRequeteActivites";

// Dans votre composant, après avoir la requête (ex. requete = data) :
<SectionRequeteActivites
  requeteId={requete.id}
  poleId={requete.pole ?? requete.pole_id}
  onRefreshRequete={() => refetch()}
/>
```

Si votre détail requête est ailleurs (ex. `app/requetes/[id]/page.tsx` ou `pages/requete/[id].tsx`), placez ce bloc au bon endroit dans le même fichier.

---

## 4. Lien dans le menu / layout (accès aux pages)

Dans le composant où vous affichez le **menu** ou la **navigation** (layout, sidebar, navbar), ajoutez un lien vers les modèles d’activité (et optionnellement vers le calendrier et les requêtes).

Exemple avec Next.js `Link` :

```tsx
import Link from "next/link";

// Dans votre nav / sidebar :
<Link href="/admin/activite-templates">Modèles d&apos;activité</Link>
<Link href="/calendar">Calendrier</Link>
<Link href="/requetes">Requêtes</Link>
```

- **Modèles d’activité** → `/admin/activite-templates`
- **Calendrier** → `/calendar`
- **Détail d’une requête** → `/requetes/[id]` (la section activités est sur cette page)

---

## 5. Variables d’environnement

Dans le projet **cnts**, fichier **`.env.local`** :

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

(Adresse de votre backend Django.)

---

## 6. Récapitulatif des URLs dans « cnts »

| Ce que vous voulez | URL dans cnts |
|--------------------|----------------|
| Modèles d’activité (admin) | `/admin/activite-templates` |
| Calendrier | `/calendar` |
| Détail d’une requête (avec activités) | `/requetes/42` (ex. id = 42) |

Une fois les fichiers copiés, les pages créées et le lien « Modèles d’activité » ajouté dans votre menu, tout sera accessible dans le projet **cnts** sans créer un autre projet.
