name: Generate Facebook Product Feed

on:
  schedule:
    - cron: "0 18 * * *"  # Runs at 2am AWST (UTC+8)
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          pip install requests requests-oauthlib

      - name: Generate BrickLink product feed
        run: python generate_facebook_feed.py

      - name: Install Playwright and browser
        run: |
          pip install playwright
          playwright install

      - name: Scrape image links for first 5 inventory items
        run: python fetch_storefront_images.py

      - name: Replace original feed with updated image links
        run: mv meta_product_feed_with_images.csv meta_product_feed.csv

      - name: Commit and push feed
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add meta_product_feed.csv index.html
          git commit -m "🧱 Update Facebook product feed"
          git push

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./
          publish_branch: gh-pages
