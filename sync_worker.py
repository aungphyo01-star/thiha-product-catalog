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

# ⚠️ သင့် Google Sheet ရဲ့ Web App URL ကို ဒီနေရာမှာ သေချာပြန်ထည့်ပေးပါဗျာ
WEB_APP_URL = "YOUR_GOOGLE_WEB_APP_URL_HERE"

def sync():
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        # ပစ္စည်း ID များ ရှာဖွေခြင်း
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 1000})
        
        # ⚡ OPTIMIZATION: ဝန်လုံးဝမပိစေရန် id နှင့် name နှစ်ခုတည်းကိုသာ ညှစ်ထုတ်ဆွဲယူသည်
        products = models.execute_kw(DB, uid, PASSWORD, "product.template", "read", [product_ids], {"fields": ["id", "name"]})
        
        sheet_read_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
        existing_mm_names = {}
        try:
            old_df = pd.read_csv(sheet_read_url)
            if "ID" in old_df.columns and "Myanmar_Name" in old_df.columns:
                existing_mm_names = dict(zip(old_df["ID"].astype(str), old_df["Myanmar_Name"].fillna("")))
        except:
            pass

        raw_data_rows = []
        for p in products:
            p_id = str(p.get("id", ""))
            p_name_en = p.get("name", "")
            p_name_mm = existing_mm_names.get(p_id, "")
            
            # ⚡ Apps Script Structure အတိုင်း Column နေရာလွတ်များ ညှိပေးခြင်း
            raw_data_rows.append([p_id, p_name_en, p_name_mm, "", ""])

        payload = {"is_first": True, "data": raw_data_rows}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(WEB_APP_URL, data=json.dumps(payload), headers=headers)
        print(f"Sync Status: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sync()
