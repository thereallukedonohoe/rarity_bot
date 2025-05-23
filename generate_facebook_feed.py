import os
import csv
import requests
from requests_oauthlib import OAuth1
from html import unescape

# BrickLink API authentication
auth = OAuth1(
    os.environ['BL_CONSUMER_KEY'],
    os.environ['BL_CONSUMER_SECRET'],
    os.environ['BL_TOKEN_VALUE'],
    os.environ['BL_TOKEN_SECRET']
)

type_labels = {
    "P": "Part",
    "M": "Minifig",
    "S": "Set"
}

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
    for page in range(1, 2):  # Limit to 1 page for test
        url = f"https://api.bricklink.com/api/store/v1/inventories?page={page}"
        r = requests.get(url, auth=auth)
        if r.status_code != 200:
            break
        page_items = r.json().get("data", [])
        if not page_items:
            break
        all_items.extend(page_items)
        print(f"🔁 Page {page} fetched.")
    print(f"📦 Retrieved {len(all_items)} inventory items.")
    return all_items

inventory = get_inventory()

with open("meta_product_feed.csv", "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        "id", "title", "description", "availability", "condition",
        "price", "link", "image_link", "brand", "google_product_category",
        "fb_product_category", "color", "quantity_to_sell_on_facebook"
    ])
    writer.writeheader()

    for item in inventory:
        part = item.get("item", {})
        part_no = part.get("no", "N/A")
        part_type = part.get("type", "P")
        raw_name = part.get("name", "")
        name = unescape(raw_name)
        description = f"{type_labels.get(part_type, part_type)} - {part_no}"
        quantity = item.get("quantity", 0)

        try:
            price_float = float(item["unit_price"])
            price_str = f"{price_float:.2f} AUD"
        except (TypeError, ValueError):
            price_str = ""

        condition = "New" if item["new_or_used"] == "N" else "Used (like new)"

        writer.writerow({
            "id": item["inventory_id"],
            "title": "PLACEHOLDER",  # Replaced via scraping
            "description": description,
            "availability": "In Stock",
            "condition": condition,
            "price": price_str,
            "link": f"https://store.bricklink.com/luke.donohoe#/shop?o={{\"q\":\"{item['inventory_id']}\",\"sort\":0,\"pgSize\":100,\"showHomeItems\":0}}",
            "image_link": "https://via.placeholder.com/150",  # Replaced via scraping
            "brand": "Lego",
            "google_product_category": "3287",
            "fb_product_category": "47",
            "color": "PLACEHOLDER",  # Replaced via scraping
            "quantity_to_sell_on_facebook": quantity
        })

with open("index.html", "w") as f:
    f.write("<!DOCTYPE html><html><head><meta http-equiv='refresh' content='0; url=meta_product_feed.csv'></head><body></body></html>")
