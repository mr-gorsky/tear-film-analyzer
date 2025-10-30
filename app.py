import streamlit as st
import numpy as np
from PIL import Image
import io

def analyze_interferometric_colors(image):
    """Analyzes interferometric colors from image"""
    img_array = np.array(image)
    
    # Analiza bez OpenCV - koristimo numpy
    r_mean = np.mean(img_array[:,:,0])
    g_mean = np.mean(img_array[:,:,1]) 
    b_mean = np.mean(img_array[:,:,2])
    
    # Računamo "saturaciju" preko standardne devijacije
    color_variance = np.std(img_array)
    
    # Različite interpretacije za različite slike
    if color_variance < 30:
        interpretation = "Low interference pattern - possible dry eye condition"
    elif r_mean > g_mean and r_mean > b_mean:
        interpretation = "Yellow-orange interference - moderate dryness"
    else:
        interpretation = "Diverse interference colors - good tear film status"
    
    return interpretation

def analyze_fluo_test(image):
    """Analyzes fluorescein test"""
    img_array = np.array(image)
    
    # Grayscale bez OpenCV
    gray = np.mean(img_array, axis=2)
    
    brightness_mean = np.mean(gray)
    brightness_std = np.std(gray)
    
    # Različite interpretacije za različite slike
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
    
    # Preporuke ovise o stvarnim rezultatima
    if "dry" in interpretation_interf.lower() or "moderate" in interpretation_interf.lower():
        recommendations.append("Regular application of artificial tears")
        recommendations.append("Avoid prolonged screen time")
    
    if "dry" in interpretation_fluo.lower() or "uneven" in interpretation_fluo.lower():
        recommendations.append("Environmental control (air humidity)")
        recommendations.append("Increase fluid intake")
    
    if not recommendations:
        recommendations = ["Tear film condition appears satisfactory", "Regular ophthalmological check-ups recommended"]
    
    return recommendations

# Main app
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