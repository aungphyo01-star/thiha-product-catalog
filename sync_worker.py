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

# --- Google Sheet Config ---
SPREADSHEET_ID = "1wOuXbwcU9q3Jxgl4s1y2_RImhoY1dy-GdNyAPsHRUnk"

# ⚠️ သင့် Google Sheet ရဲ့ Apps Script Web App URL အစစ်ကို ပြန်ထည့်ပါ
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzwLwVZA4TEXEjvtWMvH_aTGPpo1DBoSqicsQF1utj2kZCNMfMUpLMQJ23zO_-yVCH3/exec"

def sync():
    print("🔄 Odoo ERP ထံမှ ကုန်ပစ္စည်းများနှင့် Category များကို ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        
        # ⚡ OPTIMIZATION: ကတ္တဂိုရီ (categ_id) ကိုပါ တွဲဖတ်ရန် တောင်းဆိုခြင်း
        products = models.execute_kw(DB, uid, PASSWORD, "product.template", "read", [product_ids], {"fields": ["id", "name", "categ_id"]})
        print(f"📦 Odoo ထံမှ ပစ္စည်း {len(products)} ခု ဖတ်ယူပြီးပါပြီ။")

        raw_data_rows = []
        for p in products:
            p_id = str(p.get("id", ""))
            p_name_en = p.get("name", "")
            
            # Category နာမည်ကို ယူခြင်း (Odoo က [ID, "Name"] ဟု ပြန်သဖြင့် နာမည်ကိုသာ ဖြတ်ယူသည်)
            categ_data = p.get("categ_id", False)
            p_category = categ_data[1] if categ_data else "Uncategorized"
            
            # ⚡ Price နေရာတွင် Category နာမည်အား သတ်မှတ်သိမ်းဆည်းလိုက်ပါသည်
            raw_data_rows.append([p_id, p_name_en, "", p_category, ""])

        print("📤 Google Sheet သို့ ဒေတာများ တင်ပို့နေပါသည်...")
        payload = {"is_first": True, "data": raw_data_rows}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
        print(f"✨ [SUCCESS] Sync Status: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync()
