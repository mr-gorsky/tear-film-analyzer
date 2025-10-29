import cv2
import numpy as np
from scipy import ndimage
from skimage import filters, measure, color
import streamlit as st

def analyze_tear_film_interference(image):
    """
    Analyze tear film interference patterns based on TFOS DEWS III guidelines
    """
    try:
        # Convert to RGB if BGR
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
        
        # Enhance contrast using CLAHE
        lab = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2LAB)
        lab[:,:,0] = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8)).apply(lab[:,:,0])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        # Analyze color patterns for interference grading
        hsv = cv2.cvtColor(enhanced, cv2.COLOR_RGB2HSV)
        
        # Define color ranges for interference patterns (simplified)
        color_ranges = {
            'Blue_Interference': ([100, 50, 50], [140, 255, 255]),
            'Green_Interference': ([40, 50, 50], [80, 255, 255]),
            'Yellow_Interference': ([20, 50, 50], [40, 255, 255]),
            'Red_Interference': ([0, 50, 50], [10, 255, 255])
        }
        
        color_count = {}
        total_pixels = hsv.shape[0] * hsv.shape[1]
        
        for color_name, (lower, upper) in color_ranges.items():
            lower = np.array(lower, dtype=np.uint8)
            upper = np.array(upper, dtype=np.uint8)
            mask = cv2.inRange(hsv, lower, upper)
            color_percentage = np.sum(mask > 0) / total_pixels * 100
            if color_percentage > 1:  # Only count significant colors
                color_count[color_name] = color_percentage
        
        # Determine interference grade based on TFOS patterns
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

def detect_corneal_staining(image):
    """
    Detect corneal staining patterns from fluorescein or lissamine green images
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Apply adaptive threshold for staining detection
        binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # Morphological operations to clean up detection
        kernel = np.ones((3,3), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)
        
        # Find contours of staining areas
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size and shape
        min_area = 100
        significant_contours = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area:
                # Additional shape filtering can be added here
                significant_contours.append(cnt)
        
        # Create result image with detected areas
        result_image = image.copy()
        cv2.drawContours(result_image, significant_contours, -1, (255, 0, 0), 2)
        
        # Calculate damage percentage
        total_area = gray.shape[0] * gray.shape[1]
        damage_area = sum(cv2.contourArea(cnt) for cnt in significant_contours)
        damage_percentage = (damage_area / total_area) * 100
        
        # Determine staining grade (Oxford Scale approximation)
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
            'detected_areas': result_image,
            'staining_grade': staining_grade,
            'damage_percentage': damage_percentage,
            'contour_count': len(significant_contours),
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