import streamlit as st
import pandas as pd
import xmlrpc.client
import ssl

# --- SSL Bypass ---
ssl._create_default_https_context = ssl._create_unverified_context

# --- Webpage Configuration ---
st.set_page_config(page_title="Enterprise Product Catalog", layout="wide")

# UI Global Styling (ကတ်တလောက်စာရွက်ဒီဇိုင်းကဲ့သို့ သပ်ရပ်လှပစေရန်)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; } 
    .section-banner {
        background-color: #ffd700; padding: 12px; border-radius: 6px; 
        border-left: 8px solid #002d72; margin: 25px 0; color: black; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Odoo ERP System Credentials (ဓာတ်ပုံများကို Background မှ ဆွဲရန်) ---
URL = "https://odoo-stg.linklusion.co.jp"
DB = "odoo15"
USERNAME = "aungphyo01@gmail.com"
PASSWORD = "9aa38107a400d3666e7e36a3f578e18d20388a06"

# --- Google Sheet မှ Data ဖတ်ယူမည့် Function ---
@st.cache_data(ttl=300)  # ၅ မိနစ်လျှင် တစ်ကြိမ် ဒေတာအသစ် စစ်ပါမည်
def load_catalog_data():
    SPREADSHEET_ID = "1wOuXbwcU9q3Jxgl4s1y2_RImhoY1dy-GdNyAPsHRUnk"
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
    try:
        df = pd.read_csv(url)
        return df
    except:
        return None

# --- ဓာတ်ပုံများကို နောက်ကွယ်မှ သီးသန့် အမြန်ဆွဲပေးမည့် Lazy Loading Cache System ---
@st.cache_data(ttl=600)
def fetch_product_images(product_ids):
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        images = models.execute_kw(
            DB, uid, PASSWORD, "product.template", "read",
            [product_ids], {"fields": ["id", "image_128"]}
        )
        return {str(img['id']): img['image_128'] for img in images if img.get('image_128')}
    except:
        return {}

# --- ပင်မ Logic မောင်းနှင်ခြင်း ---
df = load_catalog_data()

if df is not None:
    # 🔍 စမတ်ကျသော ရှာဖွေမှုစနစ်
    search_query = st.text_input("🔍 ကုန်ပစ္စည်းအမည်ဖြင့် ရှာဖွေရန် (မြန်မာ/English)", placeholder="Type to search...")

    if search_query:
        query = search_query.lower()
        
        # ⚡ Column ရှိမရှိ ကြိုတင်စစ်ဆေးပြီး အမှားကာကွယ်သည့် စနစ်
        if 'Myanmar_Name' in df.columns:
            df = df[
                df['Name'].str.lower().str.contains(query, na=False) | 
                df['Myanmar_Name'].str.lower().str.contains(query, na=False)
            ]
        else:
            df = df[df['Name'].str.lower().str.contains(query, na=False)]

    # ပစ္စည်း ID များကို စုစည်းပြီး ပုံများကို တစ်ပြိုင်နက် လှမ်းဆွဲခြင်း
    visible_ids = df['ID'].dropna().astype(int).tolist() if 'ID' in df.columns else []
    image_dict = fetch_product_images(visible_ids) if visible_ids else {}

    product_list = []
    for index, row in df.iterrows():
        p_id = str(row.get('ID', ''))
        p_name_en = row.get('Name', '')
        p_name_mm = str(row.get('Myanmar_Name', '')) if pd.notna(row.get('Myanmar_Name')) else ""
        p_price = row.get('Price', 0)
        
        # 🛠️ FIXED: ကွင်းအပိတ် (`}`) နှင့် (` ) `) များကို စနစ်တကျ ပြန်လည်ပိတ်ပေးထားပါတယ်ဗျာ
        product_list.append({
            "name_en": p_name_en,
            "name_mm": p_name_mm,
            "price": p_price,
            "image": image_dict.get(p_id, "")
        })

    # --- 🎨 တစ်တန်းလျှင် ၇ ခုစီ ပြသမည့် Grid စနစ် ---
    def display_grid(p_set, title, icon):
        st.markdown(f'<div class="section-banner"><h2>{icon} {title}</h2></div>', unsafe_allow_html=True)
        if not p_set:
            st.info("ပြသရန် ကုန်ပစ္စည်း မရှိသေးပါ။")
            return

        cols_per_row = 7  # တစ်တန်းလျှင် ၇ ခု ကွက်တိစီခြင်း
        for i in range(0, len(p_set), cols_per_row):
            row_items = p_set[i : i + cols_per_row]
            cols = st.columns(cols_per_row)

            for idx, prod in enumerate(row_items):
                with cols[idx]:
                    with st.container(border=True):
                        # ၁။ ဓာတ်ပုံပြသခြင်း
                        if prod['image']:
                            st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{prod["image"]}" style="height:110px; object-fit:contain; margin-bottom:8px;"></div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="height:110px;
