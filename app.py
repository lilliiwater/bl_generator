import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Générateur BL", page_icon="📄")
st.title("📄 Générateur automatique de Bon de Livraison")

# ✅ Zones larges à masquer (pour tous cas Pennylane)
RECT_COLONNE_DROITE = fitz.Rect(400, 240, 600, 870)   # colonne montants + totaux
RECT_BAS_DE_PAGE    = fitz.Rect(0,   820, 600, 900)   # mentions, RIB, TVA

# ✅ Couleur bleu Lilliwater (hex #2B4C7E → RGB 0–1)
BLEU_LOGO = (43/255, 76/255, 126/255)

def facture_vers_bl(pdf_bytes: bytes, infos_supp: str) -> io.BytesIO:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]

    # 1. Masquer "Facture" + zones de droite + mentions
    for zone in page.search_for("Facture"):
        page.add_redact_annot(zone, fill=(1, 1, 1))
    page.add_redact_annot(RECT_COLONNE_DROITE, fill=(1, 1, 1))
    page.add_redact_annot(RECT_BAS_DE_PAGE, fill=(1, 1, 1))
    page.apply_redactions()

    # 2. Ajouter "BON DE LIVRAISON" bien placé (≈ à droite du bloc client)
    page.insert_text((360, 330), "BON DE LIVRAISON", fontsize=14, fontname="helv", fill=BLEU_LOGO)

    # 3. Infos supplémentaires juste en dessous
    y = 355
    for ligne in infos_supp.splitlines():
        if ligne.strip():
            page.insert_text((360, y), ligne.strip(), fontsize=10, fontname="helv", fill=BLEU_LOGO)
            y += 15

    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return output

# Interface Streamlit
uploaded_pdf = st.file_uploader("📎 Sélectionner une facture Pennylane (PDF)", type="pdf")
infos_libres = st.text_area("📝 Infos à insérer : (chauffeur, date, etc.)", height=100)

if uploaded_pdf and st.button("🛠 Générer le Bon de Livraison"):
    bl_pdf = facture_vers_bl(uploaded_pdf.read(), infos_libres)
    st.download_button("📥 Télécharger le BL", bl_pdf, "bon_de_livraison.pdf", "application/pdf")
    st.success("✅ BL prêt à l’envoi.")
