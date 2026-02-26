# Conditionnement – Module Communication

Module géré par le **pôle Communication** (`Pole` avec `code="communication"`).

## Qui peut faire quoi

| Action | Qui |
|--------|-----|
| **Voir la liste / détail** | Tout utilisateur authentifié. Les publications affichées sont filtrées selon la **visibilité** (voir ci‑dessous). |
| **Créer / modifier / supprimer** | Uniquement **admin** (staff/superuser) ou **membres du pôle Communication** (chef du pôle ou membre via `PoleMembership`). |

- Endpoint de vérification : `GET /api/communications/can_manage/` → `{ "can_manage": true/false }`.
- Les créations ont l’`auteur` fixé à l’utilisateur connecté.

## Qui voit quoi (liste)

La liste renvoyée par `GET /api/communications/` est filtrée selon le profil de l’utilisateur :

| Visibilité de la publication | Visible par |
|------------------------------|-------------|
| **global** | Tous les utilisateurs authentifiés. |
| **company** | Utilisateurs dont le **profil.entreprise** est égal à `entreprise_cible` de la publication. |
| **pole** | Utilisateurs qui sont **membres du pôle** correspondant à `pole_cible` (chef ou `PoleMembership`). |

- Les **admins** voient toutes les publications, sans filtre de visibilité.

## API

- `GET /api/communications/` – Liste (filtrée par visibilité).
- `GET /api/communications/:id/` – Détail d’une publication.
- `GET /api/communications/can_manage/` – Droits de création/édition/suppression.
- `POST /api/communications/` – Création (pôle Communication ou admin).
- `PUT/PATCH /api/communications/:id/` – Modification (pôle Communication ou admin).
- `DELETE /api/communications/:id/` – Suppression (pôle Communication ou admin).

Paramètres de filtrage liste : `search`, `visibilite`, `entreprise_cible`, `pole_cible`, `ordering`.
