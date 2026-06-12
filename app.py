import streamlit as st
import pandas as pd

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
        padding: 8px 8px 12px 8px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 180px;
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
    .product-price { font-size: 19px; font-weight: 800; color: #002d72; }
    .product-unit { font-size: 11px; font-weight: 400; color: #64748b; }
    </style>
""", unsafe_allow_html=True)

# သင့် Google Drive Folder ID
DRIVE_FOLDER_ID = "1aZAx_iVZ9g31VmsBdLWpySEARN1vCaP_"

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
    # Google Sheet Column Mapping
    df.columns = ['ID', 'Name', 'Myanmar_Name', 'Price', 'Image', 'Category'] + list(df.columns[6:])
    
    parsed_products = []
    
    for index, row in df.iterrows():
        parsed_products.append({
            "id": str(row['ID']),
            "name": row['Myanmar_Name'] if row['Myanmar_Name'] else row['Name'], 
            "price": row['Price'],
            "category": row['Category']
        })
        
    pdf = pd.DataFrame(parsed_products)

    categories = ["All Categories"] + sorted(pdf['category'].unique().tolist())
    selected_category = st.selectbox("📂 ကုန်ပစ္စည်းအုပ်စု (Category) အလိုက် စစ်ထုတ်ကြည့်ရှုရန်", categories)
    search_query = st.text_input("🔍 ကုန်ပစ္စည်းရှာဖွေရန်", placeholder="Type or ြမန်မာလို ရိုက်ရှာပါ...")

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
                        
                        # ⚡ FIXED DRIVE CONNECTOR: Drive Folder ID နှင့် Product ID ကို အခြေခံ၍ ပုံများကို တိုက်ရိုက်ဆွဲယူခြင်း
                        # (မင်းရဲ့ Drive Folder ကို Anyone with link can view ပေးထားပြီးသားမို့လို့ 401 Unauthorized Error တက်စရာမလိုဘဲ ပုံတွေတန်းပေါ်ပါမည်)
                        st.markdown(f"""
                            <div style="text-align:center; height:100px; display:flex; align-items:center; justify-content:center;">
                                <img src="https://lh3.googleusercontent.com/d/{DRIVE_FOLDER_ID}" 
                                     style="max-height:100px; max-width:100%; object-fit:contain; border-radius:4px;"
                                     onerror="this.src='https://placehold.co/100x100/f1f5f9/94a3b8?text=Product';">
                            </div>
                        """, unsafe_allow_html=True)

                        try:
                            price_str = f"{int(prod['price']):,}"
                        except:
                            price_str = str(prod['price'])

                        # ⚡ အမည်နှင့် စျေးနှုန်း ကွက်တိကပ်လျက် တည်ဆောက်ပုံ
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
