import asyncio
import json
import csv
from playwright.async_api import async_playwright

USERNAME = "luke.donohoe"
INPUT_FILE = "meta_product_feed.csv"
OUTPUT_FILE = "meta_product_feed_with_images.csv"

async def scrape_storefront_data(playwright, inventory_id):
    browser = await playwright.chromium.launch()
    page = await browser.new_page()

    url = f"https://store.bricklink.com/{USERNAME}#/shop?o={json.dumps({'q': str(inventory_id)})}"
    await page.goto(url)
    await page.wait_for_selector(".itemBoxMain", timeout=15000)

    boxes = await page.query_selector_all(".itemBoxMain")

    for box in boxes:
        onclick_attr = await box.get_attribute("onclick")
        if not onclick_attr:
            continue
        if str(inventory_id) in onclick_attr:
            # Title
            title_element = await box.query_selector("b")
            title = await title_element.inner_text() if title_element else "UNKNOWN"

            # Image
            image_element = await box.query_selector("img")
            image_url = await image_element.get_attribute("src") if image_element else ""

            # Colour = first word of title (rough cut)
            color = title.split()[0] if title else "UNKNOWN"

            await browser.close()
            return {
                "image_link": image_url.strip(),
                "title": title.strip(),
                "color": color.strip()
            }

    await browser.close()
    raise Exception(f"No matching listing found for inventory ID {inventory_id}")

async def run():
    with open(INPUT_FILE, newline='') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    updated_rows = []
    async with async_playwright() as playwright:
        for row in rows[:5]:  # LIMIT TO 5 for testing
            inventory_id = row["id"]
            print(f"🔍 Scraping Lot ID {inventory_id}...")
            try:
                result = await scrape_storefront_data(playwright, inventory_id)
                row["image_link"] = result["image_link"]
                row["title"] = result["title"]
                row["color"] = result["color"]
            except Exception as e:
                print(f"⚠️ Failed for {inventory_id}: {e}")
            updated_rows.append(row)

    with open(OUTPUT_FILE, "w", newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=updated_rows[0].keys())
        writer.writeheader()
        writer.writerows(updated_rows)

asyncio.run(run())
