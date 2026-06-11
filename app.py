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
    # Google Sheet Column တကယ့်တည်ဆောက်ပုံအတိုင်း နာမည်ပေးခြင်း
    base_columns = ['ID', 'Name', 'Myanmar_Name', 'Price', 'Image', 'Category']
    df.columns = base_columns + list(df.columns[len(base_columns):])
    
    parsed_products = []
    
    for index, row in df.iterrows():
        p_id = str(row['ID']).strip() if pd.notna(row['ID']) else ""
        p_name = str(row['Name']).strip() if pd.notna(row['Name']) else ""
        p_myanmar = str(row['Myanmar_Name']).strip() if pd.notna(row['Myanmar_Name']) else ""
        p_img_id = str(row['Image']).strip() if pd.notna(row['Image']) else ""
        
        try:
            p_price = float(row['Price'])
        except:
            p_price = 0.0
            
        p_category = str(row['Category']).strip() if pd.notna(row['Category']) else "Uncategorized"
        if p_category.lower() == "nan" or p_category == "":
            p_category = "Uncategorized"
            
        display_title = p_myanmar if (p_myanmar and p_myanmar.lower() != "nan") else p_name
        
        parsed_products.append({
            "id": p_id,
            "name": display_title,
            "price": p_price,
            "image_id": p_img_id,
            "category": p_category
        })
        
    pdf = pd.DataFrame(parsed_products)

    # Filter UI
    categories = ["All Categories"] + sorted(pdf['category'].unique().tolist())
    selected_category = st.selectbox("📂 ကုန်ပစ္စည်းအုပ်စု (Category) အလိုက် စစ်ထုတ်ကြည့်ရှုရန်", categories)
    
    # Search Box
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
                        
                        # ⚡ BULLETPROOF GOOGLE DRIVE EXPORT LINK:
                        # Sheet ထဲက Image (E Column) ထဲမှာ ရှိနေမည့် Google Drive File ID ကိုသုံးပြီး တရားဝင် Direct Link ဖြင့် ပြသခြင်း၊
                        # အကယ်၍ File ID မရှိပါက ပုံပျက်မထွက်စေဘဲ သပ်ရပ်သော Placeholder စမတ်ကတ်လေး ပြောင်းပြပေးမည့်စနစ်
                        if prod["image_id"] and prod["image_id"].lower() != "nan" and prod["image_id"] != "":
                            drive_img_url = f"https://docs.google.com/uc?export=view&id={prod['image_id']}"
                        else:
                            drive_img_url = "https://placehold.co/100x90/f1f5f9/94a3b8?text=📦+Product"
                        
                        st.markdown(f"""
                            <div style="text-align:center; height:90px; display:flex; align-items:center; justify-content:center;">
                                <img src="{drive_img_url}" 
                                     style="max-height:90px; max-width:100%; object-fit:contain; border-radius:6px;"
                                     onerror="this.onerror=null; this.src='https://placehold.co/100x90/f1f5f9/94a3b8?text=📦+Product';">
                            </div>
                        """, unsafe_allow_html=True)

                        try:
                            price_str = f"{int(prod['price']):,}"
                        except:
                            price_str = str(prod['price'])

                        # အမည်နှင့် စျေးနှုန်း ကွက်တိကပ်လျက် တည်ဆောက်ပုံ
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
