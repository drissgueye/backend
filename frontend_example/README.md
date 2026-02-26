# Exemple d’intégration calendrier (Next.js)

Ce dossier contient du code prêt à l’emploi pour afficher les **activités des requêtes** (et les réunions) dans votre calendrier Next.js sur `http://localhost:8080/calendar`.

## Fichiers

- **`calendar/types.ts`** – Types TypeScript pour les événements API.
- **`calendar/useCalendarEvents.ts`** – Hook React qui appelle `GET /api/reunions/calendar-events/` avec le token JWT.
- **`calendar/page.tsx`** – Page calendrier (liste des événements par mois, filtre activités / réunions).

## Intégration dans votre projet Next.js

1. **Variables d’environnement**  
   Dans `.env.local` :
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```
   (Remplacez par l’URL de votre backend si différente.)

2. **Authentification**  
   Après connexion, enregistrez le token JWT :
   ```ts
   localStorage.setItem("access_token", accessToken);
   ```
   Le hook lit ce token pour appeler l’API. Si vous utilisez un autre stockage (cookie, contexte), adaptez `getAccessToken()` dans `useCalendarEvents.ts`.

3. **Copie des fichiers**
   - Soit copier tout le dossier `calendar/` dans votre app (par ex. `src/app/calendar/` ou `app/calendar/` en App Router).
   - Soit :
     - Mettre `types.ts` et `useCalendarEvents.ts` dans `lib/` ou `hooks/`.
     - Mettre le contenu de `page.tsx` dans `app/calendar/page.tsx` et adapter les imports.

4. **Page calendrier**  
   En App Router, votre route est déjà `app/calendar/page.tsx`. Remplacez son contenu par celui de `calendar/page.tsx` (en corrigeant les imports si vous avez déplacé `useCalendarEvents` et `types`).

## Option : utiliser FullCalendar

Si vous utilisez déjà un calendrier visuel (ex. `@fullcalendar/react`) :

```ts
import { useCalendarEvents, toFullCalendarEvents } from "@/lib/useCalendarEvents";

// Dans votre composant :
const { events, loading } = useCalendarEvents(range, { eventType: "activite" });
const fullCalendarEvents = toFullCalendarEvents(events);

<FullCalendar
  events={fullCalendarEvents}
  // ...
/>
```

## API utilisée

- **GET** `/api/reunions/calendar-events/?start=...&end=...&event_type=activite`  
  Retourne la liste des événements (activités des requêtes si `event_type=activite`).  
  Voir `docs/CALENDRIER_INTEGRATION.md` pour les détails.
