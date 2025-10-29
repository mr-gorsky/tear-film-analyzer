import streamlit as st

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