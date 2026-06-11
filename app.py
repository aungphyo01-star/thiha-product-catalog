import streamlit as st
import pandas as pd
import re
from deep_translator import GoogleTranslator

# --- Webpage Configuration ---
st.set_page_config(page_title="Enterprise Product Catalog", layout="wide")

# UI Global Styling: Card အမြင့်နှင့် အကွာအဝေးများကို ကျစ်လျစ်သပ်ရပ်အောင် ကွက်တိညှိခြင်း
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
        padding: 8px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 200px; /* ⚡ Card အမြင့် အားလုံးကို တစ်ပြေးညီ ဖြစ်စေရန် */
    }
    .product-image-placeholder {
        text-align: center; 
        height: 80px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        background-color: #f1f5f9; 
        border-radius: 6px;
        color: #94a3b8;
        font-size: 24px;
    }
    .product-info-box {
        display: flex;
        flex-direction: column;
        gap: 2px; /* ⚡ နာမည်နှင့် စျေးနှုန်းကို ကွက်တိ ပူးကပ်သွားစေရန် Gap ကို အနည်းဆုံးထားခြင်း */
        margin-top: 6px;
        text-align: center;
    }
    .product-title {
        font-weight: 600; 
        font-size: 13px; 
        color: #1e293b; 
        line-height: 1.3; 
        display: -webkit-box; 
        -webkit-line-clamp: 2; 
        -webkit-box-orient: vertical; 
        overflow: hidden; 
        min-height: 34px;
    }
    .product-price { 
        font-size: 18px; 
        font-weight: 800; 
        color: #002d72; 
        margin-top: 2px;
    }
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
    # Google Sheet ၏ ကော်လံဖွဲ့စည်းပုံအတိုင်း အမည်ပေးခြင်း
    df.columns = ['ID', 'Name', 'Myanmar_Name', 'Category_Column', 'Image'] + list(df.columns[5:])
    
    parsed_products = []
    
    for index, row in df.iterrows():
        p_id = str(row['ID']).strip()
        p_name = str(row['Name']).strip()
        raw_price_text = str(row['Myanmar_Name']).strip() # С Column ထဲတွင် စျေးနှုန်းရှိနေပါသည်
        raw_category = str(row['Category_Column']).strip()
        
        # ⚡ BULLETPROOF PRICE LOGIC: ဒဿမအစက် (.00) နှင့် ကော်မာ (,) များကို အမှန်ကန်ဆုံး ဖတ်ထုတ်ခြင်း
        price_found = 0.0
        if pd.notna(row['Myanmar_Name']) and raw_price_text != "" and raw_price_text.lower() != "nan":
            # စာသားထဲမှ ဂဏန်း၊ ကော်မာနှင့် အစက်ကိုသာ ချန်ပြီး ကျန်တာအကုန်ဖျက်သည် (ဥပမာ - "9,875.00 ks" -> "9875.00")
            clean_price_str = re.sub(r'[^\d.]', '', raw_price_text.replace(',', ''))
            if clean_price_str:
                try:
                    price_found = float(clean_price_str)
                except:
                    pass
                    
        # Category Path ရှင်းလင်းခြင်း
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

    # Filter UI
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
                        # 🖼️ ဓာတ်ပုံနေရာတွင် သပ်ရပ်လှပသော Box Layout ကို တိုက်ရိုက်ဆွဲပြခြင်း
                        st.markdown(f"""
                            <div class="product-image-placeholder">
                                📦
                            </div>
                        """, unsafe_allow_html=True)

                        # စျေးနှုန်းအား ကော်မာဖြတ်၍ ပုံစံချခြင်း (.00 ဒဿမကို ဖျောက်၍ သန့်သန့်ပြမည်)
                        try:
                            price_str = f"{int(prod['price']):,}"
                        except:
                            price_str = str(prod['price'])

                        # ⚡ အမည်နှင့် စျေးနှုန်းကို တစ်သားတည်း ပူးကပ်စွာ ထုတ်ပြခြင်း
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
