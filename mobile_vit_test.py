# mobile_vit_test.py - Compact Clothing Analysis Testing
"""
Compact UI to test all clothing attributes at once.
Results displayed in easy-to-compare format.

Run: streamlit run mobile_vit_test.py
"""

import streamlit as st
import torch
from PIL import Image
import time
from transformers import CLIPProcessor, CLIPModel
from sklearn.cluster import KMeans
import numpy as np

st.set_page_config(page_title="Clothing Analyzer", page_icon="👔", layout="wide")

# ===== LABELS =====
CLOTHING_TYPES = ["t-shirt", "shirt", "blouse", "sweater", "hoodie", "jeans", "trousers", 
                  "shorts", "skirt", "dress", "jumpsuit", "sneakers", "formal shoes", 
                  "boots", "sandals", "jacket", "coat", "blazer"]

PATTERNS = ["solid color", "striped", "checkered", "floral", "polka dots", 
            "geometric", "abstract print", "animal print", "gradient"]

FORMALITY = ["casual everyday", "smart casual", "business casual", "formal professional", "athletic sportswear"]

SEASONS = ["lightweight summer", "medium weight", "heavy winter"]

MATERIALS = ["cotton", "denim", "leather", "wool", "polyester", "silk", "linen", "knit"]

FITS = ["tight fitted", "slim fit", "regular fit", "relaxed fit", "loose oversized"]

# ===== MODEL =====
@st.cache_resource
def load_model():
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return model, processor

def classify(model, processor, image, labels, prefix="a photo of "):
    inputs = processor(text=[f"{prefix}{l}" for l in labels], images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        probs = model(**inputs).logits_per_image.softmax(dim=1)[0]
    idx = probs.argmax().item()
    return labels[idx], probs[idx].item()

def extract_colors(image, n=4):
    img = image.copy()
    img.thumbnail((100, 100))
    pixels = np.array(img).reshape(-1, 3)
    mask = (pixels.sum(axis=1) > 30) & (pixels.sum(axis=1) < 730)
    pixels = pixels[mask]
    if len(pixels) < n:
        return [("#000000", 100)]
    kmeans = KMeans(n_clusters=n, random_state=42, n_init=10).fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)
    _, counts = np.unique(kmeans.labels_, return_counts=True)
    props = counts / len(kmeans.labels_)
    results = []
    for i in np.argsort(props)[::-1]:
        hex_c = '#{:02x}{:02x}{:02x}'.format(*colors[i])
        results.append((hex_c, float(props[i] * 100)))
    return results

# ===== UI =====
st.title("👔 Clothing Analyzer")

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("📷 Image")
    method = st.radio("", ["Upload", "Camera"], horizontal=True, label_visibility="collapsed")
    uploaded = st.file_uploader("", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed") if method == "Upload" else st.camera_input("")
    
    if uploaded:
        image = Image.open(uploaded).convert('RGB')
        st.image(image, use_column_width=True)
        run = st.button("🚀 Analyze All", type="primary", use_container_width=True)
    else:
        run = False
        st.info("Upload an image")

with col2:
    if uploaded and run:
        model, processor = load_model()
        start = time.time()
        
        # Run all analyses
        with st.spinner("Analyzing..."):
            type_result = classify(model, processor, image, CLOTHING_TYPES)
            pattern_result = classify(model, processor, image, PATTERNS, "clothing with ")
            formality_result = classify(model, processor, image, FORMALITY)
            season_result = classify(model, processor, image, SEASONS, "")
            material_result = classify(model, processor, image, MATERIALS, "clothing made of ")
            fit_result = classify(model, processor, image, FITS)
            colors = extract_colors(image)
        
        total_time = time.time() - start
        
        # Display results in compact grid
        st.success(f"✅ Analysis complete in {total_time:.2f}s")
        
        # Row 1: Main attributes
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("👕 Type", type_result[0].title(), f"{type_result[1]*100:.0f}%")
        with c2:
            st.metric("🔲 Pattern", pattern_result[0].replace(" color", "").title(), f"{pattern_result[1]*100:.0f}%")
        with c3:
            st.metric("👔 Formality", formality_result[0].split()[0].title(), f"{formality_result[1]*100:.0f}%")
        
        # Row 2: Secondary attributes
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("❄️ Season", season_result[0].split()[0].title(), f"{season_result[1]*100:.0f}%")
        with c2:
            st.metric("🧶 Material", material_result[0].title(), f"{material_result[1]*100:.0f}%")
        with c3:
            st.metric("📐 Fit", fit_result[0].replace(" fitted", "").replace(" fit", "").title(), f"{fit_result[1]*100:.0f}%")
        
        # Row 3: Colors
        st.subheader("🎨 Colors")
        color_html = '<div style="display:flex; gap:10px; align-items:center;">'
        for hex_c, pct in colors:
            color_html += f'<div style="width:50px;height:50px;background:{hex_c};border-radius:8px;border:2px solid #444;"></div>'
            color_html += f'<span style="margin-right:20px;">{hex_c} ({pct:.0f}%)</span>'
        color_html += '</div>'
        st.markdown(color_html, unsafe_allow_html=True)
        
        # Summary table
        st.divider()
        st.subheader("📋 Summary")
        
        summary = {
            "Attribute": ["Type", "Pattern", "Formality", "Season", "Material", "Fit"],
            "Result": [
                type_result[0].title(),
                pattern_result[0].replace(" color", "").title(),
                formality_result[0].title(),
                season_result[0].title(),
                material_result[0].title(),
                fit_result[0].title()
            ],
            "Confidence": [
                f"{type_result[1]*100:.0f}%",
                f"{pattern_result[1]*100:.0f}%",
                f"{formality_result[1]*100:.0f}%",
                f"{season_result[1]*100:.0f}%",
                f"{material_result[1]*100:.0f}%",
                f"{fit_result[1]*100:.0f}%"
            ]
        }
        st.table(summary)
        
    elif not uploaded:
        st.info("� Upload an image and click 'Analyze All' to see results")
        
        # Show what will be detected
        st.subheader("📊 Attributes Detected")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("**👕 Type** (18 types)")
            st.caption("t-shirt, jeans, dress, etc.")
            st.write("**🔲 Pattern** (9 types)")
            st.caption("solid, striped, floral, etc.")
        with c2:
            st.write("**� Formality** (5 levels)")
            st.caption("casual → formal")
            st.write("**❄️ Season** (3 levels)")
            st.caption("summer → winter")
        with c3:
            st.write("**� Material** (8 types)")
            st.caption("cotton, denim, leather, etc.")
            st.write("**� Fit** (5 types)")
            st.caption("tight → oversized")
