import streamlit as st
import pandas as pd

# --- Webpage Configuration ---
st.set_page_config(page_title="Enterprise Product Catalog", layout="wide")

# UI Global Styling: ပစ္စည်းအမည်နှင့် စျေးနှုန်း အနီးကပ်ဆုံး ဖြစ်သွားစေရန် Padding နှင့် Margin များ ညှိခြင်း
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
        justify-content: flex-start; /* ⚡ အပေါ်ကပ်စနစ် သုံးထားပါသည် */
        min-height: 180px; /* ⚡ ဓာတ်ပုံပါဝင်သော ကတ်ပြားအမြင့်ကို ပိုမိုကျစ်လျစ်အောင် ညှိထားပါသည် */
    }
    .product-info-box {
        display: flex;
        flex-direction: column;
        gap: 0px; /* ⚡ စာသားနှစ်ခုကြား ကွက်လပ်ကို သုညအထိ ချုံ့ထားပါသည် */
        margin-top: 4px;
        text-align: center;
    }
    .product-title {
        font-weight: 600; 
        font-size: 13px; 
        color: #1e293b; 
        line-height: 1.2; 
        margin-bottom: 2px !important; /* ⚡ အောက်ခြေကွက်လပ်ကို ဖယ်ရှားထားပါသည် */
        display: -webkit-box; 
        -webkit-line-clamp: 2; 
        -webkit-box-orient: vertical; 
        overflow: hidden; 
        min-height: 0px;
    }
    .product-price { 
        font-size: 18px; 
        font-weight: 800; 
        color: #002d72; 
        line-height: 1; /* ⚡ စျေးနှုန်းစာသား အမြင့်ကို အကျစ်လျစ်ဆုံး လုပ်ထားပါသည် */
        margin-top: 0px !important;
    }
    .product-unit { font-size: 11px; font-weight: 400; color: #64748b; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
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
                
            p_image = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ""
            p_category = str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else "Uncategorized"
            if p_category.lower() == "nan" or p_category == "":
                p_category = "Uncategorized"
                
            if p_myanmar and p_myanmar.lower() != "nan" and p_myanmar != "":
                display_title = p_myanmar
            elif p_name and p_name.lower() != "nan" and p_name != "":
                display_title = p_name
            else:
                display_title = f"Product #{p_id}" if p_id else f"Unnamed Item ({p_category})"
            
            if p_id != "" and p_id.lower() != "nan":
                parsed_products.append({
                    "id": p_id,
                    "name": display_title,
                    "price": p_price,
                    "image": p_image,
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
                            
                            # Base64 Local Decoder
                            if prod['image'] and prod['image'].lower() != "nan" and prod['image'] != "":
                                st.markdown(f"""
                                    <div style="text-align:center; height:100px; display:flex; align-items:center; justify-content:center; margin-bottom:2px;">
                                        <img src="data:image/png;base64,{prod['image']}" 
                                             style="max-height:100px; max-width:100%; object-fit:contain; border-radius:6px;">
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                    <div style="text-align:center; height:100px; display:flex; align-items:center; justify-content:center; margin-bottom:2px;">
                                        <img src="https://placehold.co/100x100/f1f5f9/94a3b8?text=📦+Product" 
                                             style="max-height:100px; max-width:100%; object-fit:contain; border-radius:6px;">
                                    </div>
                                """, unsafe_allow_html=True)

                            try:
                                price_str = f"{int(prod['price']):,}"
                            except:
                                price_str = str(prod['price'])

                            # ⚡ ကပ်လျက်ဖြစ်သွားစေရန် ထိန်းချုပ်ထားသော CSS တည်ဆောက်ပုံ
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
