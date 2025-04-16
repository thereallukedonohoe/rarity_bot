# forced refresh after full secret reset

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

# Confirm account identity
def confirm_identity():
    print("🔐 Checking authenticated user...")
    r = requests.get("https://api.bricklink.com/api/store/v1/users/token", auth=auth)
    try:
        user = r.json().get('data', {}).get('username', 'unknown')
        print(f"👤 Authenticated as: {user}")
    except Exception as e:
        print(f"❌ Failed to confirm identity: {e}")

confirm_identity()

# Get inventory from BrickLink
def get_inventory():
    print("🔍 Fetching inventory from BrickLink...")
    r = requests.get("https://api.bricklink.com/api/store/v1/inventories", auth=auth)
    print(f"🔁 Status Code: {r.status_code}")
    try:
        print("🧾 Response:", r.json())
    except Exception as e:
        print(f"❌ Error parsing JSON: {e}")
        return []
    return r.json().get("data", [])

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
