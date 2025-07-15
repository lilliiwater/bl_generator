# app.py  –  Générateur automatique de Bon de Livraison
import streamlit as st
import fitz            # PyMuPDF
import io

st.set_page_config(page_title="Générateur BL", page_icon="📄")
st.title("📄 Générateur automatique de Bon de Livraison")

# ------------------------------------------------------------
# Paramètres DE ZONE À MASQUER  (mesurés une fois pour Pennylane A4)
# ------------------------------------------------------------
RECT_COLONNE_DROITE = fitz.Rect(400, 240, 580, 820)   # prix unitaire + totaux HT/TVA/TTC
RECT_BAS_DE_PAGE    = fitz.Rect(0,   770, 600, 850)   # RIB, mentions légales, pénalités

def facture_vers_bl(pdf_bytes: bytes, infos_supp: str) -> io.BytesIO:
    """Transforme la première page de la facture en Bon de Livraison."""
    doc  = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]

    # 1) Masquer le mot « Facture » (où qu'il soit)
    for zone in page.search_for("Facture"):
        page.add_redact_annot(zone, fill=(1, 1, 1))

    # 2) Masquer la colonne montants et le bas de page
    page.add_redact_annot(RECT_COLONNE_DROITE, fill=(1, 1, 1))
    page.add_redact_annot(RECT_BAS_DE_PAGE,    fill=(1, 1, 1))
    page.apply_redactions()

    # 3) Ajouter le titre et les informations supplémentaires
    page.insert_text((50, 50), "BON DE LIVRAISON", fontsize=16, fontname="helv")

    y = 80  # position verticale de départ pour le texte libre
    for ligne in infos_supp.splitlines():
        if ligne.strip():                     # ignore lignes vides
            page.insert_text((50, y), ligne, fontsize=10, fontname="helv")
            y += 14                           # espace entre les lignes

    # 4) Sauvegarde dans un buffer mémoire
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return output

# ------------------- Interface Streamlit -------------------
uploaded_pdf = st.file_uploader("Choisir une facture PDF (Pennylane)", type="pdf")
infos_libres = st.text_area(
    "Infos supplémentaires (date d’expédition, n° commande, chauffeur…) "
    "(une ligne = un paragraphe)")

if uploaded_pdf and st.button("🛠 Générer le Bon de Livraison"):
    bl_pdf = facture_vers_bl(uploaded_pdf.read(), infos_libres)
    st.download_button(
        label="📥 Télécharger le BL",
        data=bl_pdf,
        file_name="bon_de_livraison.pdf",
        mime="application/pdf"
    )
    st.success("Bon de livraison créé avec succès !")
