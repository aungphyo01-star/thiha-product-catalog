import ssl
import xmlrpc.client
import pandas as pd
import requests
import json

# --- SSL Bypass ---
ssl._create_default_https_context = ssl._create_unverified_context

# --- Odoo ERP System Credentials ---
URL = "https://odoo.linklusion.co.jp"
DB = "odoo15"
USERNAME = "aungphyo01@gmail.com"
PASSWORD = "f48f4bafa7c2b69d4156fc44e424182070c8287d"

# --- Google Sheet Web App URL ---
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzwLwVZA4TEXEjvtWMvH_aTGPpo1DBoSqicsQF1utj2kZCNMfMUpLMQJ23zO_-yVCH3/exec"

def sync():
    print("🔄 Odoo ERP ထံမှ ကုန်ပစ္စည်းများနှင့် ဓာတ်ပုံများကို စတင်ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        # ရောင်းချမည့် ပစ္စည်းအားလုံးကို ရှာဖွေခြင်း
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        
        # ⚡ FIXED: image_128 (ဓာတ်ပုံဒေတာ) ကိုပါ Odoo ထံမှ တစ်ခါတည်း တွဲဖတ်ရန် တောင်းဆိုလိုက်ပါသည်
        products = models.execute_kw(DB, uid, PASSWORD, "product.template", "read", [product_ids], {"fields": ["id", "name", "list_price", "categ_id", "image_128"]})
        print(f"📦 Odoo ထံမှ ပစ္စည်းနှင့် ဓာတ်ပုံ {len(products)} ခု ဖတ်ယူပြီးပါပြီ။")

        raw_data_rows = []
        for p in products:
            p_id = str(p.get("id", ""))
            p_name_en = p.get("name", "")
            p_price = p.get("list_price", 0)
            p_image = p.get("image_128", "")  # Base64 string စစ်စစ် ရရှိမည်
            
            # Category နာမည် သန့်စင်ခြင်း
            categ_data = p.get("categ_id", False)
            p_category = [item.strip() for item in categ_data[1].split("/")][-1] if categ_data else "Uncategorized"
            
            # ⚡ FIXED Structure: [ID, Name, Myanmar_Name, Price, Image, Category] အတိုင်း နေရာကွက်တိ သွင်းခြင်း
            raw_data_rows.append([p_id, p_name_en, "", p_price, p_image, p_category])

        print("📤 Google Sheet သို့ ဒေတာနှင့် ဓာတ်ပုံများ လွှဲပြောင်းတင်ပို့နေပါသည်...")
        payload = {"is_first": True, "data": raw_data_rows}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
        print(f"✨ [SUCCESS] Sync Status: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync()
