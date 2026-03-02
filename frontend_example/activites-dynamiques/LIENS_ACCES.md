# Liens d’accès — Activités dynamiques

## Où cliquer pour y accéder ?

### 1. Modèles d’activité (admin)

**URL à utiliser dans le navigateur (une fois la route créée dans votre app Next.js) :**

```
/admin/activite-templates
```

Exemple : `http://localhost:3000/admin/activite-templates`

**Pour que ce lien existe**, vous devez :

1. Créer la page dans votre app Next.js, par exemple :
   - Fichier : `app/admin/activite-templates/page.tsx`
   - Contenu : importer et afficher `<ActiviteTemplateList />` (voir README du module).

2. Ajouter un lien dans votre menu ou layout (sidebar, navbar admin) :
   - Texte du lien : **« Modèles d’activité »** (ou « Activités dynamiques »).
   - Cible : **`/admin/activite-templates`**.

Exemple de lien (Next.js App Router) :

```tsx
import Link from "next/link";

<Link href="/admin/activite-templates">Modèles d'activité</Link>
```

---

### 2. Activités d’une requête (liste + ajout)

Il n’y a **pas d’URL séparée** pour « les activités ». Elles sont affichées **sur la page de détail d’une requête**.

**URL de la page détail requête (exemple) :**

```
/requetes/42
```

(Remplacez `42` par l’id de la requête.)

**Pour que la section « Activités planifiées » s’affiche :**

1. Sur votre page détail requête (ex. `app/requetes/[id]/page.tsx`), ajoutez le composant :
   ```tsx
   <SectionRequeteActivites
     requeteId={requete.id}
     poleId={requete.pole ?? requete.pole_id}
     onRefreshRequete={() => refetchRequete()}
   />
   ```
2. L’utilisateur ouvre une requête depuis la liste des requêtes (lien du type « Voir » ou « Requête REQ-2026-00042 » qui mène vers `/requetes/42`). La section activités apparaît sur cette même page.

---

## Récapitulatif

| Action | Où aller |
|--------|----------|
| Créer / modifier / désactiver des modèles d’activité | Menu → **Modèles d’activité** → `/admin/activite-templates` |
| Voir ou ajouter des activités sur une requête | Liste requêtes → cliquer sur une requête → page détail (`/requetes/[id]`) ; la section « Activités planifiées » est sur cette page |
