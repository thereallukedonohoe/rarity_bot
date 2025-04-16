# Stud and Brick | Rarity Bot

This GitHub Action runs daily at 2am AWST (6pm UTC) to:
- Pull your BrickLink inventory
- Query the number of sellers per part
- Rank the rarest parts
- Update the top 20 as `featured` in your BrickLink store
- Save results to CSV and JSON files

## Setup

1. Create a **private GitHub repo**
2. Go to Settings → Secrets → Actions, and add:

   - `BL_CONSUMER_KEY`
   - `BL_CONSUMER_SECRET`
   - `BL_TOKEN_VALUE`
   - `BL_TOKEN_SECRET`

3. Upload the contents of this ZIP
4. Commit to `main` and GitHub will run this every night 🎉
