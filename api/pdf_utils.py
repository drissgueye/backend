"""
Génération PDF du compte rendu de clôture (requête).
Utilise ReportLab : pip install reportlab
"""
from __future__ import annotations

import io
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requetes.models import Requete


def _escape_for_paragraph(text: str) -> str:
    """Échappe les caractères spéciaux pour ReportLab Paragraph (sous-ensemble HTML)."""
    if not text:
        return ""
    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace("\n", "<br/>")
    return text


def build_compte_rendu_pdf(requete: "Requete") -> bytes:
    """
    Génère le PDF du compte rendu de clôture pour une requête.
    Retourne les octets du fichier PDF.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError:
        raise RuntimeError(
            "Le module reportlab est requis pour l'export PDF. Installez-le avec : pip install reportlab"
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=6,
    )

    story = []

    # Titre
    story.append(
        Paragraph(
            _escape_for_paragraph(f"Compte rendu de clôture – {requete.numero_reference}"),
            title_style,
        )
    )
    story.append(Paragraph(_escape_for_paragraph(requete.titre), heading_style))
    story.append(Spacer(1, 0.5 * cm))

    # Infos requête
    story.append(Paragraph("Informations de la requête", heading_style))
    demandeur = ""
    if requete.travailleur:
        demandeur = getattr(requete.travailleur, "get_full_name", lambda: "")() or getattr(
            requete.travailleur, "username", ""
        )
        profil = getattr(requete.travailleur, "profil", None)
        if profil and (getattr(profil, "prenom", "") or getattr(profil, "nom", "")):
            parts = [getattr(profil, "prenom", "") or "", getattr(profil, "nom", "") or ""]
            demandeur = " ".join(p for p in parts if p).strip() or demandeur
    lignes = [
        f"<b>Référence :</b> {_escape_for_paragraph(requete.numero_reference)}",
        f"<b>Demandeur :</b> {_escape_for_paragraph(demandeur)}",
        f"<b>Entreprise :</b> {_escape_for_paragraph(requete.entreprise.nom if requete.entreprise else '—')}",
        f"<b>Pôle :</b> {_escape_for_paragraph(requete.pole.nom if requete.pole else '—')}",
        f"<b>Date d'ouverture :</b> {requete.created_at.strftime('%d/%m/%Y') if requete.created_at else '—'}",
    ]
    if requete.date_cloture:
        lignes.append(f"<b>Date de clôture :</b> {requete.date_cloture.strftime('%d/%m/%Y')}")
    for line in lignes:
        story.append(Paragraph(line, body_style))
    story.append(Spacer(1, 0.3 * cm))

    # Objet
    story.append(Paragraph("Objet", heading_style))
    story.append(
        Paragraph(_escape_for_paragraph(requete.description or "—"), body_style)
    )
    story.append(Spacer(1, 0.5 * cm))

    # Compte rendu
    story.append(Paragraph("Compte rendu de clôture", heading_style))
    if requete.compte_rendu and requete.compte_rendu.strip():
        story.append(
            Paragraph(_escape_for_paragraph(requete.compte_rendu.strip()), body_style)
        )
    else:
        story.append(
            Paragraph(
                "<i>Aucun compte rendu saisi.</i>",
                body_style,
            )
        )

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
