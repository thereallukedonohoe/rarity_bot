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
    await page.wait_for_selector("img[src^='https://img.bricklink.com']", timeout=10000)
    await page.wait_for_selector(".itemBoxMain", timeout=10000)

    # Get image
    image_element = await page.query_selector("img[src^='https://img.bricklink.com']")
    image_url = await image_element.get_attribute("src")

    # Get title (e.g. "Light Bluish Gray Flag 2 x 2 Square")
    title_element = await page.query_selector(".itemBoxMain b")
    title_text = await title_element.inner_text()

    await browser.close()
    return {
        "image_link": image_url.strip(),
        "title": title_text.strip(),
        "color": title_text.split()[0]  # crude extract — better logic can be added later
    }

async def run():
    with open(INPUT_FILE, newline='') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    updated_rows = []
    async with async_playwright() as playwright:
        for row in rows[:5]:  # LIMIT TO 5
            inventory_id = row["id"]
            print(f"🔍 Scraping data for Lot ID {inventory_id}...")
            try:
                result = await scrape_storefront_data(playwright, inventory_id)
                row["image_link"] = result["image_link"]
                row["title"] = result["title"]
                row["color"] = result["color"]
            except Exception as e:
                print(f"⚠️ Failed for Lot ID {inventory_id}: {e}")
            updated_rows.append(row)

    # Write output
    with open(OUTPUT_FILE, "w", newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=updated_rows[0].keys())
        writer.writeheader()
        writer.writerows(updated_rows)

asyncio.run(run())
