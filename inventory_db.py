import pandas as pd

INITIAL_INVENTORY = pd.DataFrame([
    {"sku_id": "SKU_01", "name": "Cold Drinks (Pack of 4)", "base_price": 160.0, "current_stock": 45, "restock_lead_time_min": 60, "safety_stock": 10},
    {"sku_id": "SKU_02", "name": "Instant Noodles Box", "base_price": 120.0, "current_stock": 80, "restock_lead_time_min": 120, "safety_stock": 15},
    {"sku_id": "SKU_03", "name": "Rain Poncho / Umbrella", "base_price": 299.0, "current_stock": 20, "restock_lead_time_min": 90, "safety_stock": 5},
    {"sku_id": "SKU_04", "name": "Electrolyte Energy Drink", "base_price": 75.0, "current_stock": 35, "restock_lead_time_min": 45, "safety_stock": 8},
])
