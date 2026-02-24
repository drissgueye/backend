# Guide : afficher les activités avec leur date dans le calendrier

## 1. Lancer le backend (API Django)

Ouvrez un terminal dans le dossier du projet et exécutez :

```powershell
cd c:\wamp64\www\sites\cntsNew\backendCnts
.\.venv\Scripts\Activate.ps1
# Si le venv est dans le dossier parent :
# ..\.venv\Scripts\Activate.ps1
python manage.py runserver 127.0.0.1:8000
```

L’API sera disponible sur **http://127.0.0.1:8000**.

---

## 2. Lancer le frontend (React / Vite)

Dans un **autre** terminal :

```powershell
cd c:\wamp64\www\sites\cntsNew\cnts
npm run dev
```

Ouvrez ensuite **http://localhost:8080** dans le navigateur.

---

## 3. Vérifier le calendrier

1. Connectez-vous à l’application.
2. Allez sur **Calendrier** (http://localhost:8080/calendar).
3. Pour chaque activité dans la grille, vous devriez voir :
   - **Ligne 1 :** icône + titre de l’activité
   - **Ligne 2 :** **Date : 25 févr. 14:30** (date et heure)
   - **Ligne 3 :** Requête [référence]

4. Si vous ne voyez **aucune activité** :
   - Regardez le texte sous le titre : « — X événement(s) ce mois ». Si X = 0, il n’y a pas d’activités planifiées pour le mois affiché.
   - Créez une activité planifiée depuis une requête (onglet Suivi d’activités) avec une date dans le mois courant.
   - Ouvrez les **Outils de développement** (F12) → onglet **Réseau**, rechargez la page, cherchez la requête `calendar-events` et vérifiez la réponse (liste d’événements ou erreur 403/500).

---

## 4. Vérifier que l’API renvoie des événements

Une fois connecté, vous pouvez tester l’API avec un token :

1. F12 → **Application** (ou Stockage) → **Local Storage** → récupérez la valeur de `cnts.accessToken`.
2. Dans un terminal (avec curl ou PowerShell) :

```powershell
$token = "COLLEZ_VOTRE_TOKEN_ICI"
$start = [DateTime]::UtcNow.Date.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
$end = [DateTime]::UtcNow.AddMonths(1).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/reunions/calendar-events/?start=$start&end=$end&debug=1" -Headers @{ Authorization = "Bearer $token" }
```

Si la réponse contient un tableau `events` avec des éléments, le calendrier peut les afficher. S’il est vide, créez des activités planifiées sur des requêtes.

---

## Résumé des modifications (déjà en place)

- Dans la **grille du mois** : chaque activité affiche une ligne **« Date : 25 févr. 14:30 »**.
- Dans le **détail du jour** (clic sur une date) : **« Date : 25 févr. 2026 à 14:30 »**.
- Si après avoir suivi ce guide vous ne voyez toujours aucun changement, faites un **rechargement forcé** du calendrier : **Ctrl+F5** dans le navigateur.
