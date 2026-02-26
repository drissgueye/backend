# Intégration calendrier – Activités des requêtes (Next.js)

## URL de l’API

- **Base API :** `http://localhost:8000/api` (ou la valeur de `NEXT_PUBLIC_API_URL`)
- **Événements calendrier :** `GET /api/reunions/calendar-events/`

## Authentification

L’endpoint exige un utilisateur connecté (JWT). Envoie le token dans l’en-tête :

```
Authorization: Bearer <access_token>
```

## Paramètres de requête (optionnels)

| Paramètre     | Description |
|--------------|-------------|
| `start`      | Début de la plage (ISO datetime, ex. `2026-02-01T00:00:00Z`) |
| `end`        | Fin de la plage (ISO datetime) |
| `event_type` | `reunion` = uniquement réunions, `activite` = uniquement activités requêtes |
| `debug`      | `1` pour inclure des infos de debug dans la réponse |

## Format de réponse

Un tableau d’événements. Chaque événement contient au minimum :

- `id` : identifiant (ex. `activite-123`, `reunion-456`)
- `event_type` : `"activite"` ou `"reunion"`
- `title` : titre à afficher
- `start` : début (ISO datetime)
- `end` : fin (ISO datetime)

### Événements de type `activite` (activités des requêtes)

En plus des champs communs :

- `type_activite`, `type_activite_display`
- `statut`, `statut_display`
- `requete_id`, `numero_reference`
- `description`, `activite_id`

### Événements de type `reunion`

- `dossier_id`, `dossier_numero`, `lieu`, `ordre_du_jour`, `reunion_id`, etc.

## Exemple d’appel (JavaScript)

```ts
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const token = localStorage.getItem('access_token'); // ou votre store auth

const start = '2026-02-01T00:00:00Z';
const end   = '2026-02-28T23:59:59Z';

const res = await fetch(
  `${apiUrl}/reunions/calendar-events/?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}&event_type=activite`,
  {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  }
);
const events = await res.json();
```

## Côté backend

- CORS autorise toutes les origines (`CORS_ALLOW_ALL_ORIGINS = True`), donc `http://localhost:8080` est accepté.
- Les activités affichées sont celles des requêtes visibles par l’utilisateur connecté (pôle, délégué, etc.).

## Fichiers d’exemple

Le dossier `frontend_example/calendar/` contient une page Next.js (App Router) et un hook réutilisable pour afficher les activités des requêtes dans le calendrier. À copier ou adapter dans votre projet Next.js.
