import streamlit as st
import pandas as pd
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
    
    /* Product Card တစ်ခုချင်းစီ၏ Layout အား စနစ်တကျ ကျစ်လျစ်စေရန် ညှိခြင်း */
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
    
    /* ပစ္စည်းအမည်နှင့် ဈေးနှုန်းကြား အကွာအဝေးကို အလိုအလျောက် ကျစ်လျစ်စေမည့် စနစ် */
    .product-info-box {
        display: flex;
        flex-direction: column;
        gap: 4px; /* ⚡ စာသားနှင့် ဈေးနှုန်းကြား အကွာအဝေးကို ကွက်တိချန်ခြင်း */
        margin-top: 6px;
        text-align: center;
    }
    
    .product-title {
        font-weight: 600; 
        font-size: 13px; 
        color: #1e293b; 
        line-height: 1.3; 
        display: -webkit-box; 
        -webkit-line-clamp: 2; /* ⚡ နာမည်ရှည်လျှင် ၂ ကြောင်းသာပြပြီး ... ဖြတ်မည် */
        -webkit-box-orient: vertical; 
        overflow: hidden; 
        min-height: 34px; /* Card အမြင့် တစ်ပြေးညီဖြစ်စေရန် အနိမ့်ဆုံးအမြင့်ကို အနည်းငယ်လျှော့ချခြင်း */
    }
    
    .product-price {
        font-size: 19px; 
        font-weight: 800; 
        color: #002d72; 
    }
    
    .product-unit {
        font-size: 11px; 
        font-weight: 400; 
        color: #64748b;
    }
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
    df['ID'] = df['ID'].fillna("").astype(str)
    df['Name'] = df['Name'].fillna("").astype(str)
    df['Myanmar_Name'] = df['Myanmar_Name'].fillna("").astype(str)
    df['Price'] = df['Price'].fillna(0).astype(float)
    df['Image'] = df['Image'].fillna("").astype(str)
    df['Category'] = df['Category'].fillna("Uncategorized").astype(str)

    # 📂 Category Filter
    categories = ["All Categories"] + sorted(df['Category'].unique().tolist())
    selected_category = st.selectbox("📂 ကုန်ပစ္စည်းအုပ်စု (Category) အလိုက် စစ်ထုတ်ကြည့်ရှုရန်", categories)

    # 🔍 Search Box
    search_query = st.text_input("🔍 ကုန်ပစ္စည်းရှာဖွေရန် (မြန်မာလိုဖြစ်စေ၊ English လိုဖြစ်စေ ရိုက်ရှာနိုင်ပါသည်)", placeholder="Type or ြမန်မာလို ရိုက်ရှာပါ...")

    if selected_category != "All Categories":
        df = df[df['Category'] == selected_category]

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
        df = df[df['Name'].str.lower().str.contains(query, na=False)]

    total_items = len(df)
    
    if total_items > 0:
        product_list = []
        for index, row in df.iterrows():
            display_name = row['Myanmar_Name'] if row['Myanmar_Name'] else row['Name']
            product_list.append({
                "name": display_name, 
                "price": row['Price'],
                "image": row['Image']
            })

        # --- 🎨 Grid ပြသခြင်းစနစ် (တစ်တန်းလျှင် ၇ ခု) ---
        st.markdown(f'<div class="section-banner"><h2>📦 Product Catalog - {selected_category} ({total_items} ခု)</h2></div>', unsafe_allow_html=True)
        
        cols_per_row = 7
        for i in range(0, len(product_list), cols_per_row):
            row_items = product_list[i : i + cols_per_row]
            cols = st.columns(cols_per_row)

            for idx, prod in enumerate(row_items):
                with cols[idx]:
                    with st.container():
                        # 🖼️ ဓာတ်ပုံပြသခြင်းအပိုင်း
                        if prod['image'] and str(prod['image']).strip() != "":
                            st.markdown(f"""
                                <div style="text-align:center; height:100px; display:flex; align-items:center; justify-content:center;">
                                    <img src="data:image/png;base64,{prod['image']}" 
                                         style="max-height:100px; max-width:100%; object-fit:contain; border-radius:4px;">
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                                <div style="text-align:center; height:100px; display:flex; align-items:center; justify-content:center;">
                                    <img src="https://placehold.co/100x100/f1f5f9/94a3b8?text=No+Image" 
                                         style="max-height:100px; max-width:100%; object-fit:contain; border-radius:4px;">
                                </div>
                            """, unsafe_allow_html=True)

                        # ⚡ FIXED HTML BLOCK: အမည်နှင့် ဈေးနှုန်းကို ပူးကပ်သွားအောင် Div တစ်ခုတည်းဖြင့် စုစည်းလိုက်ခြင်း
                        try:
                            price_str = f"{float(prod['price']):,.0f}"
                        except:
                            price_str = str(prod['price'])

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
