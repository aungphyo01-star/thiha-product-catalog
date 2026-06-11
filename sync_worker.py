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

# သင့် Google Drive Folder ID
DRIVE_FOLDER_ID = "1aZAx_iVZ9g31VmsBdLWpySEARN1vCaP_"

def sync():
    print("🔄 Odoo ERP ထံမှ Live Data များနှင့် ဓာတ်ပုံများကို စတင်ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        products = models.execute_kw(DB, uid, PASSWORD, "product.template", "read", [product_ids], {"fields": ["id", "name", "list_price", "categ_id", "image_128"]})
        print(f"📦 Odoo ထံမှ ပစ္စည်း စုစုပေါင်း {len(products)} ခု ဖတ်ယူပြီးပါပြီ။")

        raw_data_rows = []
        headers = {"Content-Type": "application/json"}
        
        print("📸 ဓာတ်ပုံများကို Google Drive Folder ထဲသို့ တစ်ပုံချင်းစီ စတင်ပို့ဆောင်သိမ်းဆည်းနေပါသည်...")
        
        for idx, p in enumerate(products):
            p_id = str(p.get("id", ""))
            p_name_en = p.get("name", "")
            p_price = p.get("list_price", 0)
            p_image = p.get("image_128", "") # Odoo Base64 Image Text
            
            categ_data = p.get("categ_id", False)
            p_category = [item.strip() for item in categ_data[1].split("/")][-1] if categ_data else "Uncategorized"
            
            # စာသားဒေတာများကို Sheet ထဲပို့ရန် အစုအဖွဲ့ထဲ ထည့်သွင်းခြင်း
            raw_data_rows.append([p_id, p_name_en, "", p_price, "", p_category])
            
            # ⚡ FIXED DRIVE UPLOAD: ပစ္စည်းတွင် ပုံရှိပါက Apps Script Case 1 ထံ တိုက်ရိုက် မောင်းသွင်းခြင်း
            if p_image and str(p_image).strip() != "":
                try:
                    upload_payload = {
                        "action": "drive_upload",
                        "folder_id": DRIVE_FOLDER_ID,
                        "filename": f"{p_id}.png",
                        "image_data": p_image
                    }
                    # Timeout မဖြစ်စေရန် တစ်ပုံချင်းစီ ပေါ့ပေါ့ပါးပါး ပို့သည်
                    tx_res = requests.post(WEB_APP_URL, data=json.dumps(upload_payload), headers=headers)
                    print(f"[{idx+1}/{len(products)}] 📤 Saved Image for ID {p_id}: {tx_res.text}")
                except Exception as img_err:
                    print(f"❌ ID {p_id} ၏ပုံအား သိမ်းဆည်းရန် အခက်အခဲရှိပါသည်: {img_err}")

        # စာသားဒေတာများကို Google Sheet ထဲသို့ တစ်ပြိုင်နက်တည်း သွန်းထည့်ခြင်း
        print("📤 Google Sheet သို့ စာသားဒေတာများ လွှဲပြောင်းတင်ပို့နေပါသည်...")
        payload = {"is_first": True, "data": raw_data_rows}
        
        response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
        print(f"✨ [SUCCESS] Final Sheet Sync Status: {response.text}")
        print(f"💡 အခု မင်းရဲ့ Google Drive Folder ကို ပုံတွေ ဝင်/မဝင် စောင့်ကြည့်နိုင်ပါပြီဗျာ!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync()
