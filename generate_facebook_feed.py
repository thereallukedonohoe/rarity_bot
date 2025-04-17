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

# BrickLink official color ID to name mapping (from catalogColors.asp)
color_lookup = {
    0: "Black", 1: "Blue", 2: "Green", 3: "Dark Turquoise", 4: "Red", 5: "Dark Pink", 6: "Brown",
    7: "Tan", 8: "Yellow", 9: "White", 10: "Orange", 11: "Light Gray", 12: "Gray", 13: "Light Blue",
    14: "Lime", 15: "Pink", 17: "Light Yellow", 18
