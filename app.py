import streamlit as st
import numpy as np
from PIL import Image
import io

def analyze_interferometric_colors(image):
    """Analyzes interferometric colors from the image"""
    # Convert PIL Image to numpy array
    img_array = np.array(image)
    
    # Analyze colors using numpy (without OpenCV)
    # Calculate average RGB values
    r_mean = np.mean(img_array[:,:,0])
    g_mean = np.mean(img_array[:,:,1])
    b_mean = np.mean(img_array[:,:,2])
    
    # Calculate saturation via standard deviation
    saturation = np.std(img_array)
    
    # Generate interpretation based on analysis
    if saturation < 30:
        interpretation = "Low interference - possible dry eye"
    elif r_mean > g_mean and r_mean > b_mean:
        interpretation = "Yellow-orange interference colors - moderate dryness"
    else:
        interpretation = "Diverse interference colors - good tear film condition"
    
    return interpretation, r_mean, g_mean, b_mean, saturation

def analyze_fluo_test(image):
    """Analyzes fluorescein test"""
    img_array = np.array(image)
    
    # Convert to grayscale using numpy
    gray = np.mean(img_array, axis=2)
    
    # Analyze brightness and distribution
    brightness_mean = np.mean(gray)
    brightness_std = np.std(gray)
    
    if brightness_mean < 100:
        interpretation = "Weak fluorescein response - possible dry eye"
    elif brightness_std > 50:
        interpretation = "Uneven distribution - dry eye"
    else:
        interpretation = "Even distribution - normal fluorescein test"
    
    return interpretation, brightness_mean, brightness_std

def get_recommendations(interpretation_interf, interpretation_fluo):
    """Generates recommendations based on both analyses"""
    recommendations = []
    
    if "dry" in interpretation_interf.lower() or "dryness" in interpretation_interf.lower():
        recommendations.append("Regular application of artificial tears")
        recommendations.append("Avoid prolonged screen time")
        recommendations.append("Use air humidification in rooms")
    
    if "dry" in interpretation_fluo.lower() or "dryness" in interpretation_fluo.lower():
        recommendations.append("Environmental control (air humidity)")
        recommendations.append("Increase fluid intake")
        recommendations.append("Protective glasses in wind and sun")
    
    # Remove duplicates
    recommendations = list(set(recommendations))
    
    if not recommendations:
        recommendations = [
            "Tear film condition is satisfactory", 
            "Regular check-ups are recommended annually",
            "Continue good eye protection habits"
        ]
    
    return recommendations

# Main app
st.set_page_config(page_title="Tear Film Analyzer", page_icon="👁️", layout="wide")

st.title("👁️ Tear Film Analyzer")

st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for information
with st.sidebar:
    st.header("ℹ️ About the App")
    st.info("""
    This app analyzes tear film images through:
    - **Interference colors** - tear film quality
    - **Fluorescein test** - ocular surface integrity
    """)
    
    st.header("📝 Instructions")
    st.write("""
    1. Upload interference colors image
    2. Upload fluorescein test image  
    3. Review analysis results
    4. Follow recommendations
    """)

# Upload section
st.header("📤 Upload Images")

col1, col2 = st.columns(2)

with col1:
    uploaded_file_interf = st.file_uploader(
        "**Interference Colors**", 
        type=['jpg', 'jpeg', 'png'],
        key="interf",
        help="Upload interference colors image of tear film"
    )

with col2:
    uploaded_file_fluo = st.file_uploader(
        "**Fluorescein Test**", 
        type=['jpg', 'jpeg', 'png'], 
        key="fluo",
        help="Upload fluorescein test image"
    )

# Interference colors analysis
if uploaded_file_interf is not None:
    st.header("🔍 Interference Colors Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        image_interf = Image.open(uploaded_file_interf)
        st.image(image_interf, caption="Uploaded Image - Interference Colors", use_column_width=True)
    
    with col2:
        with st.spinner('Analyzing interference colors...'):
            interpretation_interf, r, g, b, saturation = analyze_interferometric_colors(image_interf)
            
            st.subheader("📊 Analysis Results:")
            st.success(f"**Interpretation:** {interpretation_interf}")
            
            # Show metrics
            with st.expander("Detailed Metrics"):
                st.write(f"**Average Red (R):** {r:.2f}")
                st.write(f"**Average Green (G):** {g:.2f}")
                st.write(f"**Average Blue (B):** {b:.2f}")
                st.write(f"**Saturation (std dev):** {saturation:.2f}")

# Fluorescein test analysis
if uploaded_file_fluo is not None:
    st.header("💡 Fluorescein Test Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        image_fluo = Image.open(uploaded_file_fluo)
        st.image(image_fluo, caption="Uploaded Image - Fluorescein Test", use_column_width=True)
    
    with col2:
        with st.spinner('Analyzing fluorescein test...'):
            interpretation_fluo, brightness, brightness_std = analyze_fluo_test(image_fluo)
            
            st.subheader("📊 Analysis Results:")
            st.success(f"**Interpretation:** {interpretation_fluo}")
            
            # Show metrics
            with st.expander("Detailed Metrics"):
                st.write(f"**Average Brightness:** {brightness:.2f}")
                st.write(f"**Standard Deviation:** {brightness_std:.2f}")

# Recommendations after diagnosis
if uploaded_file_interf is not None and uploaded_file_fluo is not None:
    st.header("💡 Recommendations After Diagnosis")
    
    recommendations = get_recommendations(interpretation_interf, interpretation_fluo)
    
    st.info("Based on the analysis of both images, we recommend the following:")
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")
    
    # Additional information
    with st.expander("ℹ️ Additional Information"):
        st.write("""
        **Note:** These recommendations are generated based on image analysis and should 
        be taken as guidelines. For complete diagnosis and treatment, always consult 
        with an ophthalmologist.
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Tear Film Analyzer © 2024 | For educational purposes"
    "</div>", 
    unsafe_allow_html=True
)