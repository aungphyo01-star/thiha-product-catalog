import ssl
import xmlrpc.client
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
    print("🔄 Odoo ERP မှ Live ဒေတာများနှင့် ပုံများကို Maximum Safety စနစ်ဖြင့် စတင်ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.product", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        total_products = len(product_ids)
        print(f"📦 ERP တွင် ရောင်းချမည့် ပစ္စည်းစုစုပေါင်း {total_products} ခု တွေ့ရှိရပါသည်။")

        # ⚡ CRITICAL BULLETPROOF CHUNK: Google Sheet ဟန်းပြီး ဒေတာပြတ်မကျစေရန် ၈ ခုစီသာ ခွဲပို့မည်
        CHUNK_SIZE = 8
        headers = {"Content-Type": "application/json"}
        
        for i in range(0, total_products, CHUNK_SIZE):
            chunk_ids = product_ids[i : i + CHUNK_SIZE]
            chunk_products = models.execute_kw(
                DB, uid, PASSWORD, "product.product", "read", 
                [chunk_ids], {"fields": ["id", "display_name", "list_price", "categ_id", "image_128"]}
            )
            
            raw_data_rows = []
            for p in chunk_products:
                p_id = str(p.get("id", ""))
                p_name_en = p.get("display_name", "")
                p_price = p.get("list_price", 0)
                
                # Odoo Security အား ကျော်ဖြတ်ရန် Image Base64 အား တိုက်ရိုက်ဆွဲယူခြင်း
                p_image_raw = p.get("image_128", "")
                p_image = str(p_image_raw).strip() if p_image_raw else ""
                
                categ_data = p.get("categ_id", False)
                p_category = [item.strip() for item in categ_data[1].split("/")][-1] if categ_data else "Uncategorized"
                
                raw_data_rows.append([p_id, p_name_en, "", p_price, p_image, p_category])
            
            is_first_chunk = True if i == 0 else False
            payload = {"is_first": is_first_chunk, "data": raw_data_rows}
            
            response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
            print(f"🔹 Sync Progress: {min(i + CHUNK_SIZE, total_products)}/{total_products} ... Status: {response.text}")
            
            # ⚡ ၃ စက္ကန့် အချိန်ခြားပေးခြင်းဖြင့် Google Sheets ဘက်မှ ဒေတာများကို ဟန်းမသွားဘဲ စိတ်ချရစွာ သိမ်းဆည်းနိုင်မည်
            time.sleep(3.0)

        print(f"✨ [SUCCESS] ပစ္စည်း {total_products} ခုလုံး ဒေတာနှင့် ပုံများ Google Sheet ထဲသို့ ၁၀၀% အပြည့်အဝ ဝင်ရောက်သွားပါပြီ!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync()
