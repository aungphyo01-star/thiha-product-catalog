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

# ⚠️ အရေးကြီးဆုံး: သင့် Google OAuth Access Token အသစ်စက်စက်ကို ဤနေရာတွင် အစားထိုးပေးပါ
DRIVE_ACCESS_TOKEN = "ya29.a0AT3oNZ-5aNq7ejXPP2QngSg4moRSMbQ5cB10B1ZGnvJcgc3FkrxwawqFXkjYeq9wrXntKUGoBKb2YPXaK-_9gFKnTx7kCHGWsQm8F5OBQHp-6517jT3QqD51oBqGnuOF9ASkvb4gNeyh7o5VigugEn2tr2aYcHNf8tTXZaQAc3oTYtGm_HkM4cXI6h9B7at9OC_thuIaCgYKAdcSARcSFQHGX2Miko3PuvFtNoU1NeWCTqIzgg0206"

def upload_to_drive_direct(p_id, base64_image):
    """ Google Drive API v3 သို့ ပုံအား Multipart Upload တိုက်ရိုက်တင်သည့်စနစ် """
    if not base64_image or str(base64_image).strip() == "":
        return "No Image"
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
        
        res = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart", 
            headers=headers, 
            files=files,
            timeout=15
        )
        return res.status_code
    except Exception as e:
        return f"Error: {str(e)}"

def sync():
    print("🔄 Odoo ERP ထံမှ စာသားများနှင့် ဓာတ်ပုံများကို စတင်ဆွဲယူနေပါသည်...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        product_ids = models.execute_kw(DB, uid, PASSWORD, "product.template", "search", [[("sale_ok", "=", True)]], {"limit": 2000})
        total_products = len(product_
