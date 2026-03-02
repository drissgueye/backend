# Activités dynamiques — Exemples de payloads

## 1. Créer un modèle d'activité (admin)

**POST** `/api/activite-templates/`  
Rôle : Super Admin / Administrateur.

```json
{
  "nom": "Évaluation grille salariale",
  "code": "evaluation_grille",
  "description": "Suivi de l'évaluation des grilles salariales par secteur.",
  "is_active": true,
  "ordre": 10,
  "champs": [
    {
      "nom": "secteur_ou_branche",
      "label": "Secteur / branche",
      "type_champ": "text",
      "required": false,
      "ordre": 0,
      "options": [],
      "is_active": true
    },
    {
      "nom": "date_limite",
      "label": "Date limite de remise",
      "type_champ": "date",
      "required": true,
      "ordre": 1,
      "options": [],
      "is_active": true
    }
  ],
  "pole_ids": [1, 2]
}
```

Avec un champ de type **liste de choix** :

```json
{
  "nom": "Suivi primes ou avantages",
  "code": "suivi_primes",
  "description": "",
  "is_active": true,
  "ordre": 20,
  "champs": [
    {
      "nom": "type_prime",
      "label": "Type (prime, avantage, etc.)",
      "type_champ": "choice",
      "required": true,
      "ordre": 0,
      "options": [
        { "value": "prime", "label": "Prime" },
        { "value": "avantage", "label": "Avantage en nature" },
        { "value": "autre", "label": "Autre" }
      ],
      "is_active": true
    },
    {
      "nom": "reference",
      "label": "Référence accord / texte",
      "type_champ": "text",
      "required": false,
      "ordre": 1,
      "options": [],
      "is_active": true
    }
  ],
  "pole_ids": [1]
}
```

Types de champs possibles : `text`, `textarea`, `number`, `date`, `datetime`, `boolean`, `file`, `choice`.

---

## 2. Lister les activités disponibles pour un pôle (workflow)

**GET** `/api/poles/<pole_id>/activites-disponibles/`

Réponse (exemple) :

```json
[
  {
    "id": 1,
    "nom": "Évaluation grille salariale",
    "code": "evaluation_grille",
    "description": "Suivi de l'évaluation des grilles salariales par secteur.",
    "is_active": true,
    "ordre": 10,
    "champs": [
      {
        "id": 1,
        "nom": "secteur_ou_branche",
        "label": "Secteur / branche",
        "type_champ": "text",
        "type_champ_display": "Texte",
        "required": false,
        "ordre": 0,
        "options": [],
        "is_active": true
      },
      {
        "id": 2,
        "nom": "date_limite",
        "label": "Date limite de remise",
        "type_champ": "date",
        "type_champ_display": "Date",
        "required": true,
        "ordre": 1,
        "options": [],
        "is_active": true
      }
    ],
    "pole_ids": [1, 2],
    "created_at": "2026-02-27T10:00:00Z",
    "updated_at": "2026-02-27T10:00:00Z"
  }
]
```

À utiliser côté front pour n’afficher que les activités proposables lors du traitement d’une requête de ce pôle.

---

## 3. Créer une activité sur une requête (avec template)

**POST** `/api/requetes/<requete_id>/activites/`

Avec **modèle d’activité dynamique** (`activite_template_id` + `extra_data`) :

```json
{
  "requete_id": 42,
  "activite_template_id": 1,
  "titre": "Éval. grille Q1 2026",
  "description": "Point avec la direction sur la branche assurance.",
  "date_planifiee": "2026-03-15T14:00:00Z",
  "extra_data": {
    "secteur_ou_branche": "Assurance",
    "date_limite": "2026-03-31"
  }
}
```

Avec **liste de choix** dans `extra_data` :

```json
{
  "requete_id": 42,
  "activite_template_id": 2,
  "titre": "Suivi prime annuelle",
  "date_planifiee": "2026-04-01T09:00:00Z",
  "extra_data": {
    "type_prime": "prime",
    "reference": "Accord 2025 - article 12"
  }
}
```

Sans template (activité « legacy », comme avant) :

```json
{
  "requete_id": 42,
  "type_activite": "call",
  "titre": "Appel travailleur",
  "date_planifiee": "2026-02-28T10:00:00Z"
}
```

Règles de validation pour `extra_data` lorsque `activite_template_id` est fourni :

- Champs marqués **required** doivent être présents et non vides.
- **Types** : texte (string), date (AAAA-MM-JJ), datetime (ISO 8601), nombre (number), boolean, choice (valeur dans `options[].value`).
- Pour **choice**, la valeur envoyée doit être l’une des `value` définies dans le template.

---

## 4. Mettre à jour une activité (dont champs personnalisés)

**PATCH** `/api/requetes/<requete_id>/activites/<activite_id>/`

Exemple (statut + extra_data) :

```json
{
  "statut": "completed",
  "date_realisation": "2026-03-15T15:30:00Z",
  "commentaire": "Accord obtenu sur la date limite.",
  "extra_data": {
    "secteur_ou_branche": "Assurance",
    "date_limite": "2026-04-15"
  }
}
```

---

## 5. Filtrer les modèles d’activité par pôle

**GET** `/api/activite-templates/?pole=1`  
Retourne uniquement les modèles assignés au pôle d’id 1 (même usage workflow que `activites-disponibles`).

**GET** `/api/activite-templates/?is_active=true`  
Retourne uniquement les modèles actifs.
