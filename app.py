import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Générateur BL", page_icon="📄")
st.title("📄 Générateur automatique de Bon de Livraison")

BLEU_LOGO = (43 / 255, 76 / 255, 126 / 255)

def facture_vers_bl(pdf_bytes: bytes, infos_supp: str) -> io.BytesIO:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]

    # Masquer "Facture"
    for zone in page.search_for("Facture"):
        page.add_redact_annot(zone, fill=(1, 1, 1))

    # Masquer colonnes prix à partir des titres
    mots_prix = ["Prix u. HT", "TVA (%)", "Total HT"]
    x_positions = []
    for mot in mots_prix:
        results = page.search_for(mot)
        for r in results:
            x_positions.append(r.x0)

    if x_positions:
        min_x = min(x_positions)
        rect_col = fitz.Rect(min_x, 200, 600, 800)
        page.add_redact_annot(rect_col, fill=(1, 1, 1))

    # Masquer tout en dessous de "Détails TVA"
    tva_zone = page.search_for("Détails TVA")
    if tva_zone:
        y = tva_zone[0].y0
        page.add_redact_annot(fitz.Rect(0, y, 600, 900), fill=(1, 1, 1))

    page.apply_redactions()

    # Titre "BON DE LIVRAISON" sous le logo (pas sur)
    page.insert_text((50, 120), "BON DE LIVRAISON", fontsize=14, fontname="helv", fill=BLEU_LOGO)

    # Infos complémentaires en face des quantités
    lignes_infos = infos_supp.strip().splitlines()
    y = 380  # Aligné avec lignes produits
    for ligne in lignes_infos:
        if ligne.strip():
            page.insert_text((300, y), ligne.strip(), fontsize=10, fontname="helv", fill=BLEU_LOGO)
            y += 20

    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return output

# Interface utilisateur
uploaded_file = st.file_uploader("📎 Sélectionnez une facture PDF", type="pdf")
infos_libres = st.text_area("📝 Infos à afficher en face des produits (une ligne = un produit)", height=120)

if uploaded_file and st.button("🛠 Générer le Bon de Livraison"):
    # Lire le PDF d'origine
    input_bytes = uploaded_file.read()
    bl_pdf = facture_vers_bl(input_bytes, infos_libres)

    # Nom du fichier de sortie : remplacer "Facture" par "BL"
    original_name = uploaded_file.name
    new_name = original_name.replace("Facture", "BL")

    st.download_button(
        "📥 Télécharger le BL",
        data=bl_pdf,
        file_name=new_name,
        mime="application/pdf"
    )
    st.success(f"✅ Bon de livraison prêt : {new_name}")
