name: Generate Facebook Product Feed (Test - 5 Pages)

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout main branch
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # full history for branch switching

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: pip install requests requests_oauthlib

      - name: Generate feed
        env:
          BL_CONSUMER_KEY: ${{ secrets.BL_CONSUMER_KEY }}
          BL_CONSUMER_SECRET: ${{ secrets.BL_CONSUMER_SECRET }}
          BL_TOKEN_VALUE: ${{ secrets.BL_TOKEN_VALUE }}
          BL_TOKEN_SECRET: ${{ secrets.BL_TOKEN_SECRET }}
        run: |
          python generate_facebook_feed.py

      - name: Push to gh-pages
        run: |
          git config --global user.email "github-actions@github.com"
          git config --global user.name "github-actions"
          git fetch origin gh-pages
          git checkout gh-pages || git checkout --orphan gh-pages
          mv meta_product_feed.csv index.html . || true
          git add meta_product_feed.csv index.html
          git commit -m "Update Facebook product feed (5-page test)" || echo "No changes"
          git push origin gh-pages
