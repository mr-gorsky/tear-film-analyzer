import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

def analyze_interferometric_colors(image):
    """Analizira interferentne boje sa slike"""
    # Konvertiraj PIL Image u numpy array
    img_array = np.array(image)
    
    # Konvertiraj u HSV za analizu boja
    hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
    
    # Analiziraj dominantne boje
    hue_mean = np.mean(hsv[:,:,0])
    saturation_mean = np.mean(hsv[:,:,1])
    value_mean = np.mean(hsv[:,:,2])
    
    # Generiraj interpretaciju na temelju analize
    if saturation_mean < 50:
        interpretation = "Niska interferencija - moguća suša oka"
    elif hue_mean < 30:
        interpretation = "Žuto-narančaste interferentne boje - umjerena suhoća"
    else:
        interpretation = "Raznolike interferentne boje - dobro stanje suznog filma"
    
    return interpretation, hue_mean, saturation_mean, value_mean

def analyze_fluo_test(image):
    """Analizira fluoresceinski test"""
    img_array = np.array(image)
    
    # Konvertiraj u grayscale za analizu intenziteta
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Analiziraj svjetlinu i distribuciju
    brightness_mean = np.mean(gray)
    brightness_std = np.std(gray)
    
    if brightness_mean < 100:
        interpretation = "Slab fluoresceinski odgovor - moguća suša oka"
    elif brightness_std > 50:
        interpretation = "Neujednačena distribucija - suhoća oka"
    else:
        interpretation = "Ujednačena distribucija - normalan fluo test"
    
    return interpretation, brightness_mean, brightness_std

def get_recommendations(interpretation_interf, interpretation_fluo):
    """Generira preporuke na temelju obje analize"""
    recommendations = []
    
    if "suša" in interpretation_interf.lower() or "suhoća" in interpretation_interf.lower():
        recommendations.append("Redovita primjena vještačkih suza")
        recommendations.append("Izbjegavajte dugotrajno gledanje u ekrane")
        recommendations.append("Koristite vlažnost zraka u prostoriji")
    
    if "suša" in interpretation_fluo.lower() or "suhoća" in interpretation_fluo.lower():
        recommendations.append("Kontrola okoline (vlažnost zraka)")
        recommendations.append("Povećanje unosa tekućine")
        recommendations.append("Zaštitne naočale kod vjetra i sunca")
    
    # Ukloni duplikate
    recommendations = list(set(recommendations))
    
    if not recommendations:
        recommendations = [
            "Stanje suznog filma je zadovoljavajuće", 
            "Redoviti pregledi preporučuju se jednom godišnje",
            "Nastavite s dobrim navikama zaštite očiju"
        ]
    
    return recommendations

# Glavni dio aplikacije
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

# Sidebar za informacije
with st.sidebar:
    st.header("ℹ️ O aplikaciji")
    st.info("""
    Ova aplikacija analizira slike suznog filma kroz:
    - **Interferentne boje** - kvaliteta suznog filma
    - **Fluoresceinski test** - integritet očne površine
    """)
    
    st.header("📝 Upute")
    st.write("""
    1. Uploadajte sliku interferentnih boja
    2. Uploadajte sliku fluo testa  
    3. Pregledajte rezultate analize
    4. Slijedite preporuke
    """)

# Upload sekcija
st.header("📤 Upload Slika")

col1, col2 = st.columns(2)

with col1:
    uploaded_file_interf = st.file_uploader(
        "**Interferentne boje**", 
        type=['jpg', 'jpeg', 'png'],
        key="interf",
        help="Uploadajte sliku interferentnih boja suznog filma"
    )

with col2:
    uploaded_file_fluo = st.file_uploader(
        "**Fluo test**", 
        type=['jpg', 'jpeg', 'png'], 
        key="fluo",
        help="Uploadajte sliku fluoresceinskog testa"
    )

# Analiza interferentnih boja
if uploaded_file_interf is not None:
    st.header("🔍 Analiza interferentnih boja")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        image_interf = Image.open(uploaded_file_interf)
        st.image(image_interf, caption="Uploadana slika - Interferentne boje", use_column_width=True)
    
    with col2:
        with st.spinner('Analiziram interferentne boje...'):
            interpretation_interf, hue, saturation, value = analyze_interferometric_colors(image_interf)
            
            st.subheader("📊 Rezultati analize:")
            st.success(f"**Interpretacija:** {interpretation_interf}")
            
            # Prikaži metrike
            with st.expander("Detaljne metrike"):
                st.write(f"**Srednja vrijednost nijanse (Hue):** {hue:.2f}")
                st.write(f"**Srednja zasićenost (Saturation):** {saturation:.2f}")
                st.write(f"**Srednja svjetlina (Value):** {value:.2f}")

# Analiza fluo testa
if uploaded_file_fluo is not None:
    st.header("💡 Analiza fluo testa")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        image_fluo = Image.open(uploaded_file_fluo)
        st.image(image_fluo, caption="Uploadana slika - Fluo test", use_column_width=True)
    
    with col2:
        with st.spinner('Analiziram fluo test...'):
            interpretation_fluo, brightness, brightness_std = analyze_fluo_test(image_fluo)
            
            st.subheader("📊 Rezultati analize:")
            st.success(f"**Interpretacija:** {interpretation_fluo}")
            
            # Prikaži metrike
            with st.expander("Detaljne metrike"):
                st.write(f"**Srednja svjetlina:** {brightness:.2f}")
                st.write(f"**Standardna devijacija:** {brightness_std:.2f}")

# Preporuke nakon dijagnoze
if uploaded_file_interf is not None and uploaded_file_fluo is not None:
    st.header("💡 Preporuke nakon dijagnoze")
    
    recommendations = get_recommendations(interpretation_interf, interpretation_fluo)
    
    st.info("Na temelju analize obje slike, preporučujemo sljedeće:")
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")
    
    # Dodatne informacije
    with st.expander("ℹ️ Dodatne informacije"):
        st.write("""
        **Napomena:** Ove preporuke su generirane na temelju analize slika i trebaju se 
        shvatiti kao smjernice. Za potpunu dijagnozu i liječenje uvijek se konzultirajte 
        s oftalmologom.
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Tear Film Analyzer © 2024 | Za edukativne svrhe"
    "</div>", 
    unsafe_allow_html=True
)