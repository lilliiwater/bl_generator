import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Générateur BL", page_icon="📄")
st.title("📄 Générateur automatique de Bon de Livraison")

# Couleur bleu Lilliwater
BLEU_LOGO = (43 / 255, 76 / 255, 126 / 255)

def facture_vers_bl(pdf_bytes: bytes, infos_supp: str) -> io.BytesIO:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]

    # 1. Masquer le mot "Facture"
    for zone in page.search_for("Facture"):
        page.add_redact_annot(zone, fill=(1, 1, 1))

    # 2. Masquer la colonne PRIX uniquement : à droite des titres "Prix u. HT", "TVA (%)", "Total HT"
    keywords_to_mask = ["Prix u. HT", "TVA (%)", "Total HT"]
    x_positions = []

    for keyword in keywords_to_mask:
        results = page.search_for(keyword)
        for rect in results:
            x_positions.append(rect.x0)

    if x_positions:
        min_x = min(x_positions)
        rect_colonne_prix = fitz.Rect(min_x, 200, 600, 800)
        page.add_redact_annot(rect_colonne_prix, fill=(1, 1, 1))

    # 3. Masquer tout sous "Détails TVA"
    tva_zone = page.search_for("Détails TVA")
    if tva_zone:
        y_start = tva_zone[0].y0
        rect_tva = fitz.Rect(0, y_start, 600, 900)
        page.add_redact_annot(rect_tva, fill=(1, 1, 1))

    page.apply_redactions()

    # 4. Ajouter "BON DE LIVRAISON" juste sous le logo (à gauche)
    page.insert_text((50, 50), "BON DE LIVRAISON", fontsize=14, fontname="helv", fill=BLEU_LOGO)

    # 5. Ajouter infos face aux produits, à côté des quantités
    # Pour simplifier : insérer à partir de Y = 380, en augmentant de 20px par ligne
    y = 380
    for ligne in infos_supp.splitlines():
        if ligne.strip():
            page.insert_text((300, y), ligne.strip(), fontsize=10, fontname="helv", fill=BLEU_LOGO)
            y += 20

    # Générer PDF final
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return output

# Interface
uploaded_pdf = st.file_uploader("📎 Charger une facture PDF", type="pdf")
infos_libres = st.text_area("📝 Infos à insérer ligne par ligne (face aux produits)", height=120)

if uploaded_pdf and st.button("🛠 Générer le Bon de Livraison"):
    bl_pdf = facture_vers_bl(uploaded_pdf.read(), infos_libres)
    st.download_button("📥 Télécharger le BL", bl_pdf, "bon_de_livraison.pdf", "application/pdf")
    st.success("✅ Bon de livraison prêt.")
