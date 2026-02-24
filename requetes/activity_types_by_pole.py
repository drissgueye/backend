"""
Types d'activité et champs associés par pôle (suivi des activités sur les tickets).
Chaque pôle a des missions différentes : les types d'activité et les champs affichés
dans le formulaire "Ajouter une activité" dépendent du pôle de la requête.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from requetes.models import Pole

# Structure d'un champ optionnel lié à un type d'activité
# type: "text" | "date" | "datetime" | "number" | "textarea"
FIELD_DEF = dict[str, Any]  # name, label, type, required

# Structure d'un type d'activité : value, label, champs optionnels
ACTIVITY_TYPE_DEF = dict[str, Any]  # value, label, fields: list[FIELD_DEF]

# Types d'activité par code de pôle (Pole.code)
ACTIVITY_TYPES_BY_POLE: dict[str, list[ACTIVITY_TYPE_DEF]] = {
    "generic": [
        {"value": "call", "label": "Appel téléphonique", "fields": []},
        {"value": "meeting", "label": "Rendez-vous", "fields": []},
        {"value": "document", "label": "Document à fournir", "fields": []},
        {"value": "note", "label": "Note interne", "fields": []},
    ],
    # 1. Pôle Conditions de Travail et Rémunération
    "remuneration": [
        {"value": "call", "label": "Appel téléphonique", "fields": []},
        {"value": "meeting", "label": "Rendez-vous", "fields": []},
        {"value": "note", "label": "Note interne", "fields": []},
        {
            "value": "evaluation_grille",
            "label": "Évaluation grille salariale",
            "fields": [
                {"name": "secteur_ou_branche", "label": "Secteur / branche", "type": "text", "required": False},
                {"name": "date_limite", "label": "Date limite de remise", "type": "date", "required": False},
            ],
        },
        {
            "value": "suivi_primes",
            "label": "Suivi primes ou avantages",
            "fields": [
                {"name": "type_prime", "label": "Type (prime, avantage, etc.)", "type": "text", "required": False},
                {"name": "reference", "label": "Référence accord / texte", "type": "text", "required": False},
            ],
        },
        {
            "value": "suivi_heures_abus",
            "label": "Suivi heures sup. ou abus contrats précaires",
            "fields": [
                {"name": "nature", "label": "Nature (heures sup., CDD abusif, etc.)", "type": "text", "required": False},
                {"name": "effectifs_concernes", "label": "Effectifs concernés", "type": "text", "required": False},
            ],
        },
        {
            "value": "negociation_convention",
            "label": "Négociation convention collective",
            "fields": [
                {"name": "theme", "label": "Thème / point négocié", "type": "text", "required": False},
                {"name": "date_reunion", "label": "Date de réunion", "type": "date", "required": False},
            ],
        },
    ],
    # 2. Pôle Formation et Carrière
    "training": [
        {"value": "call", "label": "Appel téléphonique", "fields": []},
        {"value": "meeting", "label": "Rendez-vous", "fields": []},
        {"value": "note", "label": "Note interne", "fields": []},
        {
            "value": "plan_formation",
            "label": "Plan annuel de formation",
            "fields": [
                {"name": "resume_plan", "label": "Résumé du plan", "type": "textarea", "required": False},
                {"name": "deadline", "label": "Échéance", "type": "date", "required": False},
            ],
        },
        {
            "value": "mentorat",
            "label": "Programme mentorat / évolution carrière",
            "fields": [
                {"name": "objectif", "label": "Objectif (mentorat, évolution)", "type": "text", "required": False},
                {"name": "beneficiaires", "label": "Bénéficiaires", "type": "text", "required": False},
            ],
        },
        {
            "value": "suivi_blocage",
            "label": "Suivi employé bloqué sans évolution",
            "fields": [
                {"name": "situation", "label": "Situation / blocage", "type": "textarea", "required": False},
                {"name": "actions_prevues", "label": "Actions prévues", "type": "textarea", "required": False},
            ],
        },
    ],
    # 3. Pôle Dialogue Social et Médiation
    "mediation": [
        {"value": "call", "label": "Appel téléphonique", "fields": []},
        {"value": "meeting", "label": "Rendez-vous / réunion", "fields": []},
        {"value": "note", "label": "Note interne", "fields": []},
        {
            "value": "assemblee_generale",
            "label": "Assemblée générale d'employés",
            "fields": [
                {"name": "date_ag", "label": "Date prévue", "type": "date", "required": False},
                {"name": "ordre_du_jour", "label": "Ordre du jour", "type": "textarea", "required": False},
            ],
        },
        {
            "value": "intervention_licenciement",
            "label": "Intervention licenciement abusif / conflit",
            "fields": [
                {"name": "type_intervention", "label": "Type (licenciement, conflit interpersonnel)", "type": "text", "required": False},
                {"name": "entretien_disciplinaire", "label": "Assistance entretien disciplinaire", "type": "text", "required": False},
            ],
        },
        {
            "value": "convocation_rh",
            "label": "Convocation RH / instance dialogue",
            "fields": [
                {"name": "sujet", "label": "Sujet", "type": "text", "required": False},
                {"name": "date_convocation", "label": "Date convocation", "type": "date", "required": False},
            ],
        },
        {
            "value": "rapport_mediation",
            "label": "Rapport de médiation",
            "fields": [
                {"name": "conclusions", "label": "Conclusions", "type": "textarea", "required": False},
                {"name": "prochaines_etapes", "label": "Prochaines étapes", "type": "textarea", "required": False},
            ],
        },
    ],
    # 4. Pôle Santé, Sécurité et Bien-être au travail
    "health": [
        {"value": "call", "label": "Appel téléphonique", "fields": []},
        {"value": "meeting", "label": "Rendez-vous", "fields": []},
        {"value": "note", "label": "Note interne", "fields": []},
        {
            "value": "enquete_stress_rps",
            "label": "Enquête stress / RPS",
            "fields": [
                {"name": "perimetre", "label": "Périmètre (service, site)", "type": "text", "required": False},
                {"name": "date_enquete", "label": "Date prévue", "type": "date", "required": False},
            ],
        },
        {
            "value": "visite_ergonomie",
            "label": "Visite ergonomie / matériel",
            "fields": [
                {"name": "lieu", "label": "Lieu / poste", "type": "text", "required": False},
                {"name": "demande_materiel", "label": "Demande matériel ergonomique", "type": "textarea", "required": False},
            ],
        },
        {
            "value": "negociation_mutuelle",
            "label": "Négociation mutuelle santé",
            "fields": [
                {"name": "objet", "label": "Objet (négociation, suivi)", "type": "text", "required": False},
                {"name": "date_echange", "label": "Date échange", "type": "date", "required": False},
            ],
        },
        {
            "value": "reflexion_sante_travailleurs",
            "label": "Réflexion / avis prise en charge santé travailleurs",
            "fields": [
                {"name": "sujet", "label": "Sujet de réflexion", "type": "textarea", "required": False},
                {"name": "consultation_prevue", "label": "Consultation des membres prévue", "type": "text", "required": False},
            ],
        },
    ],
    # 5. Pôle Juridique et Conformité
    "legal": [
        {"value": "call", "label": "Appel téléphonique", "fields": []},
        {"value": "meeting", "label": "Rendez-vous", "fields": []},
        {"value": "document", "label": "Document à fournir", "fields": []},
        {"value": "note", "label": "Note interne", "fields": []},
        {
            "value": "conseil_droits",
            "label": "Conseil sur les droits",
            "fields": [
                {"name": "theme_droit", "label": "Thème (licenciement, contrat, etc.)", "type": "text", "required": False},
            ],
        },
        {
            "value": "intervention_licenciement_abusif",
            "label": "Intervention licenciement abusif",
            "fields": [
                {"name": "reference_dossier", "label": "Référence dossier", "type": "text", "required": False},
                {"name": "tribunal", "label": "Tribunal / instance", "type": "text", "required": False},
            ],
        },
        {
            "value": "suivi_application_lois",
            "label": "Suivi application des lois sociales",
            "fields": [
                {"name": "texte_ou_theme", "label": "Texte / thème", "type": "text", "required": False},
            ],
        },
        {
            "value": "assignation_avocat",
            "label": "Prise en charge avocat / suivi dossier",
            "fields": [
                {"name": "avocat_nom", "label": "Nom de l'avocat", "type": "text", "required": False},
                {"name": "reference_tribunal", "label": "Référence tribunal", "type": "text", "required": False},
                {"name": "date_audience", "label": "Date audience", "type": "date", "required": False},
            ],
        },
    ],
    # 6. Pôle Communication et Sensibilisation
    "communication": [
        {"value": "call", "label": "Appel téléphonique", "fields": []},
        {"value": "meeting", "label": "Rendez-vous", "fields": []},
        {"value": "note", "label": "Note interne", "fields": []},
        {
            "value": "bulletin_whatsapp",
            "label": "Bulletin / groupe WhatsApp syndical",
            "fields": [
                {"name": "support", "label": "Support (bulletin, WhatsApp)", "type": "text", "required": False},
                {"name": "date_publication", "label": "Date publication prévue", "type": "date", "required": False},
            ],
        },
        {
            "value": "campagne_droits",
            "label": "Campagne « Connais tes droits »",
            "fields": [
                {"name": "intitule", "label": "Intitulé campagne", "type": "text", "required": False},
                {"name": "cible", "label": "Public cible", "type": "text", "required": False},
            ],
        },
        {
            "value": "journee_conférence",
            "label": "Journée syndicale / conférence",
            "fields": [
                {"name": "theme", "label": "Thème", "type": "text", "required": False},
                {"name": "date_evenement", "label": "Date", "type": "date", "required": False},
            ],
        },
        {
            "value": "cohesion_promotion",
            "label": "Cohésion sociale / promotion assurance",
            "fields": [
                {"name": "type_activite", "label": "Type (don de sang, forum premier emploi, etc.)", "type": "text", "required": False},
                {"name": "partenaires", "label": "Partenaires (écoles, etc.)", "type": "text", "required": False},
            ],
        },
        {
            "value": "spot_sensibilisation",
            "label": "Sensibilisation rôle de l'assurance (spots)",
            "fields": [
                {"name": "support", "label": "Support (spot, vulgarisation)", "type": "text", "required": False},
                {"name": "date_lancement", "label": "Date lancement", "type": "date", "required": False},
            ],
        },
    ],
    # 7. Pôle Innovation, Digitalisation et Transformation
    "innovation": [
        {"value": "call", "label": "Appel téléphonique", "fields": []},
        {"value": "meeting", "label": "Rendez-vous", "fields": []},
        {"value": "note", "label": "Note interne", "fields": []},
        {
            "value": "formation_outils",
            "label": "Revendication formation nouveaux outils",
            "fields": [
                {"name": "outils", "label": "Outils (CRM, IA, plateformes)", "type": "text", "required": False},
                {"name": "public_cible", "label": "Public cible", "type": "text", "required": False},
            ],
        },
        {
            "value": "equipe_promotion_tic",
            "label": "Équipe promotion assurance / TIC",
            "fields": [
                {"name": "mission", "label": "Mission (spots, vulgarisation)", "type": "textarea", "required": False},
                {"name": "responsable_tic", "label": "Responsable TIC", "type": "text", "required": False},
            ],
        },
    ],
    # 8. Pôle Relations Extérieures et Partenariats
    "external_relations": [
        {"value": "call", "label": "Appel téléphonique", "fields": []},
        {"value": "meeting", "label": "Rendez-vous", "fields": []},
        {"value": "note", "label": "Note interne", "fields": []},
        {
            "value": "echange_syndicats",
            "label": "Échange syndicats (CNTS, international)",
            "fields": [
                {"name": "organisme", "label": "Organisme (CNTS, ILO, CIMA, etc.)", "type": "text", "required": False},
                {"name": "sujet", "label": "Sujet", "type": "text", "required": False},
            ],
        },
        {
            "value": "atelier_acaps_fanaf",
            "label": "Atelier ACAPS / FANAF",
            "fields": [
                {"name": "organisateur", "label": "Organisateur", "type": "text", "required": False},
                {"name": "date_atelier", "label": "Date", "type": "date", "required": False},
            ],
        },
        {
            "value": "accord_cooperation",
            "label": "Accord de coopération / partenariat",
            "fields": [
                {"name": "partenaire", "label": "Partenaire", "type": "text", "required": False},
                {"name": "objet", "label": "Objet de l'accord", "type": "textarea", "required": False},
            ],
        },
        {
            "value": "activite_inter_syndicat",
            "label": "Activité inter-syndicats (travail commun)",
            "fields": [
                {"name": "syndicats_impliques", "label": "Syndicats impliqués", "type": "text", "required": False},
                {"name": "type_activite", "label": "Type d'activité", "type": "text", "required": False},
            ],
        },
    ],
    # 9. Pôle Jeunesse et Intégration des Nouveaux Employés
    "youth": [
        {"value": "call", "label": "Appel téléphonique", "fields": []},
        {"value": "meeting", "label": "Rendez-vous", "fields": []},
        {"value": "note", "label": "Note interne", "fields": []},
        {
            "value": "session_accueil",
            "label": "Session d'accueil syndical nouveau collaborateur",
            "fields": [
                {"name": "date_session", "label": "Date session", "type": "date", "required": False},
                {"name": "nombre_participants", "label": "Nombre de participants", "type": "text", "required": False},
            ],
        },
        {
            "value": "defense_stagiaires_prestataires",
            "label": "Défense stagiaires / prestataires",
            "fields": [
                {"name": "contexte", "label": "Contexte (négociation, litige)", "type": "textarea", "required": False},
            ],
        },
        {
            "value": "groupe_jeunes_syndiques",
            "label": "Groupe de jeunes syndiqués",
            "fields": [
                {"name": "objectif", "label": "Objectif / activité", "type": "text", "required": False},
                {"name": "date_reunion", "label": "Date réunion", "type": "date", "required": False},
            ],
        },
    ],
    # 10. Sport et bien-être
    "sport_wellbeing": [
        {"value": "call", "label": "Appel téléphonique", "fields": []},
        {"value": "meeting", "label": "Rendez-vous", "fields": []},
        {"value": "note", "label": "Note interne", "fields": []},
        {
            "value": "tournoi_rando",
            "label": "Tournoi / randonnée (sport récréatif)",
            "fields": [
                {"name": "type_evenement", "label": "Type (tournoi, randonnée)", "type": "text", "required": False},
                {"name": "date_evenement", "label": "Date", "type": "date", "required": False},
                {"name": "lieu", "label": "Lieu", "type": "text", "required": False},
            ],
        },
        {
            "value": "journee_bien_etre",
            "label": "Journée bien-être / séminaire gestion du stress",
            "fields": [
                {"name": "theme", "label": "Thème", "type": "text", "required": False},
                {"name": "date_evenement", "label": "Date", "type": "date", "required": False},
            ],
        },
    ],
    # 11. Pôle Habitat (proposition)
    "habitat": [
        {"value": "call", "label": "Appel téléphonique", "fields": []},
        {"value": "meeting", "label": "Rendez-vous", "fields": []},
        {"value": "note", "label": "Note interne", "fields": []},
        {
            "value": "info_aides_logement",
            "label": "Information aides au logement",
            "fields": [
                {"name": "type_aide", "label": "Type d'aide (prêt, subvention, etc.)", "type": "text", "required": False},
                {"name": "organisme", "label": "Organisme partenaire", "type": "text", "required": False},
            ],
        },
        {
            "value": "partenariat_habitat",
            "label": "Partenariat logement / promoteurs",
            "fields": [
                {"name": "partenaire", "label": "Partenaire (promoteur, bailleur)", "type": "text", "required": False},
                {"name": "objet", "label": "Objet (convention, avantage)", "type": "textarea", "required": False},
            ],
        },
        {
            "value": "suivi_dossier_habitat",
            "label": "Suivi dossier personnel logement",
            "fields": [
                {"name": "type_dossier", "label": "Type (demande prêt, attribution)", "type": "text", "required": False},
                {"name": "date_limite", "label": "Échéance", "type": "date", "required": False},
            ],
        },
        {
            "value": "animation_collectivite",
            "label": "Animation vie collective / cadre de vie",
            "fields": [
                {"name": "action", "label": "Action (réunion quartier, amélioration cadre de vie)", "type": "text", "required": False},
                {"name": "date_prevue", "label": "Date prévue", "type": "date", "required": False},
            ],
        },
        {
            "value": "reflexion_habitat_travailleurs",
            "label": "Réflexion habitat des travailleurs",
            "fields": [
                {"name": "theme", "label": "Thème (logement social, transport, proximité, etc.)", "type": "text", "required": False},
                {"name": "date_echange", "label": "Date d'échange / réunion", "type": "date", "required": False},
            ],
        },
    ],
}


def get_activity_types_for_pole(pole_code: str | None) -> list[ACTIVITY_TYPE_DEF]:
    """
    Retourne les types d'activité (et champs associés) pour un code de pôle.
    Si le code est vide ou inconnu, retourne les types génériques.
    """
    code = (pole_code or "").strip().lower() or "generic"
    return ACTIVITY_TYPES_BY_POLE.get(code, ACTIVITY_TYPES_BY_POLE["generic"]).copy()


def get_allowed_type_values_for_pole(pole_code: str | None) -> set[str]:
    """Retourne l'ensemble des valeurs (value) autorisées pour type_activite pour ce pôle."""
    types_list = get_activity_types_for_pole(pole_code)
    return {t["value"] for t in types_list}


def is_valid_activity_type_for_pole(pole_code: str | None, type_value: str) -> bool:
    """Indique si type_value est un type d'activité valide pour le pôle."""
    return type_value in get_allowed_type_values_for_pole(pole_code)


# Mapping nom de pôle (tel qu'en base) -> code, pour les pôles sans code renseigné
POLE_NOM_TO_CODE: dict[str, str] = {
    "Pôle Habitat": "habitat",
    "Pôle Conditions de Travail et Rémunération": "remuneration",
    "Pôle Formation et Carrière": "training",
    "Pôle Dialogue Social et Médiation": "mediation",
    "Pôle Santé, Sécurité et Bien-être au travail": "health",
    "Pôle Juridique et Conformité": "legal",
    "Pôle Communication et Sensibilisation": "communication",
    "Pôle Innovation, Digitalisation et Transformation": "innovation",
    "Pôle Relations Extérieures et Partenariats": "external_relations",
    "Pôle Jeunesse et Intégration des Nouveaux Employés": "youth",
    "Pôle Sport et Bien-être": "sport_wellbeing",
}


def get_pole_activity_code(pole: Any) -> str:
    """
    Retourne le code d'activité à utiliser pour un pôle (Pole model).
    Priorité au mapping par nom (POLE_NOM_TO_CODE) pour que chaque pôle
    ait bien ses types d'activité dédiés (ex. Pôle Habitat -> "habitat").
    Sinon utilise pole.code, puis "generic".
    """
    nom = getattr(pole, "nom", None) or ""
    if nom in POLE_NOM_TO_CODE:
        return POLE_NOM_TO_CODE[nom]
    if getattr(pole, "code", None) and str(pole.code).strip():
        return str(pole.code).strip().lower()
    return "generic"
