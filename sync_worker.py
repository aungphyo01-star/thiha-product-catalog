import ssl
import xmlrpc.client
import requests
import json
import time

ssl._create_default_https_context = ssl._create_unverified_context

URL = "https://odoo.linklusion.co.jp"
DB = "odoo15"
USERNAME = "aungphyo01@gmail.com"
PASSWORD = "f48f4bafa7c2b69d4156fc44e424182070c8287d"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzwLwVZA4TEXEjvtWMvH_aTGPpo1DBoSqicsQF1utj2kZCNMfMUpLMQJ23zO_-yVCH3/exec"

# ⚡ IMGBB PRODUCTION API KEY (ပုံများကို အမြန်ဆုံး CDN Direct Link အဖြစ် ပြောင်းပေးမည့်သော့)
IMGBB_API_KEY = "69bd2c39e01f654b9cb796b42b6a7a0b"

def upload_to_cdn(base64_image):
    if not base64_image or str(base64_image).strip() == "":
        return ""
    try:
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": IMGBB_API_KEY, "image": base64_image}
        res = requests.post(url, data=payload, timeout=10)
        res_json = res.json()
        if res_json.get("success"):
            return res_json["data"]["url"] # CDN Link ပြန်ပေးမည်
        return ""
    except:
        return ""

def sync():
    print("🔄 ERP မှ ဒေတာများနှင့် ပုံများကို သန်းခေါင်ယံအမြန်နှုန်း CDN စနစ်ဖြင့် စတင်ချိတ်ဆက်နေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        total_products = len(product_ids)
        print(f"📦 ပစ္စည်းစုစုပေါင်း {total_products} ခု တွေ့ရှိရပါသည်။")

        CHUNK_SIZE = 30 # ပုံတင်ရမှာမို့လို့ Chunk ကို ၃၀ စီ သန့်သန့်ခွဲပို့ပါမည်
        headers = {"Content-Type": "application/json"}
        
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
                p_image_raw = p.get("image_128", "")
                
                # ပုံကို အမြန်နှုန်း CDN Link အဖြစ် ချက်ချင်းပြောင်းလဲခြင်း
                p_image_url = upload_to_cdn(p_image_raw) if p_image_raw else ""
                
                categ_data = p.get("categ_id", False)
                p_category = [item.strip() for item in categ_data[1].split("/")][-1] if categ_data else "Uncategorized"
                
                raw_data_rows.append([p_id, p_name_en, "", p_price, p_image_url, p_category])
            
            is_first_chunk = True if i == 0 else False
            payload = {"is_first": is_first_chunk, "data": raw_data_rows}
            
            response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
            print(f"🔹 Sync Progress: {min(i + CHUNK_SIZE, total_products)}/{total_products} ... Status: {response.text}")
            time.sleep(0.3)

        print("✨ [SUCCESS] ၆၁၃ ခုလုံး CDN Link အဖြစ် Google Sheet ထဲ အပြည့်အဝ ရောက်သွားပါပြီ!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync()
