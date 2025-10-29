import streamlit as st
import cv2
import numpy as np
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from utils.image_processing import analyze_tear_film_interference, detect_corneal_staining
from utils.tear_analysis import calculate_dry_eye_type, get_recommendations, analyze_tear_meniscus

# Page configuration
st.set_page_config(
    page_title="Tear Film Analyzer | TFOS DEWS III",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e86ab;
        border-bottom: 2px solid #2e86ab;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2e86ab;
        margin: 0.5rem 0;
    }
    .recommendation-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">👁️ Tear Film Analysis System</h1>', unsafe_allow_html=True)
    st.markdown("""
    **Professional dry eye diagnosis based on TFOS DEWS III guidelines (June 2025)**
    
    This system analyzes tear film characteristics through slit lamp photography and clinical parameters 
    to provide comprehensive dry eye assessment and treatment recommendations.
    """)
    
    # Sidebar for clinical data input
    st.sidebar.markdown('<h2 style="color: #1f77b4;">📋 Clinical Parameters</h2>', unsafe_allow_html=True)
    
    # Clinical parameters input
    with st.sidebar.expander("Tear Film Parameters", expanded=True):
        tbut = st.number_input("TBUT (seconds)", min_value=0.0, max_value=30.0, value=10.0, step=0.5,
                              help="Tear Break-Up Time - normal > 10 seconds")
        tmh = st.number_input("Tear Meniscus Height (mm)", min_value=0.0, max_value=1.0, value=0.3, step=0.05,
                             help="Normal range: 0.2-0.3 mm")
        schirmer = st.number_input("Schirmer Test (mm/5min)", min_value=0.0, max_value=35.0, value=15.0, step=1.0,
                                  help="Without anesthesia - normal > 10 mm/5min")
    
    with st.sidebar.expander("Meibomian Gland Assessment", expanded=True):
        meibomian_grade = st.selectbox("Meibomian Gland Expression", 
                                      ["0 - Clear", "1 - Cloudy", "2 - Granular", "3 - Toothpaste", "4 - No secretion"],
                                      help="Quality of meibum expression")
        meiboscore = st.slider("Meiboscore (0-3)", 0, 3, 1,
                              help="0=no loss, 1=≤25%, 2=26-50%, 3=>50% gland dropout")
    
    with st.s.sidebar.expander("Questionnaire Scores", expanded=True):
        osdi_score = st.slider("OSDI Score (0-100)", 0, 100, 25,
                              help="Ocular Surface Disease Index")
        deq5_score = st.slider("DEQ-5 Score (0-22)", 0, 22, 8,
                              help="Dry Eye Questionnaire-5")
    
    with st.sidebar.expander("Additional Findings"):
        corneal_staining = st.selectbox("Corneal Staining (Oxford Scale)",
                                       ["0 - None", "I - Mild", "II - Moderate", "III - Marked", "IV - Severe", "V - Extreme"])
        conjunctival_staining = st.selectbox("Conjunctival Staining (Oxford Scale)",
                                           ["0 - None", "I - Mild", "II - Moderate", "III - Marked", "IV - Severe", "V - Extreme"])
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Image Analysis", "🎯 Staining Assessment", "📈 Comprehensive Report", "📚 Guidelines"])
    
    with tab1:
        st.markdown('<h2 class="section-header">Tear Film Interference Pattern Analysis</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            uploaded_file = st.file_uploader("Upload Slit Lamp Tear Film Image", 
                                           type=['jpg', 'jpeg', 'png'],
                                           help="Upload a high-quality image of tear film interference patterns")
            
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Original Slit Lamp Image", use_column_width=True)
                
                # Analysis options
                analysis_type = st.radio("Analysis Type", 
                                       ["Interference Pattern Analysis", "Tear Meniscus Assessment"])
        
        with col2:
            if uploaded_file is not None and st.button("🔍 Analyze Tear Film", type="primary"):
                with st.spinner("Analyzing tear film characteristics..."):
                    if analysis_type == "Interference Pattern Analysis":
                        analysis_result = analyze_tear_film_interference(np.array(image))
                        
                        if analysis_result:
                            st.image(analysis_result['enhanced_image'], 
                                    caption="Enhanced Interference Pattern", 
                                    use_column_width=True)
                            
                            # Display results in metrics
                            st.markdown("### Analysis Results")
                            col_a, col_b, col_c = st.columns(3)
                            
                            with col_a:
                                st.metric("Interference Grade", analysis_result['interference_grade'])
                            with col_b:
                                st.metric("Color Complexity", f"{analysis_result['color_count']} patterns")
                            with col_c:
                                st.metric("Pattern Coverage", f"{analysis_result['total_color_percentage']:.1f}%")
                            
                            # Color distribution chart
                            if analysis_result['color_distribution']:
                                fig = px.pie(values=list(analysis_result['color_distribution'].values()),
                                           names=list(analysis_result['color_distribution'].keys()),
                                           title="Interference Color Distribution")
                                st.plotly_chart(fig)
    
    with tab2:
        st.markdown('<h2 class="section-header">Corneal and Conjunctival Staining Assessment</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            staining_file = st.file_uploader("Upload Staining Image", 
                                           type=['jpg', 'jpeg', 'png'], 
                                           key="staining",
                                           help="Upload fluorescein or lissamine green staining image")
            
            if staining_file is not None:
                image = Image.open(staining_file)
                st.image(image, caption="Original Staining Image", use_column_width=True)
        
        with col2:
            if staining_file is not None and st.button("🔍 Analyze Staining", type="primary"):
                with st.spinner("Detecting corneal staining patterns..."):
                    staining_result = detect_corneal_staining(np.array(image))
                    
                    if staining_result:
                        st.image(staining_result['detected_areas'], 
                                caption="Detected Staining Areas", 
                                use_column_width=True)
                        
                        # Staining analysis results
                        st.markdown("### Staining Assessment")
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric("Staining Grade", staining_result['staining_grade'])
                        with col_b:
                            st.metric("Damage Area", f"{staining_result['damage_percentage']:.1f}%")
                        with col_c:
                            st.metric("Lesion Count", staining_result['contour_count'])
                        
                        # Interpretation
                        if staining_result['damage_percentage'] > 15:
                            st.markdown('<div class="warning-box">⚠️ <strong>Significant corneal damage detected</strong> - Consider immediate ophthalmological evaluation</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<h2 class="section-header">Comprehensive Dry Eye Assessment</h2>', unsafe_allow_html=True)
        
        if st.button("🔄 Generate Complete Analysis", type="primary"):
            with st.spinner("Generating comprehensive diagnosis..."):
                # Analyze all parameters
                tmh_analysis = analyze_tear_meniscus(tmh)
                
                # Convert meibomian grade to numerical value
                meibomian_numeric = int(meibomian_grade.split(" - ")[0])
                
                # Comprehensive dry eye analysis
                dry_eye_analysis = calculate_dry_eye_type(
                    tbut=tbut,
                    tmh=tmh,
                    schirmer=schirmer,
                    meibomian_grade=meibomian_numeric,
                    meiboscore=meiboscore,
                    osdi_score=osdi_score,
                    deq5_score=deq5_score,
                    corneal_staining=corneal_staining,
                    conjunctival_staining=conjunctival_staining
                )
                
                # Get recommendations
                recommendations = get_recommendations(dry_eye_analysis)
                
                # Display results in a comprehensive layout
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 📋 Clinical Summary")
                    
                    # Parameters table
                    clinical_data = pd.DataFrame({
                        'Parameter': ['TBUT', 'Tear Meniscus Height', 'Schirmer Test', 
                                    'Meibomian Grade', 'Meiboscore', 'OSDI', 'DEQ-5'],
                        'Value': [f"{tbut} s", f"{tmh} mm", f"{schirmer} mm/5min", 
                                meibomian_grade, f"{meiboscore}/3", f"{osdi_score}/100", f"{deq5_score}/22"],
                        'Status': [
                            'Normal' if tbut >= 10 else 'Abnormal',
                            tmh_analysis['status'],
                            'Normal' if schirmer >= 10 else 'Abnormal',
                            'Normal' if meibomian_numeric <= 1 else 'Abnormal',
                            'Normal' if meiboscore <= 1 else 'Abnormal',
                            'Normal' if osdi_score <= 22 else 'Abnormal',
                            'Normal' if deq5_score <= 6 else 'Abnormal'
                        ]
                    })
                    st.dataframe(clinical_data, use_container_width=True)
                    
                    # Dry eye type visualization
                    st.markdown("### 🎯 Diagnosis")
                    
                    col_diag1, col_diag2 = st.columns(2)
                    with col_diag1:
                        st.metric("Dry Eye Type", dry_eye_analysis['dry_eye_type'])
                    with col_diag2:
                        st.metric("Severity Level", dry_eye_analysis['severity'])
                    
                    # Severity gauge
                    severity_levels = {'None': 0, 'Mild': 1, 'Moderate': 2, 'Severe': 3}
                    current_severity = severity_levels.get(dry_eye_analysis['severity'], 0)
                    
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number+delta",
                        value = current_severity,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Disease Severity"},
                        gauge = {
                            'axis': {'range': [0, 3], 'tickvals': [0, 1, 2, 3], 'ticktext': ['None', 'Mild', 'Moderate', 'Severe']},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 1], 'color': "lightgreen"},
                                {'range': [1, 2], 'color': "yellow"},
                                {'range': [2, 3], 'color': "red"}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.75,
                                'value': current_severity
                            }
                        }
                    ))
                    fig_gauge.update_layout(height=300)
                    st.plotly_chart(fig_gauge, use_container_width=True)
                
                with col2:
                    st.markdown("### 💡 Treatment Recommendations")
                    
                    for i, recommendation in enumerate(recommendations, 1):
                        st.markdown(f'<div class="recommendation-box"><strong>{i}.</strong> {recommendation}</div>', unsafe_allow_html=True)
                    
                    # Additional guidance
                    st.markdown("### 📖 TFOS DEWS III Guidance")
                    st.info("""
                    **Based on TFOS DEWS III 2025 Guidelines:**
                    - Dry eye is a multifactorial disease characterized by loss of homeostasis
                    - Core mechanism involves tear film instability and hyperosmolarity
                    - Inflammation plays key role in disease pathogenesis
                    - Treatment should be tailored to disease subtype and severity
                    """)
    
    with tab4:
        st.markdown('<h2 class="section-header">TFOS DEWS III Guidelines Reference</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        ### Key Diagnostic Criteria (TFOS DEWS III 2025)
        
        #### 1. Dry Eye Subtypes
        **Aqueous Deficient Dry Eye (ADDE):**
        - Schirmer test ≤ 5 mm/5min (without anesthesia)
        - Reduced tear meniscus height (< 0.2 mm)
        - Increased tear osmolarity
        
        **Evaporative Dry Eye (EDE):**
        - TBUT ≤ 5 seconds
        - Meibomian gland dysfunction
        - Normal Schirmer test
        
        **Mixed Dry Eye:**
        - Features of both ADDE and EDE
        
        #### 2. Severity Grading
        """)
        
        severity_data = pd.DataFrame({
            'Severity': ['Mild', 'Moderate', 'Severe'],
            'TBUT': ['≤10s', '≤5s', 'Immediate'],
            'Schirmer': ['≤10mm', '≤5mm', '≤2mm'],
            'Corneal Staining': ['Mild & transient', 'Moderate marked', 'Severe persistent'],
            'Symptoms': ['Mild & episodic', 'Moderate chronic', 'Severe constant']
        })
        st.dataframe(severity_data, use_container_width=True)
        
        st.markdown("""
        #### 3. Diagnostic Workflow
        1. **Step 1:** Symptom assessment (OSDI/DEQ-5)
        2. **Step 2:** Tear film stability (TBUT)
        3. **Step 3:** Tear volume assessment (TMH/Schirmer)
        4. **Step 4:** Ocular surface damage (staining)
        5. **Step 5:** Meibomian gland evaluation
        
        *Reference: TFOS DEWS III Diagnostic Methodology Report, June 2025*
        """)

if __name__ == "__main__":
    main()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p><strong>TFOS DEWS III Based Tear Film Analysis System</strong></p>
    <p><em>For professional use only. Final diagnosis and treatment decisions should be made by qualified ophthalmologists.</em></p>
    <p>Reference: TFOS DEWS III Reports, June 2025</p>
</div>
""", unsafe_allow_html=True)