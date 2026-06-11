import ssl
import xmlrpc.client
import pandas as pd
import requests
import json
import base64

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

# သင့် Google Cloud Access Token
DRIVE_ACCESS_TOKEN = "ya29.a0AT3oNZ-5aNq7ejXPP2QngSg4moRSMbQ5cB10B1ZGnvJcgc3FkrxwawqFXkjYeq9wrXntKUGoBKb2YPXaK-_9gFKnTx7kCHGWsQm8F5OBQHp-6517jT3QqD51oBqGnuOF9ASkvb4gNeyh7o5VigugEn2tr2aYcHNf8tTXZaQAc3oTYtGm_HkM4cXI6h9B7at9OC_thuIaCgYKAdcSARcSFQHGX2Miko3PuvFtNoU1NeWCTqIzgg0206"

def upload_to_drive_direct(p_id, base64_image):
    """ Apps Script ကို လုံးဝကျော်ပြီး Google Drive API v3 ထံ Multipart တိုက်ရိုက် Upload တင်သည့်စနစ် """
    if not base64_image or str(base64_image).strip() == "":
        return None
    try:
        image_bytes = base64.b64decode(base64_image)
        
        metadata = {
            "name": f"{p_id}.png",
            "parents": [DRIVE_FOLDER_ID]
        }
        files = {
            "data": ("metadata", json.dumps(metadata), "application/json; charset=UTF-8"),
            "file": ("image/png", image_bytes, "image/png")
        }
        headers = {"Authorization": f"Bearer {DRIVE_ACCESS_TOKEN}"}
        
        # Google Server ဆီ တိုက်ရိုက်ပို့ခြင်း (Apps Script Permissions များနှင့် လုံးဝမသက်ဆိုင်တော့ပါ)
        res = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart", 
            headers=headers, 
            files=files,
            timeout=20
        )
        return res.status_code
    except Exception as e:
        print(f"⚠️ ID {p_id} ၏ပုံအား Drive သို့ တင်ပို့စဉ် Error ဖြစ်သည်: {e}")
        return None

def sync():
    print("🔄 Odoo Production ERP ထံမှ Live Data များနှင့် ဓာတ်ပုံများကို စတင်ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        products = models.execute_kw(DB, uid, PASSWORD, "product.template", "read", [product_ids], {"fields": ["id", "name", "list_price", "categ_id", "image_128"]})
        print(f"📦 ERP ထံမှ ပစ္စည်း {len(products)} ခု ဖတ်ယူပြီးပါပြီ။")

        raw_data_rows = []
        print("📸 ဓာတ်ပုံများကို Google Drive ထဲသို့ Direct API စနစ်ဖြင့် အကွက်ချ သိမ်းဆည်းနေပါသည်...")
        
        for idx, p in enumerate(products):
            p_id = str(p.get("id", ""))
            p_name_en = p.get("name", "")
            p_price = p.get("list_price", 0)
            p_image = p.get("image_128", "")
            
            categ_data = p.get("categ_id", False)
            p_category = [item.strip() for item in categ_data[1].split("/")][-1] if categ_data else "Uncategorized"
            
            # Google Sheet Layout: [ID, Name, Myanmar_Name, Price, Image, Category]
            raw_data_rows.append([p_id, p_name_en, "", p_price, "", p_category])
            
            # ⚡ FIXED LOGIC: Apps Script ခေါ်တာကို လုံးဝဖြုတ်ပစ်ပြီး Google Drive API ဆီသာ တိုက်ရိုက် မောင်းသွင်းခိုင်းခြင်း
            if p_image:
                status = upload_to_drive_direct(p_id, p_image)
                print(f"[{idx+1}/{len(products)}] 📤 Drive Upload for ID {p_id}: Status {status}")

        print("📤 Google Sheet သို့ စာသားဒေတာများ ပို့ဆောင်နေပါသည်...")
        payload = {"is_first": True, "data": raw_data_rows}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
        print(f"✨ [SUCCESS] Final Sheet Sync Status: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync()
