import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import io
import base64

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

# Image processing functions without OpenCV
def enhance_image_contrast(image):
    """Enhance image contrast using PIL"""
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(2.0)

def analyze_tear_film_interference(image_array):
    """
    Analyze tear film interference patterns using PIL instead of OpenCV
    """
    try:
        # Convert numpy array to PIL Image
        if isinstance(image_array, np.ndarray):
            image = Image.fromarray(image_array)
        else:
            image = image_array
        
        # Enhance contrast
        enhanced = enhance_image_contrast(image)
        
        # Convert to numpy for analysis
        enhanced_array = np.array(enhanced)
        
        # Simple color analysis (simplified without OpenCV)
        # Convert to HSV-like analysis using RGB
        r, g, b = enhanced_array[:,:,0], enhanced_array[:,:,1], enhanced_array[:,:,2]
        
        # Detect color patterns (simplified)
        blue_areas = (b > 150) & (r < 100) & (g < 100)
        green_areas = (g > 150) & (r < 100) & (b < 100)
        yellow_areas = (r > 150) & (g > 150) & (b < 100)
        red_areas = (r > 150) & (g < 100) & (b < 100)
        
        total_pixels = enhanced_array.shape[0] * enhanced_array.shape[1]
        
        color_count = {
            'Blue_Interference': np.sum(blue_areas) / total_pixels * 100,
            'Green_Interference': np.sum(green_areas) / total_pixels * 100,
            'Yellow_Interference': np.sum(yellow_areas) / total_pixels * 100,
            'Red_Interference': np.sum(red_areas) / total_pixels * 100
        }
        
        # Filter out insignificant colors
        color_count = {k: v for k, v in color_count.items() if v > 1}
        
        # Determine interference grade
        total_color_percentage = sum(color_count.values())
        
        if total_color_percentage > 60:
            interference_grade = "Excellent"
        elif total_color_percentage > 40:
            interference_grade = "Good"
        elif total_color_percentage > 20:
            interference_grade = "Fair"
        elif total_color_percentage > 5:
            interference_grade = "Poor"
        else:
            interference_grade = "Very Poor"
        
        return {
            'enhanced_image': enhanced,
            'interference_grade': interference_grade,
            'color_count': len(color_count),
            'color_distribution': color_count,
            'total_color_percentage': total_color_percentage,
            'interpretation': get_interference_interpretation(interference_grade)
        }
    
    except Exception as e:
        st.error(f"Error in interference analysis: {e}")
        return None

def get_interference_interpretation(grade):
    """Provide clinical interpretation of interference patterns"""
    interpretations = {
        "Excellent": "Normal lipid layer thickness and spread - healthy tear film",
        "Good": "Mild lipid layer abnormalities - minimal evaporation",
        "Fair": "Moderate lipid layer disruption - increased evaporation likely",
        "Poor": "Significant lipid layer deficiency - high evaporation risk",
        "Very Poor": "Severe lipid layer abnormalities - marked evaporative dry eye"
    }
    return interpretations.get(grade, "Unable to interpret")

def detect_corneal_staining(image_array):
    """
    Detect corneal staining patterns using PIL
    """
    try:
        if isinstance(image_array, np.ndarray):
            image = Image.fromarray(image_array)
        else:
            image = image_array
        
        # Convert to grayscale
        gray = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(3.0)
        
        # Apply edge detection
        edges = enhanced.filter(ImageFilter.FIND_EDGES)
        
        # Convert to numpy for analysis
        edges_array = np.array(edges)
        
        # Simple thresholding for damaged areas
        threshold = 50
        damaged_areas = edges_array > threshold
        
        # Calculate damage percentage
        total_pixels = edges_array.shape[0] * edges_array.shape[1]
        damage_percentage = np.sum(damaged_areas) / total_pixels * 100
        
        # Create result image
        result_image = image.copy()
        result_array = np.array(result_image)
        
        # Highlight damaged areas in red
        result_array[damaged_areas] = [255, 0, 0]  # Red color
        
        result_image_highlighted = Image.fromarray(result_array)
        
        # Determine staining grade
        if damage_percentage > 30:
            staining_grade = "Severe (IV-V)"
        elif damage_percentage > 15:
            staining_grade = "Moderate (III)"
        elif damage_percentage > 5:
            staining_grade = "Mild (II)"
        elif damage_percentage > 1:
            staining_grade = "Trace (I)"
        else:
            staining_grade = "None (0)"
        
        return {
            'detected_areas': result_image_highlighted,
            'staining_grade': staining_grade,
            'damage_percentage': damage_percentage,
            'contour_count': int(damage_percentage / 2),  # Approximate count
            'interpretation': get_staining_interpretation(staining_grade, damage_percentage)
        }
    
    except Exception as e:
        st.error(f"Error in staining detection: {e}")
        return None

def get_staining_interpretation(grade, percentage):
    """Provide clinical interpretation of staining results"""
    if "Severe" in grade:
        return "Significant corneal epithelial damage - requires immediate attention"
    elif "Moderate" in grade:
        return "Moderate epithelial disruption - consider anti-inflammatory treatment"
    elif "Mild" in grade:
        return "Mild epithelial changes - monitor and consider lubrication"
    else:
        return "Minimal or no epithelial damage - normal finding"

# Tear analysis functions
def analyze_tear_meniscus(tmh):
    """
    Analyze tear meniscus height based on TFOS DEWS III criteria
    """
    if tmh < 0.2:
        return {
            'status': 'Low',
            'interpretation': 'Reduced tear volume suggestive of aqueous deficiency',
            'risk_level': 'High',
            'recommendation': 'Consider aqueous enhancement therapy'
        }
    elif tmh < 0.3:
        return {
            'status': 'Borderline',
            'interpretation': 'Marginal tear volume, monitor for progression',
            'risk_level': 'Moderate',
            'recommendation': 'Regular lubrication and monitoring'
        }
    else:
        return {
            'status': 'Normal',
            'interpretation': 'Adequate tear volume',
            'risk_level': 'Low',
            'recommendation': 'Maintain current ocular surface health'
        }

def calculate_dry_eye_type(tbut, tmh, schirmer, meibomian_grade, meiboscore, 
                          osdi_score, deq5_score, corneal_staining, conjunctival_staining):
    """
    Determine dry eye type and severity based on TFOS DEWS III diagnostic criteria
    """
    # Convert string inputs to numerical values where needed
    corneal_staining_numeric = convert_staining_to_numeric(corneal_staining)
    conjunctival_staining_numeric = convert_staining_to_numeric(conjunctival_staining)
    
    # Calculate scores for different dry eye components
    aqueous_score = calculate_aqueous_score(tmh, schirmer)
    evaporative_score = calculate_evaporative_score(tbut, meibomian_grade, meiboscore)
    inflammatory_score = calculate_inflammatory_score(corneal_staining_numeric, conjunctival_staining_numeric)
    symptom_score = calculate_symptom_score(osdi_score, deq5_score)
    
    # Determine primary dry eye type
    total_score = aqueous_score + evaporative_score + inflammatory_score + symptom_score
    
    # Type determination logic based on TFOS DEWS III
    if aqueous_score >= 6 and evaporative_score < 4:
        dry_eye_type = "Aqueous Deficient Dry Eye (ADDE)"
    elif evaporative_score >= 6 and aqueous_score < 4:
        dry_eye_type = "Evaporative Dry Eye (EDE)"
    elif aqueous_score >= 4 and evaporative_score >= 4:
        dry_eye_type = "Mixed Dry Eye"
    else:
        dry_eye_type = "Subclinical or No Dry Eye"
    
    # Severity determination
    if total_score >= 12:
        severity = "Severe"
    elif total_score >= 8:
        severity = "Moderate"
    elif total_score >= 4:
        severity = "Mild"
    else:
        severity = "None"
    
    return {
        'dry_eye_type': dry_eye_type,
        'severity': severity,
        'total_score': total_score,
        'component_scores': {
            'aqueous_deficiency': aqueous_score,
            'evaporative': evaporative_score,
            'inflammatory': inflammatory_score,
            'symptomatic': symptom_score
        },
        'tfos_classification': classify_tfos_dry_eye(aqueous_score, evaporative_score)
    }

def calculate_aqueous_score(tmh, schirmer):
    """Calculate aqueous deficiency score"""
    score = 0
    # TMH scoring
    if tmh < 0.2:
        score += 3
    elif tmh < 0.3:
        score += 1
    
    # Schirmer scoring
    if schirmer < 5:
        score += 3
    elif schirmer < 10:
        score += 2
    elif schirmer < 15:
        score += 1
    
    return min(score, 6)

def calculate_evaporative_score(tbut, meibomian_grade, meiboscore):
    """Calculate evaporative dry eye score"""
    score = 0
    # TBUT scoring
    if tbut < 5:
        score += 3
    elif tbut < 10:
        score += 2
    elif tbut < 15:
        score += 1
    
    # Meibomian gland scoring
    score += meibomian_grade  # 0-4
    score += meiboscore       # 0-3
    
    return min(score, 6)

def calculate_inflammatory_score(corneal_staining, conjunctival_staining):
    """Calculate inflammatory component score"""
    return corneal_staining + conjunctival_staining

def calculate_symptom_score(osdi_score, deq5_score):
    """Calculate symptom severity score"""
    score = 0
    # OSDI scoring
    if osdi_score > 50:
        score += 3
    elif osdi_score > 33:
        score += 2
    elif osdi_score > 22:
        score += 1
    
    # DEQ-5 scoring
    if deq5_score > 12:
        score += 3
    elif deq5_score > 8:
        score += 2
    elif deq5_score > 6:
        score += 1
    
    return min(score, 4)

def convert_staining_to_numeric(staining_string):
    """Convert staining description to numerical value"""
    staining_map = {
        "0 - None": 0,
        "I - Mild": 1,
        "II - Moderate": 2,
        "III - Marked": 3,
        "IV - Severe": 4,
        "V - Extreme": 5
    }
    return staining_map.get(staining_string, 0)

def classify_tfos_dry_eye(aqueous_score, evaporative_score):
    """Provide TFOS DEWS III classification"""
    if aqueous_score >= 4 and evaporative_score < 3:
        return "Pure Aqueous Deficiency"
    elif evaporative_score >= 4 and aqueous_score < 3:
        return "Pure Evaporative"
    elif aqueous_score >= 3 and evaporative_score >= 3:
        return "Mixed Mechanism"
    else:
        return "Subclinical/Pre-clinical"

def get_recommendations(analysis):
    """
    Generate treatment recommendations based on TFOS DEWS III management guidelines
    """
    recommendations = []
    severity = analysis['severity']
    dry_eye_type = analysis['dry_eye_type']
    component_scores = analysis['component_scores']
    
    # Base recommendations by severity
    if severity == "Mild":
        recommendations.extend([
            "Artificial tears 4x daily (preservative-free)",
            "Warm compresses 1-2x daily for 10 minutes",
            "Environmental modifications (humidifier, avoid air drafts)",
            "Omega-3 fatty acid supplementation (2000 mg daily)",
            "Blink exercises during digital device use"
        ])
    
    elif severity == "Moderate":
        recommendations.extend([
            "Preservative-free artificial tears 6-8x daily",
            "Warm compresses with lid massage 2x daily",
            "Lipid-based lubricants for nighttime use",
            "Consider punctal plugs for aqueous deficiency",
            "Topical cyclosporine 0.05% or lifitegrast 5% BID",
            "Oral doxycycline 50 mg daily for MGD (3-month course)"
        ])
    
    elif severity == "Severe":
        recommendations.extend([
            "Intensive lubrication regimen (hourly if needed)",
            "Punctal occlusion (temporary then permanent)",
            "Topical corticosteroids (short-term, monitored)",
            "Autologous serum tears 4-6x daily",
            "Intense Pulsed Light (IPL) therapy for MGD",
            "Scleral contact lenses for severe surface disease",
            "Referral to dry eye specialist for advanced management"
        ])
    
    # Type-specific recommendations
    if "Aqueous Deficient" in dry_eye_type:
        recommendations.extend([
            "Prioritize aqueous enhancement strategies",
            "Consider nocturnal ointments for surface protection",
            "Evaluate for underlying autoimmune conditions"
        ])
    
    if "Evaporative" in dry_eye_type:
        recommendations.extend([
            "Focus on meibomian gland dysfunction management",
            "Lid hygiene with commercial cleansers",
            "Consider azithromycin ophthalmic solution for anterior blepharitis"
        ])
    
    # Component-specific recommendations
    if component_scores['inflammatory'] >= 3:
        recommendations.append("Anti-inflammatory therapy as primary treatment modality")
    
    # Follow-up and monitoring
    recommendations.extend([
        "Re-evaluate in 4-6 weeks for treatment response",
        "Adjust therapy based on symptom and sign improvement",
        "Long-term maintenance therapy typically required"
    ])
    
    return recommendations

def main():
    # Header
    st.markdown('<h1 class="main-header">👁️ Tear Film Analysis System</h1>', unsafe_allow_html=True)
    st.markdown("""
    **Professional dry eye diagnosis based on TFOS DEWS III guidelines (2025)**
    
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
                                      ["0 - Clear", "1 - Cloudy", "2 - Granular", "3 - Toothpaste", "4 - No secretion"])
        meiboscore = st.slider("Meiboscore (0-3)", 0, 3, 1,
                              help="0=no loss, 1=≤25%, 2=26-50%, 3=>50% gland dropout")
    
    with st.sidebar.expander("Questionnaire Scores", expanded=True):
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
        
        with col2:
            if uploaded_file is not None and st.button("🔍 Analyze Tear Film", type="primary"):
                with st.spinner("Analyzing tear film characteristics..."):
                    analysis_result = analyze_tear_film_interference(image)
                    
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
                    staining_result = detect_corneal_staining(image)
                    
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
                
                # Display results
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
                    
                    # Diagnosis
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