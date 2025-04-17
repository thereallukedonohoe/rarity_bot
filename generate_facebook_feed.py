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

# Official BrickLink color ID to name mapping
color_lookup = {
    0: "White", 1: "Tan", 2: "Yellow", 3: "Blue", 4: "Red", 5: "Dark Pink", 6: "Black",
    7: "Blue", 8: "Brown", 9: "Light Gray", 10: "Gray", 11: "Dark Gray", 12: "Light Blue",
    13: "Lime", 14: "Pink", 15: "Dark Yellow", 16: "Tan", 17: "Light Green", 18: "Green",
    19: "Dark Green", 20: "Dark Turquoise", 21: "Light Turquoise", 22: "Sand Blue",
    23: "Sand Green", 24: "Sand Red", 25: "Dark Blue", 26: "Light Lime", 27: "Dark Orange",
    28: "Very Light Blue", 29: "Bright Light Orange", 30: "Bright Light Blue", 31: "Light Blue-Violet",
    32: "Medium Blue", 33: "Medium Green", 34: "Earth Orange", 35: "Medium Orange",
    36: "Dark Red", 37: "Dark Pink", 38: "Light Pink", 39: "Light Yellow", 40: "Light Purple",
    41: "Dark Purple", 42: "Chrome Gold", 43: "Chrome Silver", 44: "Chrome Black",
    45: "Pearl Light Gray", 46: "Pearl Dark Gray", 47: "Pearl Very Light Gray", 48: "Pearl White",
    49: "Pearl Blue", 50: "Pearl Green", 51: "Pearl Red", 52: "Pearl Gold", 53: "Pearl Copper",
    54: "Trans-Clear", 55: "Trans-Black", 56: "Trans-Red", 57: "Trans-Green", 58: "Trans-Blue",
    59: "Trans-Yellow", 60: "Trans-Neon Orange", 61: "Trans-Neon Green", 62: "Trans-Light Blue",
    63: "Trans-Purple", 64: "Trans-Pink", 65: "Metallic Gold", 66: "Metallic Silver",
    67: "Glow in Dark White", 68: "Glow in Dark Opaque", 69: "Glow in Dark Trans",
    70: "Milky White", 71: "Chrome Blue", 72: "Chrome Green", 73: "Chrome Pink",
    74: "Chrome Red", 75: "Chrome Orange", 76: "Speckle Black-Silver", 77: "Speckle Black-Gold",
    78: "Speckle Black-Copper", 79: "Rubber Black", 80: "Rubber White", 81: "Rubber Blue",
    82: "Rubber Red", 83: "Rubber Yellow", 84: "Rubber Trans-Clear", 85: "Rubber Dark Gray",
    86: "Rubber Light Gray", 87: "Rubber Green", 88: "Rubber Orange", 89: "Rubber Lime",
    90: "Rubber Brown", 91: "Rubber Tan", 92: "Rubber Pink", 93: "Rubber Purple"
}

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
    for page in range(1, 2):  # Limit to 1 page for testing
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
        color_id = item["color_id"]
        color = color_lookup.get(color_id, f"Color ID {color_id}")
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
            "title": f"{color} {name}",
            "description": description,
            "availability": "In Stock",
            "condition": condition,
            "price": price_str,
            "link": f"https://store.bricklink.com/luke.donohoe#/shop?o={{\"q\":\"{item['inventory_id']}\",\"sort\":0,\"pgSize\":100,\"showHomeItems\":0}}",
            "image_link": f"https://www.bricklink.com/PL/{part_no}.jpg",  # Placeholder, replaced by scraper
            "brand": "Lego",
            "google_product_category": "3287",
            "fb_product_category": "47",
            "color": color,
            "quantity_to_sell_on_facebook": quantity
        })

with open("index.html", "w") as f:
    f.write("<!DOCTYPE html><html><head><meta http-equiv='refresh' content='0; url=meta_product_feed.csv'></head><body></body></html>")
