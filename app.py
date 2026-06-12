import streamlit as st
import pandas as pd

# --- Webpage Configuration ---
st.set_page_config(page_title="Enterprise Product Catalog", layout="wide")

# UI Global Styling
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; } 
    .section-banner {
        background-color: #ffd700; padding: 12px; border-radius: 6px; 
        border-left: 8px solid #002d72; margin: 25px 0; color: black; font-weight: bold;
    }
    div[data-testid="stContainer"] {
        background-color: white; border: 1px solid #e2e8f0 !important;
        border-radius: 8px; padding: 8px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        display: flex; flex-direction: column; justify-content: flex-start; min-height: 180px;
    }
    .product-info-box { display: flex; flex-direction: column; gap: 0px; margin-top: 4px; text-align: center; }
    .product-title {
        font-weight: 600; font-size: 13px; color: #1e293b; line-height: 1.2; margin-bottom: 2px !important;
        display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 0px;
    }
    .product-price { font-size: 18px; font-weight: 800; color: #002d72; line-height: 1; margin-top: 2px !important; }
    .product-unit { font-size: 11px; font-weight: 400; color: #64748b; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_catalog_data():
    SPREADSHEET_ID = "1wOuXbwcU9q3Jxgl4s1y2_RImhoY1dy-GdNyAPsHRUnk"
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
    try:
        return pd.read_csv(url)
    except:
        return None

df = load_catalog_data()

# ⚡ Selected Products List
ALLOWED_PRODUCTS = [
    "Sunday 3in1 Coffee Mix", "Sunday 3in1 Tea Mix", "Sunday Nhat Phyaw Coffee",
    "Raw Tamarind", "Red Butter Bean", "Red Dragon Cigarettes (L)",
    "Red Dragon Cigerattes Small", "Red Valiant Cigarette", "Rice Soap"
]

if df is not None:
    parsed_products = []
    
    for index, row in df.iterrows():
        try:
            p_id = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            p_name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            p_myanmar = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
            
            try:
                p_price = float(row.iloc[3])
            except:
                p_price = 0.0
                
            p_image = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ""
            p_category = str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else "Uncategorized"
            if p_category.lower() == "nan" or p_category == "":
                p_category = "Uncategorized"
                
            # ⚡ SHORT-HAND TITLES: စာကြောင်းပြ
