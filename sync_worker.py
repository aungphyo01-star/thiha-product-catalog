import ssl
import xmlrpc.client
import pandas as pd
import requests
import json

ssl._create_default_https_context = ssl._create_unverified_context

URL = "https://odoo-stg.linklusion.co.jp"
DB = "odoo15"
USERNAME = "aungphyo01@gmail.com"
PASSWORD = "9aa38107a400d3666e7e36a3f578e18d20388a06"
SPREADSHEET_ID = "1wOuXbwcU9q3Jxgl4s1y2_RImhoY1dy-GdNyAPsHRUnk"

# ⚠️ သင့် Google Sheet ရဲ့ Apps Script Web App URL ကို ပြန်ထည့်ပါ
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzwLwVZA4TEXEjvtWMvH_aTGPpo1DBoSqicsQF1utj2kZCNMfMUpLMQJ23zO_-yVCH3/exec"

def sync():
    print("🔄 Odoo ERP ထံမှ အင်္ဂလိပ်ဒေတာများ အမြန်နှုန်းဖြင့် ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        products = models.execute_kw(DB, uid, PASSWORD, "product.template", "read", [product_ids], {"fields": ["id", "name"]})

        raw_data_rows = []
        for p in products:
            p_id = str(p.get("id", ""))
            p_name_en = p.get("name", "")
            # UI မှာ အင်္ဂလိပ်လိုပဲ ပြမှာမို့လို့ မြန်မာကွက်လပ်ကို Blank ("") ထားလိုက်ပါတယ်
            raw_data_rows.append([p_id, p_name_en, "", "", ""])

        payload = {"is_first": True, "data": raw_data_rows}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
        print(f"✨ [SUCCESS] Sync Speed: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync()
