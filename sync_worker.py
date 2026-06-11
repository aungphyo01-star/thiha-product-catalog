import ssl
import xmlrpc.client
import pandas as pd
import requests
import json
import base64
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

# သင့် Google Drive Folder ID
DRIVE_FOLDER_ID = "1aZAx_iVZ9g31VmsBdLWpySEARN1vCaP_"

# ⚠️ သင့် Google Drive API Access Token အသစ်စက်စက်ကို ဤနေရာတွင် သေချာစွာ ထည့်သွင်းပေးပါဦးဗျာ
DRIVE_ACCESS_TOKEN = "ya29.a0AT3oNZ-5aNq7ejXPP2QngSg4moRSMbQ5cB10B1ZGnvJcgc3FkrxwawqFXkjYeq9wrXntKUGoBKb2YPXaK-_9gFKnTx7kCHGWsQm8F5OBQHp-6517jT3QqD51oBqGnuOF9ASkvb4gNeyh7o5VigugEn2tr2aYcHNf8tTXZaQAc3oTYtGm_HkM4cXI6h9B7at9OC_thuIaCgYKAdcSARcSFQHGX2Miko3PuvFtNoU1NeWCTqIzgg0206"

def upload_to_drive_direct(p_id, base64_image):
    """ Cloud Worker မှ Google Drive Folder ထဲသို့ ပုံများကို တိုက်ရိုက် Multipart Upload တင်သည့် စနစ် """
    if not base64_image or str(base64_image).strip() == "":
        return "No Image Data"
    try:
        # Base64 Text အား ပုံဖိုင် Binary အဖြစ် ပြောင်းလဲခြင်း
        image_bytes = base64.b64decode(base64_image)
        
        # Google Drive API v3 ရဲ့ တရားဝင် Metadata
        metadata = {
            "name": f"{p_id}.png",
            "parents": [DRIVE_FOLDER_ID]
        }
        
        files = {
            "data": ("metadata", json.dumps(metadata), "application/json; charset=UTF-8"),
            "file": ("image/png", image_bytes, "image/png")
        }
        
        headers = {"Authorization": f"Bearer {DRIVE_ACCESS_TOKEN}"}
        
        # Google Drive API Server ဆီသို့ တိုက်ရိုက်သွားရောက် ရေးသွင်းခြင်း
        res = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart", 
            headers=headers, 
            files=files,
            timeout=20
        )
        return res.status_code
    except Exception as e:
        return f"Upload Failed: {str(e)}"

def sync():
    print("🔄 Odoo Production ERP ထံမှ Live Data များနှင့် ဓာတ်ပုံများကို စတင်ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        # ၁။ ရောင်းချမည့် ပစ္စည်း ID စာရင်းအားလုံးကို ရှာဖွေရယူခြင်း
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        total_products = len(product_ids)
        print(f"📦 ERP ထံတွင် ရောင်းချမည့် ကုန်ပစ္စည်းစုစုပေါင်း {total_products} ခု တွေ့ရှိရပါသည်။")

        # ⚡ CHUNK PAGINATION SYSTEM: Network ဒဏ်မပိစေရန် ပစ္စည်း ၄၀ စီစီ ခွဲခွဲ၍ ဆွဲယူခြင်း
        CHUNK_SIZE = 40
        all_fetched_products = []
        
        # ⚡ FIXED: စာသားအပိတ် မျက်တောင်ကွင်းနှင့် ကွင်းပိတ်များအား အမှားအယွင်းမရှိစေရန် တည့်မတ်ထားပါသည်
        print(f"🔄 ဒေတာဝန်ပေါ့စေရန် ပစ္စည်းများကို အုပ်စုငယ် ({CHUNK_SIZE} ခုစီ) ခွဲ၍ စတင်ဒေါင်းလုဒ်ဆွဲနေပါသည်...")
        
        for i in range(0, total_products, CHUNK_SIZE):
            chunk_ids = product_ids[i : i + CHUNK_SIZE]
            chunk_products = models.execute_kw(
                DB, uid, PASSWORD, "product.template", "read", 
                [chunk_ids], {"fields": ["id", "name", "list_price", "categ_id", "image_128"]}
            )
            all_fetched_products.extend(chunk_products)
            print(f"🔹 ဒေါင်းလုဒ်ဆွဲပြီးစီးမှု: {len(all_fetched_products)}/{total_products} ခု...")
            time.sleep(0.3)

        raw_data_rows = []
        print("📸 ဓာတ်ပုံများကို Google Drive Folder ထဲသို့ Direct API စနစ်ဖြင့် စတင်ပို့ဆောင်သိည်းဆည်းနေပါသည်...")
        
        for idx, p in enumerate(all_fetched_products):
            p_id = str(p.get("id", ""))
            p_name_en = p.get("name", "")
            p_price = p.get("list_price", 0)
            p_image = p.get("image_128", "") # Odoo Base64 Image Text
            
            categ_data = p.get("categ_id", False)
            p_category = [item.strip() for item in categ_data[1].split("/")][-1] if categ_data else "Uncategorized"
            
            # Google Sheet ကော်လံတည်ဆောက်ပုံအတိုင်း Row ဒေတာ ပြင်ဆင်ခြင်း [ID, Name, Myanmar_Name, Price, Image, Category]
            raw_data_rows.append([p_id, p_name_en, "", p_price, "", p_category])
            
            # ⚡ DIRECT GOOGLE DRIVE UPLOAD: ပစ္စည်းတွင် ဓာတ်ပုံပါရှိက Drive API ဆီ တိုက်ရိုက် လှမ်းတင်ခိုင်းခြင်း
            if p_image and str(p_image).strip() != "":
                status = upload_to_drive_direct(p_id, p_image)
                print(f"[{idx+1}/{len(all_fetched_products)}] 📤 Drive Upload for ID {p_id}: Status {status}")

        print("📤 Google Sheet သို့ စာသားဒေတာများ ပို့ဆောင်နေပါသည်...")
        # Payload ဒေတာအုံကြီးတစ်ခုတည်းအဖြစ် Sheet Web App ထံသို့ ပို့ဆောင်ခြင်း (ဓာတ်ပုံစာသားများမပါ၍ ပေါ့ပါးပါသည်)
        payload = {"is_first": True, "data": raw_data_rows}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
        print(f"✨ [SUCCESS] Final Sheet Sync Status: {response.text}")
        print("💡 ယခု သင်၏ Google Drive Folder နှင့် Catalog အား စစ်ဆေးနိုင်ပါပြီဗျာ!")
        
    except Exception as e:
        print(f"❌ စနစ်လည်ပတ်မှု Error ဖြစ်ပွားသည်: {e}")

if __name__ == "__main__":
    sync()
