import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Générateur BL", page_icon="📄")
st.title("📄 Générateur automatique de Bon de Livraison")

# Couleur bleu Lilliwater (ex. #2B4C7E)
BLEU_LOGO = (43/255, 76/255, 126/255)

def facture_vers_bl(pdf_bytes: bytes, infos_supp: str) -> io.BytesIO:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]

    # 1. Masquer le mot "Facture"
    for zone in page.search_for("Facture"):
        page.add_redact_annot(zone, fill=(1, 1, 1))

    # 2. Trouver et masquer toute la colonne de montants en euros
    zones_euro = page.search_for("€")
    if zones_euro:
        min_x = min(r.x0 for r in zones_euro)
        zone_colonne = fitz.Rect(min_x - 10, 200, 600, 850)
        page.add_redact_annot(zone_colonne, fill=(1, 1, 1))

    # 3. Masquer à partir de "Détails TVA" jusqu'en bas
    zones_tva = page.search_for("Détails TVA")
    if zones_tva:
        y_start = zones_tva[0].y0
        rect_tva = fitz.Rect(0, y_start, 600, 900)
        page.add_redact_annot(rect_tva, fill=(1, 1, 1))

    page.apply_redactions()

    # 4. Ajouter le titre "BON DE LIVRAISON" à droite du bloc client
    page.insert_text((370, 300), "BON DE LIVRAISON", fontsize=14, fontname="helv", fill=BLEU_LOGO)

    # 5. Ajouter les infos supplémentaires en dessous
    y = 320
    for ligne in infos_supp.splitlines():
        if ligne.strip():
            page.insert_text((370, y), ligne.strip(), fontsize=10, fontname="helv", fill=BLEU_LOGO)
            y += 15

    # 6. Sauvegarde du PDF
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return output

# Interface utilisateur
uploaded_pdf = st.file_uploader("📎 Sélectionner une facture PDF", type="pdf")
infos_libres = st.text_area("📝 Infos à insérer : (chauffeur, date…)", height=100)

if uploaded_pdf and st.button("🛠 Générer le Bon de Livraison"):
    bl_pdf = facture_vers_bl(uploaded_pdf.read(), infos_libres)
    st.download_button("📥 Télécharger le BL", bl_pdf, "bon_de_livraison.pdf", "application/pdf")
    st.success("✅ Bon de livraison prêt.")
