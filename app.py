import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator

# --- Webpage Configuration ---
st.set_page_config(page_title="Enterprise Product Catalog", layout="wide")

# UI Global Styling: ကတ်များ ကျစ်လျစ်သပ်ရပ်ပြီး ပစ္စည်းအမည်နှင့် စျေးနှုန်း ကပ်နေစေရန် ညှိခြင်း
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
        padding: 10px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 180px;
    }
    .product-image-box {
        text-align: center; 
        height: 60px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        background-color: #f1f5f9; 
        border-radius: 6px;
        color: #94a3b8;
        font-size: 20px;
    }
    .product-info-box {
        display: flex;
        flex-direction: column;
        gap: 2px;
        margin-top: 6px;
        text-align: center;
    }
    .product-title {
        font-weight: 600; font-size: 13px; color: #1e293b; line-height: 1.3; 
        display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; 
        overflow: hidden; min-height: 34px;
    }
    .product-price { font-size: 18px; font-weight: 800; color: #002d72; }
    .product-unit { font-size: 11px; font-weight: 400; color: #64748b; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_catalog_data():
    SPREADSHEET_ID = "1wOuXbwcU9q3Jxgl4s1y2_RImhoY1dy-GdNyAPsHRUnk"
    # Header Row မပါဘဲ သန့်သန့်ဖတ်ရန်အတွက် header=0 ဟု သတ်မှတ်သည်
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
    try:
        df = pd.read_csv(url)
        return df
    except:
        return None

df = load_catalog_data()

if df is not None:
    # ⚡ FIXED COLUMN MAPPING: မင်းပြပေးလိုက်တဲ့ တကယ့် Google Sheet ကော်လံအတိုင်း ကွက်တိ နာမည်ပေးခြင်း
    # Column A=ID, B=Name, C=Myanmar_Name, D=Price, E=Image, F=Category
    df.columns = ['ID', 'Name', 'Myanmar_Name', 'Price', 'Image', 'Category'] + list(df.columns[6:])
    
    parsed_products = []
    
    for index, row in df.iterrows():
        p_id = str(row['ID']).strip()
        p_name = str(row['Name']).strip()
        p_myanmar = str(row['Myanmar_Name']).strip() if pd.notna(row['Myanmar_Name']) else ""
        
        # စျေးနှုန်းကို ကိန်းပြည့်အဖြစ် ပြောင်းလဲခြင်း
        try:
            p_price = float(row['Price'])
        except:
            p_price = 0.0
            
        p_category = str(row['Category']).strip() if pd.notna(row['Category']) else "Uncategorized"
        
        # အကယ်၍ Myanmar_Name ကော်လံထဲမှာ စာသားရှိနေရင် ၎င်းကိုပြပြီး၊ မရှိရင် ပင်မ Name ကို သုံးမည်
        display_title = p_myanmar if (p_myanmar and p_myanmar.lower() != "nan") else p_name
        
        parsed_products.append({
            "id": p_id,
            "name": display_title,
            "price": p_price,
            "category": p_category
        })
        
    pdf = pd.DataFrame(parsed_products)

    # 📂 Category Filter UI (အုပ်စုအလိုက် ကွက်တိခွဲပြနိုင်ပါပြီ)
    categories = ["All Categories"] + sorted(pdf['category'].unique().tolist())
    selected_category = st.selectbox("📂 ကုန်ပစ္စည်းအုပ်စု (Category) အလိုက် စစ်ထုတ်ကြည့်ရှုရန်", categories)
    
    # 🔍 Search Box
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
            row_items = pdf.iloc
