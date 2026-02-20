# Processeurs métier par pôle (Strategy Pattern)

Chaque pôle dispose d'une **logique métier dédiée** sans `if/elif` sur le nom du pôle.

## Structure

- **`base.py`** : `BasePoleProcessor` (abstrait), actions disponibles, exécution, transitions.
- **`types.py`** : `ActionDefinition`, `ActionResult`, `TransitionCheck`.
- **`exceptions.py`** : `PoleProcessorError`, `PoleProcessorValidationError`, etc.
- **`factory.py`** : `get_pole_processor(pole)` → processeur selon `pole.code`.
- **Processeurs concrets** : `legal.py`, `health.py`, `mediation.py`, `training.py`, `communication.py`, `generic.py`.

## Utilisation

```python
from requetes.services.pole_processors import get_pole_processor

processor = get_pole_processor(requete.pole)
actions = processor.get_available_actions(requete)
result = processor.execute_action(requete, "assign_lawyer", user=request.user, lawyer_name="Maître X", lawyer_contact="…")
```

## Codes de pôle (Pole.code)

| Code          | Processeur              |
|---------------|-------------------------|
| `legal`       | LegalPoleProcessor      |
| `health`      | HealthPoleProcessor     |
| `mediation`   | MediationPoleProcessor  |
| `training`    | TrainingPoleProcessor   |
| `communication` | CommunicationPoleProcessor |
| `generic` ou vide | GenericPoleProcessor |

## API DRF

- **GET** `/api/requetes/<id>/pole_actions/` : liste des actions disponibles + transitions autorisées.
- **POST** `/api/requetes/<id>/execute_pole_action/` : body `{ "action_id": "…", … }` pour exécuter une action.

## Configuration dynamique (PoleWorkflow)

Le modèle **PoleWorkflow** permet de définir en base les transitions autorisées par pôle (`from_status` → `to_status`). Si des lignes existent pour un pôle, seules ces transitions sont proposées ; sinon, le processeur utilise sa logique par défaut.

## Ajouter un nouveau pôle

1. Créer `requetes/services/pole_processors/mon_pole.py` avec une classe héritant de `BasePoleProcessor` et définissant `code` et `get_action_definitions()`.
2. Implémenter les `execute_<action_id>` nécessaires.
3. Enregistrer dans `factory.py` : `_REGISTRY["mon_code"] = MonPoleProcessor`.
4. Renseigner `Pole.code` en base (ou via l’admin) pour les pôles concernés.
