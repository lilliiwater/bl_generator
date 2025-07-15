import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Générateur BL", page_icon="📄")
st.title("📄 Générateur automatique de Bon de Livraison")

# Masquage zones larges
RECT_COLONNE_DROITE = fitz.Rect(400, 240, 595, 880)
RECT_BAS_DE_PAGE    = fitz.Rect(0,   800, 595, 880)

# Couleur bleu logo (ex : #4A90E2)
BLEU_LOGO = (0.29, 0.56, 0.89)

def facture_vers_bl(pdf_bytes: bytes, infos_supp: str) -> io.BytesIO:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]

    # 1. Masquer "Facture", colonne prix, bloc totaux, mentions
    for zone in page.search_for("Facture"):
        page.add_redact_annot(zone, fill=(1, 1, 1))
    page.add_redact_annot(RECT_COLONNE_DROITE, fill=(1, 1, 1))
    page.add_redact_annot(RECT_BAS_DE_PAGE,    fill=(1, 1, 1))
    page.apply_redactions()

    # 2. Ajouter "BON DE LIVRAISON" (à droite du bloc client)
    page.insert_text(
        (400, 250),
        "BON DE LIVRAISON",
        fontsize=13,
        fontname="helv",
        fill=BLEU_LOGO,
    )

    # 3. Ajouter les infos ligne par ligne (sous le titre)
    y = 270
    for ligne in infos_supp.splitlines():
        if ligne.strip():
            page.insert_text((400, y), ligne.strip(), fontsize=10, fontname="helv", fill=BLEU_LOGO)
            y += 15

    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return output

# Interface
uploaded_pdf = st.file_uploader("Choisir une facture PDF (Pennylane)", type="pdf")
infos_libres = st.text_area("Infos à ajouter (ex : date, chauffeur…)", height=100)

if uploaded_pdf and st.button("🛠 Générer le Bon de Livraison"):
    bl_pdf = facture_vers_bl(uploaded_pdf.read(), infos_libres)
    st.download_button(
        label="📥 Télécharger le BL",
        data=bl_pdf,
        file_name="bon_de_livraison.pdf",
        mime="application/pdf"
    )
    st.success("✅ Bon de livraison prêt.")
