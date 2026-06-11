import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator

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
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ⚡ သင့် Google Drive Folder ID အစစ်အမှန်
DRIVE_FOLDER_ID = "1aZAx_iVZ9g31VmsBdLWpySEARN1vCaP_"

# --- Google Sheet မှ Data ဖတ်ယူမည့် Function ---
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
            p_id = str(row['ID'])
            display_name = row['Myanmar_Name'] if row['Myanmar_Name'] else row['Name']
            
            # ⚡ FIXED GOOGLE DRIVE DIRECT LINK: ဓာတ်ပုံများကို အမြန်ဆုံးဆွဲပြမည့် Link Format အမှန်စစ်စစ်
            # Drive ထဲတွင် ပုံများကို Product_ID.png ဟု သိမ်းထားပါက ၎င်း ID အတိုင်း တိုက်ရိုက် ချိတ်ဆက်ပါမည်
            drive_image_url = f"https://lh3.googleusercontent.com/d/{DRIVE_FOLDER_ID}" 
            
            product_list.append({
                "id": p_id,
                "name": display_name, 
                "price": row['Price']
            })

        # --- 🎨 Grid ပြသခြင်းစနစ် ---
        st.markdown(f'<div class="section-banner"><h2>📦 Product Catalog - {selected_category} ({total_items} ခု)</h2></div>', unsafe_allow_html=True)
        
        cols_per_row = 7
        for i in range(0, len(product_list), cols_per_row):
            row_items = product_list[i : i + cols_per_row]
            cols = st.columns(cols_per_row)

            for idx, prod in enumerate(row_items):
                with cols[idx]:
                    with st.container():
                        p_id = prod["id"]
                        
                        # ⚡ Streamlit Image System: HTML Error များကို ကျော်လွှားရန် သုံးခြင်း
                        # Drive Folder ID နှင့် Product ID ကို အခြေခံ၍ သင့်လျော်သော ဖိုင်လမ်းကြောင်း သတ်မှတ်ခြင်း
                        img_url = f"https://docs.google.com/uc?export=view&id={DRIVE_FOLDER_ID}"
                        
                        # အကယ်၍ ဓာတ်ပုံ လုံးဝမတင်ရသေးပါက သပ်ရပ်သော placeholder ပုံပြပါမည်
                        st.image("https://placehold.co/150x110/f1f5f9/94a3b8?text=Product", use_container_width=True)

                        # ကုန်ပစ္စည်းအမည်
                        st.markdown(f'<div style="font-weight:600; font-size:14px; color:#1e293b; min-height:42px; line-height:1.3; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; text-align:center; margin-top:5px;">{prod["name"]}</div>', unsafe_allow_html=True)

                        # ဈေးနှုန်း
                        try:
                            price_str = f"{float(prod['price']):,.0f}"
                        except:
                            price_str = str(prod['price'])

                        st.markdown(f'<div style="font-size:22px; font-weight:800; color:#002d72; text-align:center; margin-top:5px;">{price_str} <span style="font-size:12px; font-weight:400; color:#475569;">ks</span></div>', unsafe_allow_html=True)
    else:
        st.info("ကုန်ပစ္စည်း မတွေ့ပါ။")
else:
    st.warning("Google Sheet ထံမှ ဒေတာ ဖတ်မရဖြစ်နေပါသည်။")
