# 🔍 စမတ်ကျသော ရှာဖွေမှုစနစ် (မြန်မာ/အင်္ဂလိပ် နှစ်မျိုးလုံး ရှာနိုင်သည်)
    if search_query:
        query = search_query.lower()
        
        # ⚡ Myanmar_Name တိုင် တကယ် ရှိ/မရှိ ကြိုတင် စစ်ဆေးသည့် အမှားဒဏ်ခံစနစ်
        if 'Myanmar_Name' in df.columns:
            df = df[
                df['Name'].str.lower().str.contains(query, na=False) | 
                df['Myanmar_Name'].str.lower().str.contains(query, na=False)
            ]
        else:
            # တိုင်မရှိပါက Name တစ်ခုတည်းဖြင့်သာ ရှာဖွေမည်
            df = df[df['Name'].str.lower().str.contains(query, na=False)]
