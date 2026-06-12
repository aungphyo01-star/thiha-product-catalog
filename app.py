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
        background-color: white;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px;
        padding: 10px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 190px;
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

@st.cache_data(ttl=60) # ⚡ ချက်ချင်း Update သိနိုင်ရန် Cache သက်တမ်းကို ၁ မိနစ်သာ ထားရှိပါသည်
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
                
            p_category = str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else "Uncategorized"
            if p_category.lower() == "nan" or p_category == "":
                p_category = "Uncategorized"
                
            # ⚡ CRASH-SAFE: အမည်မပါသော ပစ္စည်းများကို ID ဖြင့် အစားထိုးပြသပြီး ဒေတာပျောက်မသွားစေရန် ထိန်းသိမ်းခြင်း
            if p_myanmar and p_myanmar.lower() != "nan" and p_myanmar != "":
                display_title = p_myanmar
            elif p_name and p_name.lower() != "nan" and p_name != "":
                display_title = p_name
            else:
                display_title = f"Item #{p_id}" if p_id else f"Unknown Item ({p_category})"
            
            if p_id != "":
                parsed_products.append({
                    "id": p_id,
                    "name": display_title,
                    "price": p_price,
                    "category": p_category
                })
        except:
            pass
        
    if len(parsed_products) > 0:
        pdf = pd.DataFrame(parsed_products)

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
                            p_id = prod["id"]
                            
                            # ⚡ THE BULLSEYE PUBLIC LINK: အကောင့်ဝင်စရာမလိုဘဲ ပုံအစစ်များကို ရာနှုန်းပြည့်ဆွဲထုတ်ပေးသော Odoo Public API Link ဖြစ်ပါသည်
                            odoo_public_img = f"https://odoo.linklusion.co.jp/web/image?model=product.product&id={p_id}&field=image_128"
                            
                            st.markdown(f"""
                                <div style="text-align:center; height:100px; display:flex; align-items:center; justify-content:center; margin-bottom:4px;">
                                    <img src="{odoo_public_img}" 
                                         style="max-height:100px; max-width:100%; object-fit:contain; border-radius:6px;"
                                         onerror="this.onerror=null; this.src='https://placehold.co/100x100/f1f5f9/94a3b8?text=📦+Product';">
                                </div>
                            """, unsafe_allow_html=True)

                            try:
                                price_str = f"{int(prod['price']):,}"
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
        st.info("ပြသရန် ဒေတာ မရှိပါ။")
else:
    st.warning("Google Sheet ထံမှ ဒေတာ ဖတ်မရဖြစ်နေပါသည်။")
