import streamlit as st
import pandas as pd
import re
from deep_translator import GoogleTranslator

# --- Webpage Configuration ---
st.set_page_config(page_title="Enterprise Product Catalog", layout="wide")

# ⚡ UI Global Styling: Card အတွင်းပိုင်း အကွာအဝေးများကို ကျစ်လျစ်သပ်ရပ်အောင် ပြင်ဆင်ခြင်း
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
        gap: 2px; /* ⚡ စာသားနှင့် ဈေးနှုန်းကြား အကွာအဝေးကို ကွက်တိ ကပ်သွားစေရန် ညှိခြင်း */
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
    # Column Header များအား သတ်မှတ်ခြင်း
    df.columns = ['ID', 'Name', 'Myanmar_Name', 'Price_Column', 'Image'] + list(df.columns[5:])
    
    parsed_products = []
    
    # ⚡ DATA EXTRACTOR LOGIC: Name ထဲမှ ဈေးနှုန်းကို ဖြတ်ထုတ်ပြီး Price Column မှ Category ကို သန့်စင်ခြင်း
    for index, row in df.iterrows():
        raw_name = str(row['Name']).strip()
        raw_category = str(row['Price_Column']).strip() # လက်ရှိ Sheet ထဲတွင် Price နေရာ၌ Category ရောက်နေသည်
        myanmar_name = str(row['Myanmar_Name']).strip() if pd.notna(row['Myanmar_Name']) else ""
        
        # ၁။ Name စာသားထဲမှ ဈေးနှုန်းဂဏန်းကို ရှာဖွေဖြတ်ထုတ်ခြင်း (ဥပမာ - "9,875 ks" သို့မဟုတ် "834")
        price_found = 0.0
        clean_name = raw_name
        
        price_match = re.search(r'([\d,]+)\s*(?:ks|Ks|KS)?$', raw_name)
        if price_match:
            try:
                price_str = price_match.group(1).replace(',', '')
                price_found = float(price_str)
                # နာမည်ထဲမှ ဈေးနှုန်းစာသားကို ဖယ်ထုတ်၍ သန့်စင်ခြင်း
                clean_name = raw_name[:price_match.start()].strip()
            except:
                pass
                
        # ၂။ Category Path ကြီးအား အနောက်ဆုံးပိတ်စာလုံးသာ ဖြစ်အောင် သန့်စင်ခြင်း (All / Saleable / Stationery -> Stationery)
        clean_category = "Uncategorized"
        if raw_category and "/" in raw_category:
            clean_category = [item.strip() for item in raw_category.split("/")][-1]
        elif raw_category:
            clean_category = raw_category
            
        display_title = myanmar_name if myanmar_name else clean_name
        
        parsed_products.append({
            "id": str(row['ID']),
            "name": display_title,
            "price": price_found,
            "category": clean_category
        })
        
    # DataFrame အသစ်အဖြစ် ပြန်လည်တည်ဆောက်ခြင်း
    pdf = pd.DataFrame(parsed_products)

    # 📂 Category Filter
    categories = ["All Categories"] + sorted(pdf['category'].unique().tolist())
    selected_category = st.selectbox("📂 ကုန်ပစ္စည်းအုပ်စု (Category) အလိုက် စစ်ထုတ်ကြည့်ရှုရန်", categories)
    
    # 🔍 Search Box
    search_query = st.text_input("🔍 ကုန်ပစ္စည်းရှာဖွေရန်", placeholder="Type or ြမန်မာလို ရိုက်ရှာပါ...")

    if selected_category != "All Categories":
        pdf = pdf[pdf['category'] == selected_category]

    if search_query:
        is_myanmar = any('\u1000' <= char <= '\u109f' for char in search_query)
        if is_myanmar:
            try:
                translated_query = GoogleTranslator(source='my', target='en').translate(search_query)
                query = translated_query.lower()
            except:
                query = search_query.lower()
        else:
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
                        # 🖼️ Placeholder Image Box
                        st.markdown(f"""
                            <div style="text-align:center; height:100px; display:flex; align-items:center; justify-content:center; background-color:#f1f5f9; border-radius:6px;">
                                <span style="color:#94a3b8; font-size:12px; font-weight:500;">📦 Product</span>
                            </div>
                        """, unsafe_allow_html=True)

                        try:
                            price_str = f"{float(prod['price']):,.0f}"
                        except:
                            price_str = str(prod['price'])

                        # ⚡ အမည်နှင့် ဈေးနှုန်းကို ပူးကပ်စွာ ထုတ်ပြခြင်း
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
