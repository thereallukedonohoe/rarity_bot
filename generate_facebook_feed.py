# Final version with pagination and identity confirmation

import os
import csv
import requests
from requests_oauthlib import OAuth1

# Set up authentication
auth = OAuth1(
    os.environ['BL_CONSUMER_KEY'],
    os.environ['BL_CONSUMER_SECRET'],
    os.environ['BL_TOKEN_VALUE'],
    os.environ['BL_TOKEN_SECRET']
)

# Confirm store identity
def confirm_identity():
    print("🔐 Checking authenticated user...")
    r = requests.get("https://api.bricklink.com/api/store/v1/users/token", auth=auth)
    try:
        user = r.json().get('data', {}).get('username', 'unknown')
        print(f"👤 Authenticated as: {user}")
    except Exception as e:
        print(f"❌ Failed to confirm identity: {e}")

confirm_identity()

# Fetch inventory using pagination
def get_inventory():
    print("🔍 Fetching inventory from BrickLink using pagination...")
    all_items = []
    page = 1
    while True:
        url = f"https://api.bricklink.com/api/store/v1/inventories?page={page}"
        r = requests.get(url, auth=auth)
        print(f"🔁 Page {page} - Status Code: {r.status_code}")
        try:
            data = r.json()
            page_items = data.get("data", [])
            if not page_items:
                break
            all_items.extend(page_items)
            page += 1
        except Exception as e:
            print(f"❌ Failed to parse page {page}: {e}")
            break
    return all_items

inventory = get_inventory()

if not inventory:
    print("⚠️ No inventory returned — check API account or inventory state.")
    exit(1)

# Write CSV for Facebook feed
with open("meta_product_feed.csv", "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        "id", "title", "description", "availability",
        "price", "link", "image_link"
    ])
    writer.writeheader()
    for item in inventory:
        part_no = item["item"]["no"]
        color_id = item["color_id"]
        qty = item["quantity"]
        price = item["unit_price"]
        inv_id = item["inventory_id"]
        condition = item["new_or_used"]
        title = f"{part_no} ({condition})"
        description = f"{condition} LEGO part in colour {color_id} – Qty: {qty}"
        url = f"https://store.bricklink.com/luke.donohoe#/shop"
        image = f"https://www.bricklink.com/PL/{part_no}.jpg"
        writer.writerow({
            "id": inv_id,
            "title": title,
            "description": description,
            "availability": "in stock",
            "price": price,
            "link": url,
            "image_link": image
        })

# Create GitHub Pages index file
with open("index.html", "w") as index:
    index.write("<!DOCTYPE html><html><head><meta http-equiv='refresh' content='0; url=meta_product_feed.csv'></head><body></body></html>")
