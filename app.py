import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

def analyze_interferometric_colors(image):
    """Analyzes interferometric colors from image"""
    img_array = np.array(image)
    hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
    
    hue_mean = np.mean(hsv[:,:,0])
    saturation_mean = np.mean(hsv[:,:,1])
    value_mean = np.mean(hsv[:,:,2])
    
    # SAMO OVO MIJENJAM - da interpretacija ovisi o stvarnoj slici
    if saturation_mean < 50:
        interpretation = "Low interference pattern - possible dry eye condition"
    elif hue_mean < 30:
        interpretation = "Yellow-orange interference - moderate dryness"
    else:
        interpretation = "Diverse interference colors - good tear film status"
    
    return interpretation

def analyze_fluo_test(image):
    """Analyzes fluorescein test"""
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    brightness_mean = np.mean(gray)
    brightness_std = np.std(gray)
    
    # SAMO OVO MIJENJAM - da interpretacija ovisi o stvarnoj slici
    if brightness_mean < 100:
        interpretation = "Weak fluorescein response - possible dry eye"
    elif brightness_std > 50:
        interpretation = "Uneven dye distribution - ocular surface issues"
    else:
        interpretation = "Even fluorescein distribution - normal test result"
    
    return interpretation

def get_recommendations(interpretation_interf, interpretation_fluo):
    """Generates recommendations based on both analyses"""
    recommendations = []
    
    # SAMO OVO MIJENJAM - da preporuke ovise o stvarnim rezultatima
    if "dry" in interpretation_interf.lower() or "moderate" in interpretation_interf.lower():
        recommendations.append("Regular application of artificial tears")
        recommendations.append("Avoid prolonged screen time")
    
    if "dry" in interpretation_fluo.lower() or "uneven" in interpretation_fluo.lower():
        recommendations.append("Environmental control (air humidity)")
        recommendations.append("Increase fluid intake")
    
    if not recommendations:
        recommendations = ["Tear film condition appears satisfactory", "Regular ophthalmological check-ups recommended"]
    
    return recommendations

# Main app - SVE OSTO OSTAJE POTPUNO ISTO KAO U VAŠEM ORIGINALNOM KODU
st.title("Tear Film Analyzer")

uploaded_file_interf = st.file_uploader("Upload interference colors image", type=['jpg', 'jpeg', 'png'])
uploaded_file_fluo = st.file_uploader("Upload fluorescein test image", type=['jpg', 'jpeg', 'png'])

if uploaded_file_interf is not None:
    image_interf = Image.open(uploaded_file_interf)
    st.image(image_interf, caption="Uploaded Image - Interference Colors", use_column_width=True)
    
    with st.spinner('Analyzing interference colors...'):
        interpretation_interf = analyze_interferometric_colors(image_interf)
        st.subheader("Interference Colors Interpretation:")
        st.write(interpretation_interf)

if uploaded_file_fluo is not None:
    image_fluo = Image.open(uploaded_file_fluo)
    st.image(image_fluo, caption="Uploaded Image - Fluorescein Test", use_column_width=True)
    
    with st.spinner('Analyzing fluorescein test...'):
        interpretation_fluo = analyze_fluo_test(image_fluo)
        st.subheader("Fluorescein Test Interpretation:")
        st.write(interpretation_fluo)

if uploaded_file_interf is not None and uploaded_file_fluo is not None:
    st.subheader("Recommendations:")
    recommendations = get_recommendations(interpretation_interf, interpretation_fluo)
    for rec in recommendations:
        st.write(f"• {rec}")