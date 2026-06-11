import ssl
import xmlrpc.client
import pandas as pd
import requests
import json
import time

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
    print("🔄 Odoo Production ERP ထံမှ Live Data များကို စတင်ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        # ၁။ ရောင်းချမည့် ပစ္စည်း ID စာရင်းအားလုံးကို ရယူခြင်း
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        total_products = len(product_ids)
        print(f"📦 ERP ထံတွင် ရောင်းချမည့် ပစ္စည်းစုစုပေါင်း {total_products} ခု တွေ့ရှိရပါသည်။")

        # ⚡ CHUNK PAGINATION: Odoo ဆီကနေ ၄၀ စီ စနစ်တကျ ခွဲဆွဲပြီး စနစ်ထဲမှာ အရင်အကုန်စုသည်
        CHUNK_SIZE = 40
        all_fetched_products = []
        
        for i in range(0, total_products, CHUNK_SIZE):
            chunk_ids = product_ids[i : i + CHUNK_SIZE]
            chunk_products = models.execute_kw(
                DB, uid, PASSWORD, "product.template", "read", 
                [chunk_ids], {"fields": ["id", "name", "list_price", "categ_id"]} # ⚡ FIXED: image_128 ကို လုံးဝ မခေါ်တော့ပါ
            )
            all_fetched_products.extend(chunk_products)
            print(f"🔹 ဒေါင်းလုဒ်ဆွဲပြီးစီးမှု: {len(all_fetched_products)}/{total_products} ခု...")
            time.sleep(0.2)

        # ဒေတာအားလုံးကို စာသားသက်သက်အဖြစ် အပေါ့ပါးဆုံး ပြင်ဆင်ခြင်း
        raw_data_rows = []
        for p in all_fetched_products:
            p_id = str(p.get("id", ""))
            p_name_en = p.get("name", "")
            p_price = p.get("list_price", 0)
            
            categ_data = p.get("categ_id", False)
            p_category = [item.strip() for item in categ_data[1].split("/")][-1] if categ_data else "Uncategorized"
            
            # Layout: [ID, Name, Myanmar_Name, Price, Image, Category]
            raw_data_rows.append([p_id, p_name_en, "", p_price, "", p_category])
            
        print(f"📤 ပစ္စည်း {len(raw_data_rows)} ခုစလုံးကို Google Sheet ထဲသို့ တစ်ပြိုင်နက်တည်း အပြတ်သွန်းထည့်နေပါသည်...")
        
        payload = {"is_first": True, "data": raw_data_rows}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
        print(f"✨ [SUCCESS] Final Sheet Sync Status: {response.text}")
        print(f"💡 အခု ပစ္စည်း ၆溝 ကျော်လုံး Google Sheet ထဲ ကွက်တိ ရောက်သွားပါပြီဗျာ!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync()
