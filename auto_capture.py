# auto_capture.py - Auto-Capture Clothing Detection
"""
Automatically captures and classifies clothing when detected.
Uses periodic camera snapshots with CLIP detection.

Run: streamlit run auto_capture.py
"""

import streamlit as st
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
from sklearn.cluster import KMeans
import numpy as np
import time
import os
from datetime import datetime

st.set_page_config(page_title="Auto Capture", page_icon="📷", layout="wide")

# ===== MODEL =====
@st.cache_resource
def load_model():
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return model, processor

# ===== DETECTION FUNCTIONS =====
def is_clothing(model, processor, image, threshold=0.6):
    """Check if image contains clothing"""
    labels = [
        "a photo of clothing or a garment",
        "a photo of a person wearing clothes",
        "a photo of an empty room or background",
        "a photo of a random object",
        "a photo of furniture",
        "a blurry or unclear photo"
    ]
    
    inputs = processor(text=labels, images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        probs = model(**inputs).logits_per_image.softmax(dim=1)[0]
    
    # Check if clothing-related labels win
    clothing_prob = probs[0].item() + probs[1].item()
    best_idx = probs.argmax().item()
    
    is_cloth = best_idx in [0, 1] and clothing_prob > threshold
    return is_cloth, clothing_prob, labels[best_idx]

def classify_clothing(model, processor, image):
    """Full classification"""
    types = ["t-shirt", "shirt", "jeans", "trousers", "shorts", "dress", 
             "sneakers", "formal shoes", "jacket", "sweater", "hoodie", "skirt"]
    
    inputs = processor(text=[f"a photo of a {t}" for t in types], images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        probs = model(**inputs).logits_per_image.softmax(dim=1)[0]
    best_idx = probs.argmax().item()
    
    return types[best_idx], probs[best_idx].item()

def extract_colors(image, n=2):
    """Extract dominant colors"""
    img = image.copy()
    img.thumbnail((100, 100))
    pixels = np.array(img).reshape(-1, 3)
    kmeans = KMeans(n_clusters=n, random_state=42, n_init=10).fit(pixels)
    colors = ['#{:02x}{:02x}{:02x}'.format(*c.astype(int)) for c in kmeans.cluster_centers_]
    return colors

# ===== UI =====
st.title("📷 Auto-Capture Clothing Detection")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Camera")
    
    # Settings
    confidence_threshold = st.slider("Detection Confidence", 0.5, 0.9, 0.65, 0.05)
    auto_save = st.checkbox("Auto-save detected clothing", value=True)
    
    st.divider()
    
    # Camera input
    st.info("📸 Point camera at a clothing item and hold steady")
    camera_image = st.camera_input("Take photo when ready", key="camera")
    
    if camera_image:
        image = Image.open(camera_image).convert('RGB')
        
        # Load model and check
        model, processor = load_model()
        
        with st.spinner("🔍 Checking for clothing..."):
            is_cloth, confidence, detected = is_clothing(model, processor, image, confidence_threshold)
        
        if is_cloth:
            st.success(f"✅ Clothing Detected! ({confidence*100:.0f}% confidence)")
            
            # Classify
            with st.spinner("🤖 Classifying..."):
                clothing_type, type_conf = classify_clothing(model, processor, image)
                colors = extract_colors(image)
            
            # Display results
            st.metric("Type", clothing_type.title(), f"{type_conf*100:.0f}%")
            
            # Colors
            color_html = '<div style="display:flex;gap:10px;">'
            for c in colors:
                color_html += f'<div style="width:40px;height:40px;background:{c};border-radius:8px;border:2px solid #333;"></div>'
                color_html += f'<span>{c}</span>'
            color_html += '</div>'
            st.markdown(color_html, unsafe_allow_html=True)
            
            # Auto-save
            if auto_save:
                os.makedirs('wardrobe_images', exist_ok=True)
                save_path = f"wardrobe_images/auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                image.save(save_path)
                st.success(f"💾 Saved to: `{save_path}`")
                
                # Store in session for later
                if 'captured_items' not in st.session_state:
                    st.session_state.captured_items = []
                st.session_state.captured_items.append({
                    'path': save_path,
                    'type': clothing_type,
                    'colors': colors,
                    'confidence': type_conf
                })
        else:
            st.warning(f"❌ No clothing detected ({detected})")
            st.caption(f"Confidence: {confidence*100:.0f}% (need >{confidence_threshold*100:.0f}%)")

with col2:
    st.subheader("Captured Items")
    
    if 'captured_items' in st.session_state and st.session_state.captured_items:
        items = st.session_state.captured_items
        st.write(f"**{len(items)} items captured**")
        
        for i, item in enumerate(reversed(items[-6:])):  # Show last 6
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1:
                    if os.path.exists(item['path']):
                        st.image(item['path'], width=100)
                with c2:
                    st.write(f"**{item['type'].title()}**")
                    st.caption(f"Confidence: {item['confidence']*100:.0f}%")
                    st.caption(f"Colors: {', '.join(item['colors'])}")
                st.divider()
        
        if st.button("🗑️ Clear All"):
            st.session_state.captured_items = []
            st.rerun()
    else:
        st.info("No items captured yet. Point camera at clothing!")

# Tips
st.divider()
st.subheader("💡 Tips for Best Results")
col1, col2, col3 = st.columns(3)
with col1:
    st.write("**Good Lighting**")
    st.caption("Well-lit, no shadows")
with col2:
    st.write("**Plain Background**")
    st.caption("Solid color behind item")
with col3:
    st.write("**Full Item Visible**")
    st.caption("Show entire garment")
