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

# ⚡ FREE IMAGE HOSTING API KEY (ImgBB ရဲ့ အခမဲ့ API Key ဖြစ်ပြီး ပုံများကို ရေရှည် Direct Link ပြောင်းပေးပါမည်)
IMGBB_API_KEY = "69bd2c39e01f654b9cb796b42b6a7a0b"

def upload_image_to_host(base64_image):
    """ Base64 Image စာသားအား အင်တာနက်ပေါ်သို့ တိုက်ရိုက်တင်ပြီး သန့်စင်သော Live URL အဖြစ် ပြောင်းလဲပေးသည့်စနစ် """
    if not base64_image or str(base64_image).strip() == "":
        return ""
    try:
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": IMGBB_API_KEY,
            "image": base64_image
        }
        res = requests.post(url, data=payload, timeout=15)
        res_json = res.json()
        if res_json.get("success"):
            return res_json["data"]["url"] # ⚡ တကယ့် Live Direct Link (https://...) ပြန်ပေးမည်
        return ""
    except:
        return ""

def sync():
    print("🔄 Odoo Production ERP ထံမှ Live Data များနှင့် ဓာတ်ပုံများကို စတင်ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        total_products = len(product_ids)
        print(f"📦 ERP ထံတွင် ရောင်းချမည့် ပစ္စည်းစုစုပေါင်း {total_products} ခု တွေ့ရှိရပါသည်။")

        # ⚡ CHUNK PAGINATION SYSTEM: Network ဒဏ်မပိစေရန် ပစ္စည်း ၄၀ စီစီ ခွဲခွဲ၍ ဆွဲယူခြင်း
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
            for idx, p in enumerate(chunk_products):
                p_id = str(p.get("id", ""))
                p_name_en = p.get("name", "")
                p_price = p.get("list_price", 0)
                p_image_raw = p.get("image_128", "") 
                
                # ⚡ IMAGE HOSTING STRATEGY: ပုံရှိပါက Host ပေါ်တင်ပြီး သန့်ရှင်းသော URL Link အဖြစ် ပြောင်းလဲခြင်း
                p_image_url = ""
                if p_image_raw and p_image_raw != "":
                    p_image_url = upload_image_to_host(p_image_raw)
                
                categ_data = p.get("categ_id", False)
                p_category = [item.strip() for item in categ_data[1].split("/")][-1] if categ_data else "Uncategorized"
                
                # Live URL Link အား Image (ကော်လံ E) နေရာတွင် စာသားအကျဉ်းလေးအဖြစ် သိမ်းဆည်းသဖြင့် Quota ပြည့်စရာ အကြောင်းမရှိတော့ပါ
                raw_data_rows.append([p_id, p_name_en, "", p_price, p_image_url, p_category])
                print(f"   ↳ [{i + idx + 1}/{total_products}] ID {p_id} -> Link Created")
            
            # ပထမဆုံးအုပ်စုဆိုလျှင် Sheet အဟောင်းကို ရှင်းထုတ်ခိုင်းမည်
            is_first_chunk = True if i == 0 else False
            payload = {"is_first": is_first_chunk, "data": raw_data_rows}
            
            response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
            print(f"🔹 တင်ပို့ပြီးစီးမှု: {min(i + CHUNK_SIZE, total_products)}/{total_products} ခု... Status: {response.text}")
            time.sleep(0.5)

        print("✨ [SUCCESS] စနစ်တစ်ခုလုံး ဒေတာ ၆၁၃ ခုလုံးနှင့် ဓာတ်ပုံ Live URL များ Google Sheet ထဲသို့ အပြည့်အဝ ဝင်သွားပါပြီ!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync()
