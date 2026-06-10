import ssl
import xmlrpc.client
import pandas as pd
import requests
import json

# --- SSL Bypass ---
ssl._create_default_https_context = ssl._create_unverified_context

# --- Odoo ERP System Configurations ---
URL = "https://odoo-stg.linklusion.co.jp"
DB = "odoo15"
USERNAME = "aungphyo01@gmail.com"
PASSWORD = "9aa38107a400d3666e7e36a3f578e18d20388a06"

# --- Google Sheet Config ---
SPREADSHEET_ID = "1wOuXbwcU9q3Jxgl4s1y2_RImhoY1dy-GdNyAPsHRUnk"

# ⚠️ သင့် Google Sheet ရဲ့ Apps Script Web App URL ကို သေချာပြန်ထည့်ပေးပါဗျာ
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzwLwVZA4TEXEjvtWMvH_aTGPpo1DBoSqicsQF1utj2kZCNMfMUpLMQJ23zO_-yVCH3/exec"

def sync():
    print("🔄 Odoo ERP ထံမှ အင်္ဂလိပ်ဒေတာများ ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        # Odoo ထံမှ ပစ္စည်း ID များ ရှာဖွေခြင်း
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        
        # ⚡ OPTIMIZATION: နေ့တိုင်း အမြန်ဆုံး ပြီးစေရန် id နှင့် name သာ ဆွဲယူသည်
        products = models.execute_kw(DB, uid, PASSWORD, "product.template", "read", [product_ids], {"fields": ["id", "name"]})
        print(f"📦 ပစ္စည်း {len(products)} ခု ဖတ်ယူပြီးပါပြီ။")

        raw_data_rows = []
        for p in products:
            p_id = str(p.get("id", ""))
            p_name_en = p.get("name", "")
            
            # ⚡ Apps Script ရဲ့ Header ["ID", "Name", "Myanmar_Name", "Price", "Image"] အတိုင်း
            # နေရာကွက်တိဖြစ်အောင် ပုံသဏ္ဌာန် ညှိပေးခြင်း (ဈေးနှုန်းနှင့် ပုံကို Blank ထားသည်)
            raw_data_rows.append([p_id, p_name_en, "", "", ""])

        # Google Sheet သို့ ဒေတာများ လွှဲပြောင်းတင်ပို့ခြင်း
        print("📤 Google Sheet သို့ ဒေတာများ ပို့ဆောင်နေပါသည်...")
        payload = {"is_first": True, "data": raw_data_rows}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
        print(f"✨ [SUCCESS] Worker Sync Status: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync()
