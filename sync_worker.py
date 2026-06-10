import ssl
import xmlrpc.client
import pandas as pd
import requests
import json
from deep_translator import GoogleTranslator

# --- SSL Bypass ---
ssl._create_default_https_context = ssl._create_unverified_context

# --- Odoo ERP System Configurations ---
URL = "https://odoo-stg.linklusion.co.jp"
DB = "odoo15"
USERNAME = "aungphyo01@gmail.com"
PASSWORD = "9aa38107a400d3666e7e36a3f578e18d20388a06"

# --- Google Sheet Config ---
SPREADSHEET_ID = "1wOuXbwcU9q3Jxgl4s1y2_RImhoY1dy-GdNyAPsHRUnk"

# ⚠️ သင့် Google Sheet ၏ Apps Script Web App URL ကို ဤနေရာတွင် မဖြစ်မနေ ပြန်ထည့်ပါ
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzwLwVZA4TEXEjvtWMvH_aTGPpo1DBoSqicsQF1utj2kZCNMfMUpLMQJ23zO_-yVCH3/exec"

def sync():
    print("🔄 Odoo ERP ထံမှ ကုန်ပစ္စည်းဒေတာများ စတင်ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        # ပစ္စည်း ID များ ရှာဖွေခြင်း (Limit အခု ၁၀၀၀ အထိ မြှင့်ထားသည်)
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 1000})
        products = models.execute_kw(DB, uid, PASSWORD, "product.template", "read", [product_ids], {"fields": ["id", "name"]})
        print(f"📦 Odoo ထံမှ ပစ္စည်း {len(products)} ခု ဖတ်ယူပြီးပါပြီ။")

        # Google Translator Engine အား အင်္ဂလိပ်မှ မြန်မာသို့ ပြန်ရန် သတ်မှတ်ခြင်း
        translator = GoogleTranslator(source='en', target='my')

        raw_data_rows = []
        print("🔤 Google Translate စနစ်ဖြင့် မြန်မာအမည်များကို အလိုအလျောက် ပြန်ဆိုနေပါသည်...")
        
        for idx, p in enumerate(products):
            p_id = str(p.get("id", ""))
            p_name_en = p.get("name", "")
            
            # ⚡ AUTO TRANSLATE LOGIC: အင်္ဂလိပ်နာမည်ကို မြန်မာလို အလိုအလျောက် ပြန်ဆိုခြင်း
            try:
                if p_name_en:
                    p_name_mm = translator.translate(p_name_en)
                else:
                    p_name_mm = ""
            except Exception as tx_err:
                print(f"⚠️ {p_name_en} အား ဘာသာပြန်ရန် ခေတ္တအခက်အခဲရှိသဖြင့် ကွက်လပ်ထားပါသည်: {tx_err}")
                p_name_mm = ""
                
            # တိုးတက်မှု အခြေအနေအား Console တွင် ထုတ်ပြခြင်း
            print(f"[{idx+1}/{len(products)}] Translated: {p_name_en} -> {p_name_mm}")
            
            # Web App Backend Formatter အတိုင်း စီစဉ်ခြင်း
            raw_data_rows.append([p_id, p_name_en, p_name_mm, "", ""])

        # Google Sheet ထဲသို့ ဒေတာများ တိုက်ရိုက် Overwrite သွန်းထည့်ခြင်း
        print("📤 Google Sheet သို့ ဒေတာများ လွှဲပြောင်းနေပါသည်...")
        payload = {"is_first": True, "data": raw_data_rows}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
        print(f"✨ [SUCCESS] Sync Status: {response.text}")
        print("💡 အခု သင့် Google Sheet ထဲတွင် မြန်မာနာမည်များ အလိုအလျောက် ရောက်ရှိသွားပါပြီ။")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync()
