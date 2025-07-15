import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Générateur BL", page_icon="📄")
st.title("📄 Générateur automatique de Bon de Livraison")

BLEU_LOGO = (43 / 255, 76 / 255, 126 / 255)

def facture_vers_bl(pdf_bytes: bytes, infos_supp: str) -> io.BytesIO:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]

    # 1. Masquer les colonnes PRIX dynamiquement à partir de leur titre
    mots_prix = ["Prix u. HT", "TVA (%)", "Total HT"]
    for mot in mots_prix:
        for r in page.search_for(mot):
            rect = fitz.Rect(r.x0, r.y0, r.x1 + 50, 800)  # masque vers le bas
            page.add_redact_annot(rect, fill=(1, 1, 1))

    # 2. Masquer en dessous de "Détails TVA"
    tva_matches = page.search_for("Détails TVA")
    for match in tva_matches:
        rect = fitz.Rect(0, match.y0, 600, 850)
        page.add_redact_annot(rect, fill=(1, 1, 1))

    # 3. Appliquer les redactions
    page.apply_redactions()

    # 4. Ajouter "BON DE LIVRAISON" juste SOUS le logo (aligné dynamiquement)
    logo_anchor = page.search_for("LiLLii Water")
    if logo_anchor:
        y_logo = logo_anchor[0].y1 + 10
        x_logo = logo_anchor[0].x0
        page.insert_text((x_logo, y_logo), "BON DE LIVRAISON", fontsize=14, fontname="helv", fill=BLEU_LOGO)

    # 5. Ajouter les infos complémentaires à la place des colonnes masquées (ex: x = 300)
    lignes_infos = infos_supp.strip().splitlines()
    y = 380  # début des lignes produits
    for ligne in lignes_infos:
        if ligne.strip():
            page.insert_text((300, y), ligne.strip(), fontsize=10, fontname="helv", fill=BLEU_LOGO)
            y += 20

    # 6. Exporter le PDF en mémoire
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

    # Nom dynamique : remplacer Facture → BL
    original_name = uploaded_file.name
    new_name = original_name.replace("Facture", "BL").replace("facture", "BL")

    st.download_button(
        "📥 Télécharger le BL",
        data=bl_pdf,
        file_name=new_name,
        mime="application/pdf"
    )
    st.success(f"✅ Bon de livraison prêt : {new_name}")
