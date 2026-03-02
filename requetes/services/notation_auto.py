"""
Notation automatique des entreprises à partir des requêtes (issues résolues / non résolues).

Chaque critère de notation est alimenté par les requêtes dont le type_probleme
est lié à ce critère. La note (1 à 5) est déduite du taux de résolution :
- 100 % résolu → 5, 0 % résolu → 1, proportionnel entre les deux.
- Seules les requêtes clôturées (resolved, non_resolu, closed) sont comptées.
"""
from __future__ import annotations

from django.db.models import Q

from requetes.models import CritereNotation, Requete, StatutRequete, TypeProbleme


# Mapping : un critère de notation est alimenté par ces types de problème (requêtes).
# Aligné sur les critères d'évaluation et la CCA (voir CRITERES dans l'énoncé).
CRITERE_TO_TYPE_PROBLEMES: dict[str, list[str]] = {
    # 1. Critères d'évaluation des entreprises
    CritereNotation.CONFORMITE_CONTRATS: [TypeProbleme.LEGAL_COMPLIANCE],
    CritereNotation.REMUNERATION_AVANTAGES: [TypeProbleme.WORKING_CONDITIONS_REMUNERATION],
    CritereNotation.SECURITE_SANTE: [TypeProbleme.HEALTH_SAFETY_WELLBEING],
    CritereNotation.RELATIONS_SOCIALES: [
        TypeProbleme.SOCIAL_MEDIATION,
        TypeProbleme.COMMUNICATION_AWARENESS,
    ],
    CritereNotation.RUPTURE_CONTRAT: [TypeProbleme.LEGAL_COMPLIANCE],
    CritereNotation.RUPTURE_COMMUNICATION: [TypeProbleme.COMMUNICATION_AWARENESS],
    # 2. Convention collective des Assurances
    CritereNotation.CLASSIFICATION_PROFESSIONNELLE: [
        TypeProbleme.WORKING_CONDITIONS_REMUNERATION,
    ],
    CritereNotation.PRIMES_SPECIFIQUES: [TypeProbleme.WORKING_CONDITIONS_REMUNERATION],
    CritereNotation.CONDITIONS_TRAVAIL_CCA: [
        TypeProbleme.WORKING_CONDITIONS_REMUNERATION,
    ],
    CritereNotation.FORMATION: [TypeProbleme.TRAINING_CAREER],
    CritereNotation.TRAITEMENT_EQUITABLE: [
        TypeProbleme.SOCIAL_MEDIATION,
        TypeProbleme.YOUTH_NEW_EMPLOYEES,
    ],
}

STATUTS_RESOLUS = (StatutRequete.RESOLVED, StatutRequete.CLOSED)
STATUTS_NON_RESOLUS = (StatutRequete.NON_RESOLU,)
STATUTS_CLOTURES = STATUTS_RESOLUS + STATUTS_NON_RESOLUS


def get_notation_automatique(entreprise_id: int) -> dict[str, int]:
    """
    Calcule la notation automatique (1-5) par critère pour une entreprise,
    à partir des requêtes clôturées (résolu / non résolu / closed).

    Pour chaque critère, on agrège les requêtes dont le type_probleme
    est lié à ce critère. Note = 1 + 4 * (nb_résolus / nb_clôturés), arrondi.
    Si aucune requête clôturée pour ce critère, le critère n'est pas renvoyé.
    """
    result: dict[str, int] = {}
    types_par_critere = list(CRITERE_TO_TYPE_PROBLEMES.items())

    for critere, type_problemes in types_par_critere:
        requetes_cloturees = Requete.objects.filter(
            entreprise_id=entreprise_id,
            type_probleme__in=type_problemes,
            statut__in=STATUTS_CLOTURES,
        )
        total = requetes_cloturees.count()
        if total == 0:
            continue
        nb_resolus = requetes_cloturees.filter(statut__in=STATUTS_RESOLUS).count()
        ratio = nb_resolus / total
        # Note entre 1 et 5 : 1 + 4 * ratio
        note = round(1 + 4 * ratio)
        note = max(1, min(5, note))
        result[critere] = note

    return result
