import streamlit as st
import fitz  # PyMuPDF
import io

st.title("🧾 Générateur de Bon de Livraison")
st.write("Charge une facture PDF, et télécharge un bon de livraison.")

uploaded_file = st.file_uploader("Choisis une facture PDF", type="pdf")

def modifier_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    page = doc[0]

    # Masquer "Facture"
    for zone in page.search_for("Facture"):
        page.add_redact_annot(zone, fill=(1,1,1))
    page.apply_redactions()

    # Ajouter titre
    page.insert_text((50, 50), "BON DE LIVRAISON", fontsize=16)
    page.insert_text((50, 80), "Livraison prévue : fin de semaine")

    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return output

if uploaded_file:
    if st.button("🛠 Générer le BL"):
        bl_pdf = modifier_pdf(uploaded_file.read())
        st.success("Bon de livraison prêt ✅")
        st.download_button("📥 Télécharger le BL", bl_pdf, "bon_livraison.pdf", "application/pdf")
