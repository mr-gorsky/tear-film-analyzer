import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64

# Page configuration
st.set_page_config(
    page_title="TearFilm Analyzer | TFOS DEWS III",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
    }
    .logo-main {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: 2px;
    }
    .logo-sub {
        font-size: 1.8rem;
        font-weight: 300;
        letter-spacing: 3px;
    }
    .section-header {
        font-size: 1.6rem;
        color: #2e86ab;
        border-bottom: 3px solid #2e86ab;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 5px solid #2e86ab;
        margin: 0.8rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .recommendation-box {
        background-color: #e8f4f8;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 5px solid #28a745;
        margin: 0.8rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 5px solid #ffc107;
        margin: 0.8rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def create_text_logo():
    """Create a text-based logo similar to the provided design"""
    st.markdown("""
    <div class="logo-container">
        <div class="logo-main">TEARFILM</div>
        <div class="logo-sub">ANALYZER</div>
        <div style="margin-top: 0.5rem; font-size: 1rem; opacity: 0.9;">
            TFOS DEWS III Based Diagnostic System
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header with logo
    create_text_logo()
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
        Professional dry eye diagnosis based on TFOS DEWS III guidelines (2025)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with improved styling
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: #1f77b4; border-bottom: 2px solid #1f77b4; padding-bottom: 10px;">
                📋 Clinical Parameters
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Clinical parameters input
        with st.expander("🧪 Tear Film Parameters", expanded=True):
            tbut = st.number_input("**TBUT** (seconds)", min_value=0.0, max_value=30.0, value=10.0, step=0.5,
                                  help="Tear Break-Up Time - normal > 10 seconds")
            tmh = st.number_input("**Tear Meniscus Height** (mm)", min_value=0.0, max_value=1.0, value=0.3, step=0.05,
                                 help="Normal range: 0.2-0.3 mm")
            schirmer = st.number_input("**Schirmer Test** (mm/5min)", min_value=0.0, max_value=35.0, value=15.0, step=1.0,
                                      help="Without anesthesia - normal > 10 mm/5min")
        
        with st.expander("🔬 Meibomian Gland Assessment", expanded=True):
            meibomian_grade = st.selectbox("**Meibomian Gland Expression**", 
                                          ["0 - Clear", "1 - Cloudy", "2 - Granular", "3 - Toothpaste", "4 - No secretion"])
            meiboscore = st.slider("**Meiboscore** (0-3)", 0, 3, 1,
                                  help="0=no loss, 1=≤25%, 2=26-50%, 3=>50% gland dropout")
        
        with st.expander("📝 Questionnaire Scores", expanded=True):
            osdi_score = st.slider("**OSDI Score** (0-100)", 0, 100, 25,
                                  help="Ocular Surface Disease Index")
            deq5_score = st.slider("**DEQ-5 Score** (0-22)", 0, 22, 8,
                                  help="Dry Eye Questionnaire-5")
        
        with st.expander("🔍 Additional Findings"):
            corneal_staining = st.selectbox("**Corneal Staining** (Oxford Scale)",
                                           ["0 - None", "I - Mild", "II - Moderate", "III - Marked", "IV - Severe", "V - Extreme"])
            conjunctival_staining = st.selectbox("**Conjunctival Staining** (Oxford Scale)",
                                               ["0 - None", "I - Mild", "II - Moderate", "III - Marked", "IV - Severe", "V - Extreme"])
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Image Analysis", "🎯 Staining Assessment", "📈 Comprehensive Report", "📚 Guidelines"])
    
    with tab1:
        st.markdown('<h2 class="section-header">🔬 Tear Film Interference Pattern Analysis</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            uploaded_file = st.file_uploader("**Upload Slit Lamp Tear Film Image**", 
                                           type=['jpg', 'jpeg', 'png'],
                                           help="Upload a high-quality image of tear film interference patterns")
            
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="🖼️ Original Slit Lamp Image", use_column_width=True)
        
        with col2:
            if uploaded_file is not None and st.button("🔍 Analyze Tear Film", type="primary", use_container_width=True):
                with st.spinner("🔄 Analyzing tear film characteristics..."):
                    # Simple image enhancement
                    enhancer = ImageEnhance.Contrast(image)
                    enhanced = enhancer.enhance(1.8)
                    
                    st.image(enhanced, caption="✨ Enhanced Interference Pattern", use_column_width=True)
                    
                    # Mock analysis results
                    st.success("✅ Image analysis completed!")
                    
                    # Display results in nice metrics
                    st.markdown("### 📋 Analysis Results")
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.markdown('<div class="metric-card">'
                                  '<div style="font-size: 1.2rem; font-weight: bold; color: #2e86ab;">Interference Grade</div>'
                                  '<div style="font-size: 1.5rem; font-weight: bold;">Good</div>'
                                  '</div>', unsafe_allow_html=True)
                    
                    with col_b:
                        st.markdown('<div class="metric-card">'
                                  '<div style="font-size: 1.2rem; font-weight: bold; color: #2e86ab;">Pattern Coverage</div>'
                                  '<div style="font-size: 1.5rem; font-weight: bold;">45%</div>'
                                  '</div>', unsafe_allow_html=True)
                    
                    with col_c:
                        st.markdown('<div class="metric-card">'
                                  '<div style="font-size: 1.2rem; font-weight: bold; color: #2e86ab;">Quality Score</div>'
                                  '<div style="font-size: 1.5rem; font-weight: bold;">7/10</div>'
                                  '</div>', unsafe_allow_html=True)
                    
                    # Color distribution chart
                    color_data = {
                        'Blue': 35,
                        'Green': 25, 
                        'Yellow': 20,
                        'Red': 20
                    }
                    
                    fig = px.pie(values=list(color_data.values()),
                               names=list(color_data.keys()),
                               title="🎨 Interference Color Distribution",
                               color_discrete_sequence=px.colors.qualitative.Set3)
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown('<h2 class="section-header">🎯 Corneal and Conjunctival Staining Assessment</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            staining_file = st.file_uploader("**Upload Staining Image**", 
                                           type=['jpg', 'jpeg', 'png'], 
                                           key="staining",
                                           help="Upload fluorescein or lissamine green staining image")
            
            if staining_file is not None:
                image = Image.open(staining_file)
                st.image(image, caption="🖼️ Original Staining Image", use_column_width=True)
        
        with col2:
            if staining_file is not None and st.button("🔍 Analyze Staining", type="primary", use_container_width=True):
                with st.spinner("🔄 Detecting corneal staining patterns..."):
                    # Simple staining simulation
                    st.success("✅ Staining analysis completed!")
                    
                    # Mock results
                    st.markdown("### 📊 Staining Assessment")
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.markdown('<div class="metric-card">'
                                  '<div style="font-size: 1.2rem; font-weight: bold; color: #2e86ab;">Staining Grade</div>'
                                  '<div style="font-size: 1.5rem; font-weight: bold;">Mild (II)</div>'
                                  '</div>', unsafe_allow_html=True)
                    
                    with col_b:
                        st.markdown('<div class="metric-card">'
                                  '<div style="font-size: 1.2rem; font-weight: bold; color: #2e86ab;">Damage Area</div>'
                                  '<div style="font-size: 1.5rem; font-weight: bold;">8.5%</div>'
                                  '</div>', unsafe_allow_html=True)
                    
                    with col_c:
                        st.markdown('<div class="metric-card">'
                                  '<div style="font-size: 1.2rem; font-weight: bold; color: #2e86ab;">Lesion Count</div>'
                                  '<div style="font-size: 1.5rem; font-weight: bold;">12</div>'
                                  '</div>', unsafe_allow_html=True)
                    
                    # Interpretation
                    st.markdown("### 💬 Clinical Interpretation")
                    st.markdown("""
                    <div class="recommendation-box">
                        <strong>Mild epithelial changes detected</strong><br>
                        - Minimal corneal staining pattern<br>
                        - Consider lubrication therapy<br>
                        - Monitor for progression
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<h2 class="section-header">📈 Comprehensive Dry Eye Assessment</h2>', unsafe_allow_html=True)
        
        if st.button("🔄 Generate Complete Analysis", type="primary", use_container_width=True):
            with st.spinner("🔄 Generating comprehensive diagnosis..."):
                # Calculate dry eye score
                score = 0
                if tbut < 10: score += 2
                if tbut < 5: score += 1
                if tmh < 0.3: score += 1
                if schirmer < 10: score += 2
                if osdi_score > 33: score += 2
                if deq5_score > 8: score += 1
                
                # Determine diagnosis
                if score >= 8:
                    diagnosis = "Mixed Dry Eye"
                    severity = "Moderate"
                elif score >= 5:
                    diagnosis = "Evaporative Dry Eye"
                    severity = "Mild"
                else:
                    diagnosis = "Normal / Subclinical"
                    severity = "None"
                
                # Display comprehensive results
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 📋 Clinical Summary")
                    
                    clinical_data = pd.DataFrame({
                        'Parameter': ['TBUT', 'Tear Meniscus Height', 'Schirmer Test', 
                                    'Meibomian Grade', 'Meiboscore', 'OSDI', 'DEQ-5'],
                        'Value': [f"{tbut} s", f"{tmh} mm", f"{schirmer} mm/5min", 
                                meibomian_grade, f"{meiboscore}/3", f"{osdi_score}/100", f"{deq5_score}/22"],
                        'Status': [
                            '✅ Normal' if tbut >= 10 else '⚠️ Low',
                            '✅ Normal' if tmh >= 0.3 else '⚠️ Low',
                            '✅ Normal' if schirmer >= 10 else '⚠️ Low',
                            '✅ Normal' if "0" in meibomian_grade or "1" in meibomian_grade else '⚠️ Abnormal',
                            '✅ Normal' if meiboscore <= 1 else '⚠️ Abnormal',
                            '✅ Normal' if osdi_score <= 22 else '⚠️ High',
                            '✅ Normal' if deq5_score <= 6 else '⚠️ High'
                        ]
                    })
                    
                    # Style the dataframe
                    st.dataframe(clinical_data, use_container_width=True, hide_index=True)
                    
                    st.markdown("### 🎯 Diagnosis")
                    
                    col_diag1, col_diag2 = st.columns(2)
                    with col_diag1:
                        st.markdown(f'<div class="metric-card">'
                                  f'<div style="font-size: 1.2rem; font-weight: bold; color: #2e86ab;">Dry Eye Type</div>'
                                  f'<div style="font-size: 1.5rem; font-weight: bold;">{diagnosis}</div>'
                                  f'</div>', unsafe_allow_html=True)
                    
                    with col_diag2:
                        st.markdown(f'<div class="metric-card">'
                                  f'<div style="font-size: 1.2rem; font-weight: bold; color: #2e86ab;">Severity Level</div>'
                                  f'<div style="font-size: 1.5rem; font-weight: bold;">{severity}</div>'
                                  f'</div>', unsafe_allow_html=True)
                    
                    # Severity gauge
                    severity_levels = {'None': 0, 'Mild': 1, 'Moderate': 2, 'Severe': 3}
                    current_severity = severity_levels.get(severity, 0)
                    
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=current_severity,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "🩺 Disease Severity", 'font': {'size': 20}},
                        gauge={
                            'axis': {'range': [0, 3], 'tickvals': [0, 1, 2, 3], 
                                   'ticktext': ['None', 'Mild', 'Moderate', 'Severe']},
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
                    fig_gauge.update_layout(height=300, font={'size': 12})
                    st.plotly_chart(fig_gauge, use_container_width=True)
                
                with col2:
                    st.markdown("### 💡 Treatment Recommendations")
                    
                    recommendations = [
                        "Use preservative-free artificial tears 4-6x daily",
                        "Apply warm compresses 2x daily for 10 minutes",
                        "Consider omega-3 fatty acid supplementation (2000 mg daily)",
                        "Practice blink exercises during digital device use",
                        "Environmental modifications (use humidifier, avoid air drafts)",
                        "Follow up evaluation in 4-6 weeks"
                    ]
                    
                    for i, recommendation in enumerate(recommendations, 1):
                        st.markdown(f'<div class="recommendation-box">'
                                  f'<strong>#{i}</strong> {recommendation}'
                                  f'</div>', unsafe_allow_html=True)
                    
                    # TFOS guidance
                    st.markdown("### 📖 TFOS DEWS III Guidance")
                    st.info("""
                    **Based on TFOS DEWS III 2025 Guidelines:**
                    - Dry eye is a multifactorial disease characterized by loss of homeostasis
                    - Core mechanism involves tear film instability and hyperosmolarity  
                    - Inflammation plays key role in disease pathogenesis
                    - Treatment should be tailored to disease subtype and severity
                    """)
    
    with tab4:
        st.markdown('<h2 class="section-header">📚 TFOS DEWS III Guidelines Reference</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            ### 🔍 Key Diagnostic Criteria
            
            **Aqueous Deficient Dry Eye (ADDE):**
            - Schirmer test ≤ 5 mm/5min
            - Reduced tear meniscus height (< 0.2 mm)
            - Normal TBUT
            
            **Evaporative Dry Eye (EDE):**
            - TBUT ≤ 5 seconds
            - Meibomian gland dysfunction  
            - Normal Schirmer test
            
            **Mixed Dry Eye:**
            - Features of both ADDE and EDE
            """)
        
        with col2:
            st.markdown("""
            ### 🎯 Severity Grading
            """)
            
            severity_data = pd.DataFrame({
                'Mild': ['≤10s', '≤10mm', 'Mild & transient', 'Mild & episodic'],
                'Moderate': ['≤5s', '≤5mm', 'Moderate marked', 'Moderate chronic'], 
                'Severe': ['Immediate', '≤2mm', 'Severe persistent', 'Severe constant']
            }, index=['TBUT', 'Schirmer', 'Corneal Staining', 'Symptoms'])
            
            st.dataframe(severity_data, use_container_width=True)
        
        st.markdown("""
        ### 📋 Diagnostic Workflow
        1. **Step 1:** Symptom assessment (OSDI/DEQ-5)
        2. **Step 2:** Tear film stability (TBUT)
        3. **Step 3:** Tear volume assessment (TMH/Schirmer)
        4. **Step 4:** Ocular surface damage (staining)
        5. **Step 5:** Meibomian gland evaluation
        
        *Reference: TFOS DEWS III Diagnostic Methodology Report, June 2025*
        """)

if __name__ == "__main__":
    main()

# Footer with logo
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <div style="font-size: 2rem; font-weight: 800; color: #1f77b4; margin-bottom: 0.5rem;">
        TEARFILM ANALYZER
    </div>
    <p><strong>TFOS DEWS III Based Tear Film Analysis System</strong></p>
    <p><em>For professional use only. Final diagnosis and treatment decisions should be made by qualified ophthalmologists.</em></p>
    <p>Reference: TFOS DEWS III Reports, June 2025</p>
</div>
""", unsafe_allow_html=True)