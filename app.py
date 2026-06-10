import streamlit as st
import pandas as pd
import xmlrpc.client
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="Enterprise Product Catalog", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; } 
    .section-banner {
        background-color: #ffd700; padding: 12px; border-radius: 6px; 
        border-left: 8px solid #002d72; margin: 25px 0; color: black; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

URL = "https://odoo-stg.linklusion.co.jp"
DB = "odoo15"
USERNAME = "aungphyo01@gmail.com"
PASSWORD = "9aa38107a400d3666e7e36a3f578e18d20388a06"

@st.cache_data(ttl=300)
def load_catalog_data():
    SPREADSHEET_ID = "1wOuXbwcU9q3Jxgl4s1y2_RImhoY1dy-GdNyAPsHRUnk"
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
    try:
        df = pd.read_csv(url)
        return df
    except:
        return None

# ⚡ ဈေးနှုန်းနှင့် ဓာတ်ပုံများကို Background မှ တစ်ပြိုင်နက် လှမ်းဆွဲမည့် စနစ်
@st.cache_data(ttl=300)
def fetch_odoo_details(product_ids):
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        details = models.execute_kw(
            DB, uid, PASSWORD, "product.template", "read",
            [product_ids], {"fields": ["id", "list_price", "image_128"]}
        )
        return {str(item["id"]): {"price": item.get("list_price", 0), "image": item.get("image_128", "")} for item in details}
    except:
        return {}

df = load_catalog_data()

if df is not None:
    search_query = st.text_input("🔍 ကုန်ပစ္စည်းအမည်ဖြင့် ရှာဖွေရန် (မြန်မာ/English)", placeholder="Type to search...")

    if search_query:
        query = search_query.lower()
        if 'Myanmar_Name' in df.columns:
            df = df[df['Name'].str.lower().str.contains(query, na=False) | df['Myanmar_Name'].str.lower().str.contains(query, na=False)]
        else:
            df = df[df['Name'].str.lower().str.contains(query, na=False)]

    visible_ids = df['ID'].dropna().astype(int).tolist() if 'ID' in df.columns else []
    odoo_details = fetch_odoo_details(visible_ids) if visible_ids else {}

    product_list = []
    for index, row in df.iterrows():
        p_id = str(row.get('ID', ''))
        p_name_en = row.get('Name', '')
        p_name_mm = str(row.get('Myanmar_Name', '')) if pd.notna(row.get('Myanmar_Name')) else ""
        
        # Odoo ထံမှ Live Details ယူခြင်း
        p_details = odoo_details.get(p_id, {"price": 0, "image": ""})
        
        product_list.append({
            "name_en": p_name_en,
            "name_mm": p_name_mm,
            "price": p_details["price"],
            "image": p_details["image"]
        })

    def display_grid(p_set, title, icon):
        st.markdown(f'<div class="section-banner"><h2>{icon} {title}</h2></div>', unsafe_allow_html=True)
        if not p_set:
            st.info("ပြသရန် ကုန်ပစ္စည်း မရှိသေးပါ။")
            return

        cols_per_row = 7
        for i in range(0, len(p_set), cols_per_row):
            row_items = p_set[i : i + cols_per_row]
            cols = st.columns(cols_per_row)

            for idx, prod in enumerate(row_items):
                with cols[idx]:
                    with st.container(border=True):
                        if prod['image']:
                            st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{prod["image"]}" style="height:110px; object-fit:contain; margin-bottom:8px;"></div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="height:110px; background:#f1f5f9; display:flex; align-items:center; justify-content:center; border-radius:6px; margin-bottom:8px; color:#94a3b8; font-size:11px;">No Image</div>', unsafe_allow_html=True)

                        display_name = prod['name_mm'] if prod['name_mm'] else prod['name_en']
                        st.markdown(f'<div style="font-weight:600; font-size:14px; color:#1e293b; min-height:42px; line-height:1.3; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; text-align:center;">{display_name}</div>', unsafe_allow_html=True)

                        try:
                            price_str = f"{float(prod['price']):,.0f}"
                        except:
                            price_str = str(prod['price'])

                        st.markdown(f'<div style="font-size:22px; font-weight:800; color:#002d72; text-align:center; margin-top:5px;">{price_str} <span style="font-size:12px; font-weight:400; color:#475569;">ks</span></div>', unsafe_allow_html=True)

    display_grid(product_list, "Product Catalog", "📦")
else:
    st.warning("Google Sheet ထံမှ ဒေတာ ဖတ်မရဖြစ်နေပါသည်။")
