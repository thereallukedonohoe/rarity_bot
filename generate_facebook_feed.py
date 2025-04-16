import os
import csv
import requests
from requests_oauthlib import OAuth1

auth = OAuth1(
    os.environ['BL_CONSUMER_KEY'],
    os.environ['BL_CONSUMER_SECRET'],
    os.environ['BL_TOKEN_VALUE'],
    os.environ['BL_TOKEN_SECRET']
)

color_names = {0: 'Black', 1: 'Blue', 2: 'Green', 3: 'Dark Turquoise', 4: 'Red', 5: 'Dark Pink', 6: 'Brown', 7: 'Tan', 8: 'Yellow', 9: 'White', 10: 'Orange', 11: 'Light Gray', 12: 'Gray', 13: 'Light Blue', 14: 'Lime', 15: 'Pink', 16: 'Dark Yellow', 17: 'Tan', 18: 'Purple', 19: 'Blue-Violet', 20: 'Dark Blue', 21: 'Light Green', 22: 'Dark Green', 23: 'Magenta', 24: 'Light Purple', 25: 'Light Yellow', 26: 'Turquoise', 27: 'Light Lime', 28: 'Violet', 29: 'Bright Pink', 30: 'Very Light Gray', 34: 'Chrome Gold', 36: 'Chrome Silver', 38: 'Chrome Black', 39: 'Dark Orange', 42: 'Medium Blue', 68: 'Dark Tan', 69: 'Reddish Brown', 71: 'Maersk Blue', 72: 'Light Aqua', 73: 'Dark Red', 74: 'Metallic Silver', 77: 'Dark Bluish Gray', 78: 'Light Bluish Gray', 85: 'Dark Brown', 86: 'Dark Tan', 87: 'Dark Azure', 88: 'Medium Azure', 89: 'Light Aqua', 90: 'Lavender', 91: 'Dark Lavender', 110: 'Bright Light Orange', 115: 'Pearl Gold', 120: 'Flat Silver'}

def confirm_identity():
    r = requests.get("https://api.bricklink.com/api/store/v1/users/token", auth=auth)
    try:
        user = r.json().get('data', {}).get('username', 'unknown')
        print(f"👤 Authenticated as: {user}")
    except Exception as e:
        print(f"❌ Identity error: {e}")

confirm_identity()

def get_inventory():
    all_items = []
    page = 1
    url = f"https://api.bricklink.com/api/store/v1/inventories?page={page}"
    r = requests.get(url, auth=auth)
    data = r.json()
    all_items.extend(data.get("data", []))
    return all_items

inventory = get_inventory()

with open("meta_product_feed.csv", "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        "id", "title", "description", "availability", "condition",
        "price", "link", "image_link", "brand", "google_product_category",
        "fb_product_category", "color"
    ])
    writer.writeheader()

    for item in inventory:
        part = item.get("item", {})
        part_no = part.get("no", "N/A")
        name = part.get("name", "LEGO Part")
        inv_id = f"{item['inventory_id']}_{item['color_id']}"
        color = color_names.get(item["color_id"], f"Color ID {item['color_id']}")

        try:
            price_float = float(item["unit_price"])
            price_str = f"{price_float:.2f} AUD"
        except (TypeError, ValueError):
            continue

        writer.writerow({
            "id": inv_id,
            "title": part_no,
            "description": name,
            "availability": "In Stock",
            "condition": "new" if item["new_or_used"] == "N" else "used",
            "price": price_str,
            "link": f"https://store.bricklink.com/luke.donohoe#/shop",
            "image_link": f"https://www.bricklink.com/PL/{part_no}.jpg",
            "brand": "Lego",
            "google_product_category": "3287",
            "fb_product_category": "47",
            "color": color
        })

with open("index.html", "w") as f:
    f.write("<!DOCTYPE html><html><head><meta http-equiv='refresh' content='0; url=meta_product_feed.csv'></head><body></body></html>")
