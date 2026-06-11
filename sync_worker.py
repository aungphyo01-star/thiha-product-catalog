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
    print("🔄 Odoo Production ERP ထံမှ Live Data များနှင့် ဓာတ်ပုံများကို စတင်ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        # ရောင်းချမည့် ပစ္စည်း ID စာရင်းအားလုံးကို အရင်ယူခြင်း
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        total_products = len(product_ids)
        print(f"📦 ERP ထံတွင် ရောင်းချမည့် ပစ္စည်းစုစုပေါင်း {total_products} ခု တွေ့ရှိရပါသည်။")

        # ⚡ CHUNK SYNC: ဒေတာ ဝန်မပိစေရန် ပစ္စည်း ၄၀ စီစီပဲ ခွဲဆွဲပြီး Google Sheet သို့ ပို့မည့်စနစ်
        CHUNK_SIZE = 40
        headers = {"Content-Type": "application/json"}
        
        print(f"🚀 ပစ္စည်းများကို အုပ်စုငယ် ({CHUNK_SIZE} ခုစီ) ခွဲ၍ Google Sheet သို့ စတင်မောင်းသွင်းနေပါသည်...")
        
        for i in range(0, total_products, CHUNK_SIZE):
            chunk_ids = product_ids[i : i + CHUNK_SIZE]
            chunk_products = models.execute_kw(
                DB, uid, PASSWORD, "product.template", "read", 
                [chunk_ids], {"fields": ["id", "name", "list_price", "categ_id", "image_128"]}
            )
            
            raw_data_rows = []
            for p in chunk_products:
                p_id = str(p.get("id", ""))
                p_name_en = p.get("name", "")
                p_price = p.get("list_price", 0)
                p_image = p.get("image_128", "") # Base64 Image Text
                
                categ_data = p.get("categ_id", False)
                p_category = [item.strip() for item in categ_data[1].split("/")][-1] if categ_data else "Uncategorized"
                
                # Layout: [ID, Name, Myanmar_Name, Price, Image, Category]
                raw_data_rows.append([p_id, p_name_en, "", p_price, p_image, p_category])
            
            # Google Sheet Apps Script ထံသို့ အပိုင်းလိုက် ခွဲပို့ခြင်း
            # ပထမဆုံးအုပ်စုဆိုလျှင် Sheet ကိုအရင် ရှင်းခိုင်းမည် (is_first Logic)
            is_first_chunk = True if i == 0 else False
            payload = {"is_first": is_first_chunk, "data": raw_data_rows}
            
            response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
            print(f"🔹 တင်ပို့ပြီးစီးမှု: {min(i + CHUNK_SIZE, total_products)}/{total_products} ခု... Status: {response.text}")
            time.sleep(0.8) # Google Rate Limit မမိစေရန် ခဏနားပေးခြင်း

        print("✨ [SUCCESS] စနစ်တစ်ခုလုံး ဒေတာနှင့် ဓာတ်ပုံများ Google Sheet ထဲသို့ အောင်မြင်စွာ ဝင်သွားပါပြီ!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync()
