import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Générateur BL", page_icon="📄")
st.title("📄 Générateur automatique de Bon de Livraison")

BLEU_LOGO = (43 / 255, 76 / 255, 126 / 255)

def facture_vers_bl(pdf_bytes: bytes, infos_supp: str) -> io.BytesIO:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]

    # 1. Masquer "Facture"
    for zone in page.search_for("Facture"):
        page.add_redact_annot(zone, fill=(1, 1, 1))

    # 2. Masquer uniquement les colonnes PRIX
    mots_prix = ["Prix u. HT", "TVA (%)", "Total HT"]
    for mot in mots_prix:
        for r in page.search_for(mot):
            x0 = r.x0
            x1 = r.x1 + 50  # largeur colonne
            # 🟩 Masquer seulement SOUS la ligne produits
            page.add_redact_annot(fitz.Rect(x0, 370, x1, 800), fill=(1, 1, 1))

    # 3. Masquer tout en dessous de "Détails TVA"
    tva_zone = page.search_for("Détails TVA")
    if tva_zone:
        y = tva_zone[0].y0
        page.add_redact_annot(fitz.Rect(0, y, 600, 900), fill=(1, 1, 1))

    page.apply_redactions()

    # 4. Ajouter "BON DE LIVRAISON" juste sous le logo
    page.insert_text((50, 130), "BON DE LIVRAISON", fontsize=14, fontname="helv", fill=BLEU_LOGO)

    # 5. Ajouter les infos complémentaires en face de la référence produit (à gauche des quantités)
    lignes_infos = infos_supp.strip().splitlines()
    y = 380  # ligne 1 produit
    for ligne in lignes_infos:
        if ligne.strip():
            page.insert_text((200, y), ligne.strip(), fontsize=10, fontname="helv", fill=BLEU_LOGO)
            y += 20

    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return output

# Interface Streamlit
uploaded_file = st.file_uploader("📎 Sélectionner une facture PDF", type="pdf")
infos_libres = st.text_area("📝 Infos à insérer (une ligne = un produit)", height=120)

if uploaded_file and st.button("🛠 Générer le Bon de Livraison"):
    input_bytes = uploaded_file.read()
    bl_pdf = facture_vers_bl(input_bytes, infos_libres)

    # Générer un nom automatique : remplacer Facture → BL
    original_name = uploaded_file.name
    new_name = original_name.replace("Facture", "BL").replace("facture", "BL")

    st.download_button(
        "📥 Télécharger le BL",
        data=bl_pdf,
        file_name=new_name,
        mime="application/pdf"
    )
    st.success(f"✅ Bon de livraison prêt : {new_name}")
