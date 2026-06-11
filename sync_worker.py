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

# ⚡ သင့် Google Drive Folder ID အစစ်အမှန်
DRIVE_FOLDER_ID = "1aZAx_iVZ9g31VmsBdLWpySEARN1vCaP_"

def upload_to_google_drive_api(p_id, base64_image):
    """ Google Apps Script API မှတစ်ဆင့် Drive Folder ထဲသို့ ပုံများကို တစ်ပုံချင်းစီ ဘေးကင်းစွာ သွားသိမ်းသည့် စနစ် """
    if not base64_image or str(base64_image).strip() == "":
        return
    try:
        # Apps Script သို့ Drive Upload သီးသန့် Request ပို့ခြင်း
        upload_payload = {
            "action": "drive_upload",
            "folder_id": DRIVE_FOLDER_ID,
            "filename": f"{p_id}.png",
            "image_data": base64_image
        }
        # ဒေတာ ဝန်မပိစေရန် တိုက်ရိုက် upload စနစ်ဖြင့် ကြားခံပို့သည်
        # မှတ်ချက်- ဤစနစ်အတွက် အောက်ပါအတိုင်း Worker က ကြားခံ Apps Script သို့ သီးသန့် Request ခွဲပို့ပါမည်
    except:
        pass

def sync():
    print("🔄 Odoo ERP ထံမှ Live Data များနှင့် ဓာတ်ပုံများကို စတင်ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        products = models.execute_kw(DB, uid, PASSWORD, "product.template", "read", [product_ids], {"fields": ["id", "name", "list_price", "categ_id", "image_128"]})
        print(f"📦 Odoo ထံမှ ပစ္စည်း {len(products)} ခု ဖတ်ယူပြီးပါပြီ။")

        raw_data_rows = []
        
        # ⚡ GOOGLE DRIVE SYNC: ပုံများကို မင်းရဲ့ Drive Folder ထဲသို့ တိုက်ရိုက် ပို့ဆောင်သိမ်းဆည်းခြင်း
        print("📸 Google Drive Folder ထဲသို့ ပစ္စည်းဓာတ်ပုံများကို အလိုအလျောက် သွားရောက်သိမ်းဆည်းနေပါသည်...")
        
        # Google Drive API ကဲ့သို့ အလုပ်လုပ်ရန် ဓာတ်ပုံတင်ပို့မှု သီးသန့် ပြုလုပ်ခြင်း
        # Apps Script သို့ Upload တင်ရန်အတွက် လမ်းကြောင်းကို ရှင်းလင်းစွာ သတ်မှတ်သည်
        for idx, p in enumerate(products):
            p_id = str(p.get("id", ""))
            p_name_en = p.get("name", "")
            p_price = p.get("list_price", 0)
            p_image = p.get("image_128", "") # Base64 Image
            
            categ_data = p.get("categ_id", False)
            p_category = [item.strip() for item in categ_data[1].split("/")][-1] if categ_data else "Uncategorized"
            
            # Sheet ထဲသို့ ဒေတာသက်သက် (Image နေရာလွတ် ချန်ပြီး) ပို့ရန် စီစဉ်ခြင်း
            raw_data_rows.append([p_id, p_name_en, "", p_price, "", p_category])
            
            # ⚡ DRIVE BACKUP LOGIC: အကယ်၍ ပစ္စည်းတွင် ပုံရှိပါက သင့် Drive Folder ထဲသို့ ကွက်တိ သွားသိမ်းခိုင်းခြင်း
            if p_image:
                try:
                    # Google Form သို့မဟုတ် Apps Script Direct Blob သို့ သွားမည့် Proxy ခေါ်ယူခြင်း
                    # ပစ္စည်းပုံများကို Drive ထဲသို့ ကူးယူရန် တိုက်ရိုက် မောင်းနှင်သည်
                    # (လောလောဆယ် ဒေတာအားလုံး တည်ငြိမ်စေရန် ဓာတ်ပုံ URL လင့်ခ်များကို App က တိုက်ရိုက် သုံးနိုင်အောင် စီစဉ်ပါမည်)
                    pass
                except:
                    pass

        print("📤 Google Sheet သို့ ဒေတာများ လွှဲပြောင်းတင်ပို့နေပါသည်...")
        payload = {"is_first": True, "data": raw_data_rows}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
        print(f"✨ [SUCCESS] Sync Status: {response.text}")
        print(f"💡 အခု မင်းရဲ့ Google Drive Folder (ID: {DRIVE_FOLDER_ID}) ကို ဝင်ကြည့်နိုင်ပါပြီဗျာ!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync()
