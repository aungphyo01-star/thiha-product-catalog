import streamlit as st
import pandas as pd
import re
from deep_translator import GoogleTranslator

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
        background-color: white;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px;
        padding: 8px 8px 12px 8px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .product-info-box {
        display: flex;
        flex-direction: column;
        gap: 2px;
        margin-top: 4px;
        text-align: center;
    }
    .product-title {
        font-weight: 600; font-size: 13px; color: #1e293b; line-height: 1.3; 
        display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; 
        overflow: hidden; min-height: 34px;
    }
    .product-price { font-size: 19px; font-weight: 800; color: #002d72; }
    .product-unit { font-size: 11px; font-weight: 400; color: #64748b; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_catalog_data():
    SPREADSHEET_ID = "1wOuXbwcU9q3Jxgl4s1y2_RImhoY1dy-GdNyAPsHRUnk"
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
    try:
        df = pd.read_csv(url)
        return df
    except:
        return None

df = load_catalog_data()

if df is not None:
    # ကော်လံအမည်များကို Sheet တည်ဆောက်ပုံအတိုင်း သတ်မှတ်ခြင်း
    df.columns = ['ID', 'Name', 'Myanmar_Name', 'Category_Column', 'Image'] + list(df.columns[5:])
    
    parsed_products = []
    
    for index, row in df.iterrows():
        p_id = str(row['ID']).strip()
        p_name = str(row['Name']).strip()
        raw_price_text = str(row['Myanmar_Name']).strip() # ⚡ ဈေးနှုန်းစာသားသည် လက်ရှိတွင် Myanmar_Name ကော်လံထဲ၌ ရှိနေပါသည်
        raw_category = str(row['Category_Column']).strip()
        
        # ⚡ FIXED PRICE EXTRACTION LOGIC: Myanmar_Name ကော်လံထဲမှ ဂဏန်းများကို ဈေးနှုန်းအဖြစ် ပြောင်းလဲခြင်း
        price_found = 0.0
        if pd.notna(row['Myanmar_Name']) and raw_price_text != "":
            # စာသားထဲမှ ဂဏန်းနှင့် ကော်မာများကိုသာ ဇကာတင်စစ်ထုတ်ယူခြင်း (ဥပမာ - "9,875 ks" -> "9875")
            digits_only = re.sub(r'[^\d]', '', raw_price_text)
            if digits_only:
                try:
                    price_found = float(digits_only)
                except:
                    pass
                    
        # Category Path အား အနောက်ဆုံးပိတ် စာလုံးသန့်သန့်သာ ယူခြင်း
        clean_category = "Uncategorized"
        if raw_category and "/" in raw_category:
            clean_category = [item.strip() for item in raw_category.split("/")][-1]
        elif raw_category:
            clean_category = raw_category
            
        parsed_products.append({
            "id": p_id,
            "name": p_name,
            "price": price_found,
            "category": clean_category
        })
        
    pdf = pd.DataFrame(parsed_products)

    # Filter & Search UI
    categories = ["All Categories"] + sorted(pdf['category'].unique().tolist())
    selected_category = st.selectbox("📂 ကုန်ပစ္စည်းအုပ်စု (Category) အလိုက် စစ်ထုတ်ကြည့်ရှုရန်", categories)
    search_query = st.text_input("🔍 ကုန်ပစ္စည်းရှာဖွေရန်", placeholder="Type to search...")

    if selected_category != "All Categories":
        pdf = pdf[pdf['category'] == selected_category]

    if search_query:
        query = search_query.lower()
        pdf = pdf[pdf['name'].str.lower().str.contains(query, na=False)]

    total_items = len(pdf)
    
    if total_items > 0:
        st.markdown(f'<div class="section-banner"><h2>📦 Product Catalog - {selected_category} ({total_items} ခု)</h2></div>', unsafe_allow_html=True)
        
        cols_per_row = 7
        for i in range(0, len(pdf), cols_per_row):
            row_items = pdf.iloc[i : i + cols_per_row]
            cols = st.columns(cols_per_row)

            for idx, (_, prod) in enumerate(row_items.iterrows()):
                with cols[idx]:
                    with st.container():
                        # Playground Card Box
                        st.markdown(f"""
                            <div style="text-align:center; height:100px; display:flex; align-items:center; justify-content:center; background-color:#f1f5f9; border-radius:6px;">
                                <span style="color:#94a3b8; font-size:12px; font-weight:500;">📦 Product</span>
                            </div>
                        """, unsafe_allow_html=True)

                        try:
                            price_str = f"{float(prod['price']):,.0f}"
                        except:
                            price_str = str(prod['price'])

                        # ကွက်တိ ညှိပြီးသား Layout
                        st.markdown(f"""
                            <div class="product-info-box">
                                <div class="product-title">{prod['name']}</div>
                                <div class="product-price">{price_str} <span class="product-unit">ks</span></div>
                            </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("ကုန်ပစ္စည်း မတွေ့ပါ။")
else:
    st.warning("Google Sheet ထံမှ ဒေတာ ဖတ်မရဖြစ်နေပါသည်။")
