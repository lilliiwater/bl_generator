import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Générateur BL", page_icon="📄")
st.title("📄 Générateur automatique de Bon de Livraison")

BLEU_LOGO = (43 / 255, 76 / 255, 126 / 255)

def facture_vers_bl(pdf_bytes: bytes, infos_supp: str) -> io.BytesIO:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]

   # Supprimer l'ancien mot "Facture" s'il existe
facture_zone = page.search_for("Facture")
if facture_zone:
    r = facture_zone[0]
    page.add_redact_annot(r, fill=(1, 1, 1))
    page.apply_redactions()

# Insérer "BON DE LIVRAISON" à la place prévue, bien sous le logo
page.insert_text(
    (400, 70),  # x = marge de gauche observée, y = sous le logo
    "BON DE LIVRAISON",
    fontsize=14,
    fontname="helv",
    fill=BLEU_LOGO

    # 3. Masquer tout en dessous de "Détails TVA"
    tva_zone = page.search_for("Détails TVA")
    if tva_zone:
        r = tva_zone[0]
        page.add_redact_annot(fitz.Rect(0, r.y0, 600, 850), fill=(1, 1, 1))

    # 4. Appliquer les redactions
    page.apply_redactions()

    # 5. Aligner infos complémentaires sur la hauteur de "Quantité"
    quantite_zone = page.search_for("Quantité")
    y_start = 380  # par défaut
    if quantite_zone:
        y_start = quantite_zone[0].y1 + 15  # juste en dessous du titre

    lignes_infos = infos_supp.strip().splitlines()
    y = y_start
    for ligne in lignes_infos:
        if ligne.strip():
            page.insert_text((300, y), ligne.strip(), fontsize=10, fontname="helv", fill=BLEU_LOGO)
            y += 20

    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return output

# Interface utilisateur
uploaded_file = st.file_uploader("📎 Sélectionner une facture PDF", type="pdf")
infos_libres = st.text_area("📝 Infos à afficher (une ligne par produit)", height=120)

if uploaded_file and st.button("🛠 Générer le Bon de Livraison"):
    input_bytes = uploaded_file.read()
    bl_pdf = facture_vers_bl(input_bytes, infos_libres)

    original_name = uploaded_file.name
    new_name = original_name.replace("Facture", "BL").replace("facture", "BL")

    st.download_button(
        "📥 Télécharger le BL",
        data=bl_pdf,
        file_name=new_name,
        mime="application/pdf"
    )
    st.success(f"✅ Bon de livraison prêt : {new_name}")
