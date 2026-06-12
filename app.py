import streamlit as st
import pandas as pd
import math

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
            p_mm = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
            
            try:
                p_price = float(row.iloc[3])
            except:
                p_price = 0.0
                
            p_img = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ""
            p_cat = str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else "Uncategorized"
            
            title = p_mm if (p_mm and p_mm.lower() != "nan") else (p_name if (p_name and p_name.lower() != "nan") else f"Item #{p_id}")
            
            if p_id and p_id.lower() != "nan":
                parsed_products.append({
                    "id": p_id, "name": title, "raw_name": p_name,
                    "raw_mm": p_mm, "price": p_price, "image": p_img, "category": p_cat
                })
        except:
            pass
        
    if len(parsed_products) > 0:
        pdf = pd.DataFrame(parsed_products)

        # Dropdown Menu & Search Bar
        cats = ["All Categories", "⭐️ Selected Products"] + sorted(pdf['category'].unique().tolist())
        f_col1, f_col2 = st.columns([2, 2])
        with f_col1:
            selected_cat = st.selectbox("📂 ကုန်ပစ္စည်းအုပ်စု (Category) အလိုက် စစ်ထုတ်ရန်", cats)
        with f_col2:
            search_q = st.text_input("🔍 ကုန်ပစ္စည်းရှာဖွေရန်", placeholder="Type to search...")

        # Filter Logic
        if selected_cat == "⭐️ Selected Products":
            pdf = pdf[pdf['raw_name'].isin(ALLOWED_PRODUCTS) | pdf['raw_mm'].isin(ALLOWED_PRODUCTS) | pdf['name'].isin(ALLOWED_PRODUCTS)]
        elif selected_cat != "All Categories":
            pdf = pdf[pdf['category'] == selected_cat]

        if search_q:
            pdf = pdf[pdf['name'].str.lower().str.contains(search_q.lower(), na=False)]

        total_items = len(pdf)
        
        if total_items > 0:
            st.markdown(f'<div class="section-banner"><h2>📦 Product Catalog - {selected_cat} ({total_items} ခု)</h2></div>', unsafe_allow_html=True)
            
            # ⚡ PAGINATION CONFIG
            ITEMS_PER_PAGE = 35
            total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
            
            if "current_page" not in st.session_state:
                st.session_state.current_page = 1
                
            if "prev_cat" not in st.session_state or st.session_state.prev_cat != selected_cat or "prev_q" not in st.session_state or st.session_state.prev_q != search_q:
                st.session_state.current_page = 1
                st.session_state.prev_
