import asyncio
from playwright.async_api import async_playwright
import csv

USERNAME = "luke.donohoe"  # Your BrickLink store username
INPUT_FILE = "meta_product_feed.csv"
OUTPUT_FILE = "meta_product_feed_with_images.csv"

async def get_image_url(playwright, inventory_id):
    browser = await playwright.chromium.launch()
    page = await browser.new_page()
    url = f"https://store.bricklink.com/{USERNAME}#/shop?o={{\"q\":\"{inventory_id}\",\"sort\":0,\"pgSize\":100,\"showHomeItems\":0}}"
    await page.goto(url)
    await page.wait_for_selector("img[src^='https://img.bricklink.com']", timeout=10000)
    image_element = await page.query_selector("img[src^='https://img.bricklink.com']")
    src = await image_element.get_attribute("src")
    await browser.close()
    return src

async def run():
    with open(INPUT_FILE, newline='') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    updated_rows = []
    async with async_playwright() as playwright:
        for row in rows[:5]:  # LIMIT TO 5 items for testing
            inventory_id = row["id"]
            print(f"🔍 Scraping image for lot {inventory_id}...")
            try:
                image_url = await get_image_url(playwright, inventory_id)
                row["image_link"] = image_url
            except Exception as e:
                print(f"⚠️ Failed for lot {inventory_id}: {e}")
                row["image_link"] = row.get("image_link", "")
            updated_rows.append(row)

    # Write updated rows
    with open(OUTPUT_FILE, "w", newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=updated_rows[0].keys())
        writer.writeheader()
        writer.writerows(updated_rows)

asyncio.run(run())
