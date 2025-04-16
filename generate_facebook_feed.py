import os
import csv
import requests
from requests_oauthlib import OAuth1

# BrickLink API authentication
auth = OAuth1(
    os.environ['BL_CONSUMER_KEY'],
    os.environ['BL_CONSUMER_SECRET'],
    os.environ['BL_TOKEN_VALUE'],
    os.environ['BL_TOKEN_SECRET']
)

# Confirm identity
def confirm_identity():
    print("🔐 Checking authenticated user...")
    r = requests.get("https://api.bricklink.com/api/store/v1/users/token", auth=auth)
    try:
        user = r.json().get('data', {}).get('username', 'unknown')
        print(f"👤 Authenticated as: {user}")
    except Exception as e:
        print(f"❌ Failed to confirm identity: {e}")

confirm_identity()

# Fetch up to 5 pages of inventory
def get_inventory():
    print("🔍 Fetching inventory (max 5 pages)...")
    all_items = []
    for page in range(1, 6):
        url = f"https://api.bricklink.com/api/store/v1/inventories?page={page}"
        r = requests.get(url, auth=auth)
        print(f"🔁 Page {page} - Status Code: {r.status_code}")
        try:
            data = r.json()
            page_items = data.get("data", [])
            if not page_items:
                break
            all_items.extend(page_items)
        except Exception as e:
            print(f"❌ Failed to parse page {page}: {e}")
            break
    print(f"📦 Retrieved {len(all_items)} inventory items (test mode).")
    return all_items

inventory = get_inventory()

if not inventory:
    print("⚠️ No inventory returned — check API account or inventory state.")
    exit(1)

# Write product feed
with open("meta_product_feed.csv", "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        "id", "title", "description", "availability",
        "price", "link", "image_link"
    ])
    writer.writeheader()
    seen_ids = set()
    for item in inventory:
        part_no = item["item"]["no"]
        color_id = item["color_id"]
        qty = item["quantity"]
        price = item["unit_price"]
        inv_id = f"{item['inventory_id']}_{color_id}"  # Ensure uniqueness
        condition = item["new_or_used"]

        # Ensure price is valid
        try:
            price_float = float(price)
            price_str = f"{price_float:.2f} AUD"
        except (TypeError, ValueError):
            continue  # Skip items with invalid prices

        if inv_id in seen_ids:
            continue
        seen_ids.add(inv_id)

        title = f"{part_no} ({condition})"
        description = f"{condition} LEGO part in colour {color_id} – Qty: {qty}"
        url = f"https://store.bricklink.com/luke.donohoe#/shop"
        image = f"https://www.bricklink.com/PL/{part_no}.jpg"

        writer.writerow({
            "id": inv_id,
            "title": title,
            "description": description,
            "availability": "in stock",
            "price": price_str,
            "link": url,
            "image_link": image
        })

# Create GitHub Pages redirect
with open("index.html", "w") as index:
    index.write("<!DOCTYPE html><html><head><meta http-equiv='refresh' content='0; url=meta_product_feed.csv'></head><body></body></html>")
