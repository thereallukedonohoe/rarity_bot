# ✅ Trigger commit refresh for GitHub Actions secret reload

import os
import requests
import time
import json
import csv
from requests_oauthlib import OAuth1

auth = OAuth1(
    os.environ['BL_CONSUMER_KEY'],
    os.environ['BL_CONSUMER_SECRET'],
    os.environ['BL_TOKEN_VALUE'],
    os.environ['BL_TOKEN_SECRET']
)

def get_inventory():
    print("🔐 Calling BrickLink API for inventory...")
    r = requests.get("https://api.bricklink.com/api/store/v1/inventories", auth=auth)
    print(f"🔁 Response Code: {r.status_code}")
    print(f"🧾 Response: {r.text}")
    return r.json().get("data", [])

def get_seller_count(item_type, item_no):
    url = f"https://api.bricklink.com/api/store/v1/items/{item_type}/{item_no}/price?guide_type=stock"
    r = requests.get(url, auth=auth)
    data = r.json().get("data", {})
    return data.get("total_lots", 9999)

def update_featured(lot_id, value=True):
    url = f"https://api.bricklink.com/api/store/v1/inventory/{lot_id}"
    r = requests.put(url, json={"is_featured": value}, auth=auth)
    return r.status_code == 200

print("🔄 Fetching inventory...")
inventory = get_inventory()

if not inventory:
    print("❌ Inventory not loaded. Check credentials or API error above.")
    exit(1)

rare_list = []
for item in inventory:
    part_no = item['item']['no']
    item_type = item['item']['type']
    lot_id = item['inventory_id']
    qty = item['quantity']
    try:
        sellers = get_seller_count(item_type, part_no)
    except:
        sellers = 9999
    rare_list.append({
        "part_no": part_no,
        "lot_id": lot_id,
        "color_id": item['color_id'],
        "condition": item['new_or_used'],
        "qty": qty,
        "sellers": sellers,
        "price": item['unit_price']
    })
    time.sleep(0.3)

sorted_parts = sorted(rare_list, key=lambda x: x['sellers'])
top_20 = sorted_parts[:20]

print("🌟 Updating featured items...")
updated = 0
for part in top_20:
    if update_featured(part['lot_id'], True):
        updated += 1
    time.sleep(0.2)

print(f"✅ {updated} items featured.")

with open("top_20_rarest.json", "w") as f:
    json.dump(top_20, f, indent=2)

with open("top_20_rarest.csv", "w", newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=top_20[0].keys())
    writer.writeheader()
    writer.writerows(top_20)

print("📁 Output written to top_20_rarest.json and top_20_rarest.csv")
