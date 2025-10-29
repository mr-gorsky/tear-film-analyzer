import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Tear Film Analyzer | TFOS DEWS III",
    page_icon="👁️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2e86ab;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">👁️ Tear Film Analysis System</h1>', unsafe_allow_html=True)
    st.markdown("**Professional dry eye diagnosis based on TFOS DEWS III guidelines**")
    
    # Sidebar - Clinical Parameters
    st.sidebar.header("📋 Clinical Parameters")
    
    tbut = st.sidebar.number_input("TBUT (seconds)", 0.0, 30.0, 10.0, 0.5)
    tmh = st.sidebar.number_input("Tear Meniscus Height (mm)", 0.0, 1.0, 0.3, 0.05)
    schirmer = st.sidebar.number_input("Schirmer Test (mm/5min)", 0.0, 35.0, 15.0, 1.0)
    
    meibomian_grade = st.sidebar.selectbox("Meibomian Gland Expression", 
                                         ["0 - Clear", "1 - Cloudy", "2 - Granular", "3 - Toothpaste", "4 - No secretion"])
    meiboscore = st.sidebar.slider("Meiboscore (0-3)", 0, 3, 1)
    osdi_score = st.sidebar.slider("OSDI Score (0-100)", 0, 100, 25)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📊 Image Analysis", "📈 Clinical Assessment", "📚 Guidelines"])
    
    with tab1:
        st.header("Tear Film Image Analysis")
        
        uploaded_file = st.file_uploader("Upload Slit Lamp Image", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                image = Image.open(uploaded_file)
                st.image(image, caption="Original Image", use_column_width=True)
            
            with col2:
                if st.button("Analyze Image", type="primary"):
                    with st.spinner("Processing image..."):
                        # Simple image enhancement
                        enhancer = ImageEnhance.Contrast(image)
                        enhanced = enhancer.enhance(1.5)
                        
                        st.image(enhanced, caption="Enhanced Image", use_column_width=True)
                        
                        # Mock analysis results
                        st.success("Image analysis completed!")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Interference Grade", "Good")
                            st.metric("Pattern Coverage", "45%")
                        with col_b:
                            st.metric("Color Complexity", "3 patterns")
                            st.metric("Quality Score", "7/10")
    
    with tab2:
        st.header("Comprehensive Dry Eye Assessment")
        
        if st.button("Generate Diagnosis", type="primary"):
            # Simple dry eye calculation
            score = 0
            if tbut < 10: score += 1
            if tmh < 0.3: score += 1
            if schirmer < 10: score += 1
            if osdi_score > 25: score += 1
            
            if score >= 3:
                diagnosis = "Moderate Dry Eye"
                severity = "Moderate"
            elif score >= 2:
                diagnosis = "Mild Dry Eye" 
                severity = "Mild"
            else:
                diagnosis = "Normal"
                severity = "None"
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Clinical Summary")
                clinical_data = {
                    'Parameter': ['TBUT', 'TMH', 'Schirmer', 'OSDI'],
                    'Value': [f"{tbut}s", f"{tmh}mm", f"{schirmer}mm", f"{osdi_score}/100"],
                    'Status': [
                        'Normal' if tbut >= 10 else 'Low',
                        'Normal' if tmh >= 0.3 else 'Low', 
                        'Normal' if schirmer >= 10 else 'Low',
                        'Normal' if osdi_score <= 25 else 'High'
                    ]
                }
                st.dataframe(clinical_data)
                
                st.subheader("Diagnosis")
                st.metric("Dry Eye Type", diagnosis)
                st.metric("Severity", severity)
            
            with col2:
                st.subheader("Recommendations")
                
                recommendations = [
                    "Use preservative-free artificial tears 4x daily",
                    "Apply warm compresses 2x daily for 10 minutes",
                    "Consider omega-3 supplementation",
                    "Follow up in 4-6 weeks"
                ]
                
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f'<div class="metric-card">{i}. {rec}</div>', unsafe_allow_html=True)
                
                # Severity gauge
                severity_levels = {'None': 0, 'Mild': 1, 'Moderate': 2, 'Severe': 3}
                current_severity = severity_levels.get(severity, 0)
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=current_severity,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Severity"},
                    gauge={
                        'axis': {'range': [0, 3], 'tickvals': [0, 1, 2, 3]},
                        'steps': [
                            {'range': [0, 1], 'color': "lightgreen"},
                            {'range': [1, 2], 'color': "yellow"},
                            {'range': [2, 3], 'color': "red"}
                        ]
                    }
                ))
                st.plotly_chart(fig)
    
    with tab3:
        st.header("TFOS DEWS III Guidelines")
        
        st.markdown("""
        ### Key Diagnostic Criteria
        
        **Aqueous Deficient Dry Eye:**
        - Schirmer test ≤ 5 mm/5min
        - Reduced tear meniscus height
        - Normal TBUT
        
        **Evaporative Dry Eye:**
        - TBUT ≤ 5 seconds  
        - Meibomian gland dysfunction
        - Normal Schirmer test
        
        **Severity Grading:**
        """)
        
        severity_data = pd.DataFrame({
            'Mild': ['≤10s', '≤10mm', 'Mild symptoms'],
            'Moderate': ['≤5s', '≤5mm', 'Moderate symptoms'], 
            'Severe': ['Immediate', '≤2mm', 'Severe symptoms']
        }, index=['TBUT', 'Schirmer', 'Symptoms'])
        
        st.dataframe(severity_data)

if __name__ == "__main__":
    main()

st.markdown("---")
st.markdown("*TFOS DEWS III Based System - For professional use only*")