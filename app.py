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
        padding: 8px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        min-height: 180px;
    }
    .product-info-box {
        display: flex;
        flex-direction: column;
        gap: 0px;
        margin-top: 4px;
        text-align: center;
    }
    .product-title {
        font-weight: 600; 
        font-size: 13px; 
        color: #1e293b; 
        line-height: 1.2; 
        margin-bottom: 2px !important;
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
        line-height: 1; 
        margin-top: 2px !important;
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

# ⚡ Filter သီးသန့်အဖြစ် သတ်မှတ်ပေးမည့် ပစ္စည်းအမည်များစာရင်း
ALLOWED_PRODUCTS = [
    "Sunday 3in1 Coffee Mix",
    "Sunday 3in1 Tea Mix",
    "Sunday Nhat Phyaw Coffee",
    "Raw Tamarind",
    "Red Butter Bean",
    "Red Dragon Cigarettes (L)",
    "Red Dragon Cigerattes Small",
    "Red Valiant Cigarette",
    "Rice Soap"
]

if df is not None:
    parsed_products = []
    
    # ၁။ Google Sheet ထဲက ၅၉၈ ခုလုံးကို စာရင်းထဲ အရင်အပြည့်အဝ ထည့်သွင်းပါသည်
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
                    "raw_name": p_name,
                    "raw_mm": p_myanmar,
                    "price": p_price,
                    "image": p_image,
                    "category": p_category
                })
        except:
            pass
        
    if len(parsed_products) > 0:
        pdf = pd.DataFrame(parsed_products)

        # ⚡ STRATEGIC FILTER LIST: Dropdown Menu ထဲတွင် "⭐️ Selected Products" ဆိုသော Filter အား ဒုတိယမြောက်နေရာတွင် အထူးတိုးထည့်ခြင်း
        categories = ["All Categories", "⭐️ Selected Products"] + sorted(pdf['category'].unique().tolist())
        selected_category = st.selectbox("📂 ကုန်ပစ္စည်းအုပ်စု (Category) အလိုက် စစ်ထုတ်ကြည့်ရှုရန်", categories)
        search_query = st.text_input("🔍 ကုန်ပစ္စည်းရှာဖွေရန်", placeholder="Type to search...")

        # ⚡ FILTER LOGIC: Dropdown ရွေးချယ်မှုအလိုက် စစ်ထုတ်ခြင်း
        if selected_category == "⭐️ Selected Products":
            # ရွေးချယ်ထားသော ပစ္စည်းအမည်များနှင့် ကိုက်ညီမှုရှိမရှိ စစ်ထုတ်ပေးမည့်စနစ်
            pdf = pdf[
                pdf['raw_name'].isin(ALLOWED_PRODUCTS) | 
                pdf['raw_mm'].isin(ALLOWED_PRODUCTS) | 
                pdf['name'].isin(ALLOWED_PRODUCTS)
            ]
        elif selected_category != "All Categories":
            # ပုံမှန် ကုန်ပစ္စည်းအုပ်စုအလိုက် စစ်ထုတ်ခြင်း
            pdf = pdf[pdf['category'] == selected_category]

        # Search Bar ဖြင့် ထပ်မံ ရှာဖွေနိုင်ခြင်း
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

                            st.markdown(f"""
                                <div class="product-info-box">
                                    <div class="product-title">{prod['name']}</div>
                                    <div class="product-price">{price_str} <span class="product-unit">ks</span></div>
                                </div>
                            """, unsafe_allow_html=True)
                
                # Row တစ်လိုင်းပြီးတိုင်း အောက်ခြေသို့ 35px စာ ဟပေးမည့် စနစ်
                st.markdown('<div style="margin-bottom: 3
