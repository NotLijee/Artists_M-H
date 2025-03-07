import requests 
import sys
import re

#Notion Keys 
NOTION_API_KEY = "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"
NOTION_DATABASE_ID = "246410551efb4b10a7b8450f51fe278c"
NOTION_URL = "https://api.notion.com/v1/pages"

import re

# Sample email text
email_text = """
“Thea Dora”

Monthly Spotify Listeners: 47.5K

Instagram Followers: 1.3K

TikTok Followers: 125

Name: Thea Borregard

Location: Copenhagen, DK

Age: 26

Genre: Dance, Electronic

Career Overview: Born and raised in Norrebro, Copenhagen, Thea Dora first came onto the scene with her debut single “Collected” in the beginning of last year. Working with songwriter and producer Ronni Vindahl, who has worked and produced songs for Kendrick Lamar, Avicci, and MO; and worked with mixing engineer Geoff Swann who has mixed for Chappell Roan, Billie Eilish, and Charli XCX. Since her debut single she has released her debut EP “Enter” followed by two more singles, with the latest being “New Beginnings” that she has released just this year. She is set to perform at the Spot Festival in Denmark on May 2-3.

Standout Songs: Collected, New Beginnings

Editorial Playlists: All New Pop, Fresh Finds, Fresh Finds Pop, New Pop Revolution, Ny Pop 

Assessment: Last month Thea Dora saw a +46.62K increase in New Monthly Spotify Listeners. Along with a significant and impressive +9104.26% spike in just the last year alone. Considering Thea Dora has only just started putting out music in just the last year, and is working with some of the most well known names in the industry, I believe that with upcoming performances/festivals and promotion of her newest singles she will continue to rise and emerge as a new artist.

% Growth:

1 MONTH: +46.62K +4810.84%

3 MONTHS: +47.07K +9104.26%

1 YEAR: +47.07K +9104.26%

Contacts:

Manager: Unsigned

Label: Unsigned

Relevant Links:

Website

Credits
"""
def multi_select_value(value):
    # If value is already a list, return a list of dicts; otherwise, wrap it in a list.
    if isinstance(value, list):
        return [{"name": v} for v in value]
    else:
        return [{"name": value}]


# Extract artist name (first quoted word)
artist_match = re.search(r'“([^”]+)”', email_text)
artist_name = artist_match.group(1) if artist_match else "Not found"

# Extract Monthly Spotify Listeners
spotify_match = re.search(r'Monthly Spotify Listeners:\s*([\d.,K]+)', email_text)
monthly_listeners = spotify_match.group(1) if spotify_match else "Not found"

# Extract Manager
manager_match = re.search(r'Manager:\s*(.+)', email_text)
manager = manager_match.group(1).strip() if manager_match else "Not found"

# Extract Label
label_match = re.search(r'Label:\s*(.+)', email_text)
label = label_match.group(1).strip() if label_match else "Not found"

#Extract Genre
genre_match = re.search(r'Genre:\s*(.+)', email_text)
genres = [g.strip() for g in genre_match.group(1).split(',')] if genre_match else []

#Exctract Location 
location_match = re.search(r'Location:\s*([^,]+)', email_text)
location = location_match.group(1).strip() if location_match else "Not found"

role = ['Artist']

def get_listeners_category(listeners_str):
    # Remove the "K" or "M" from the listeners string and convert to number
    if 'K' in listeners_str:
        listeners_num = float(listeners_str.replace('K', '')) * 1000  # e.g., 47.5K -> 47500
    elif 'M' in listeners_str:
        listeners_num = float(listeners_str.replace('M', '')) * 1000000  # e.g., 5M -> 5000000
    else:
        listeners_num = float(listeners_str)
    
    # Categorize based on the number of listeners
    if listeners_num < 1000:
        return "<1k"
    elif 1000 <= listeners_num < 5000:
        return "1k - 5k"
    elif 5000 <= listeners_num < 10000:
        return "5k-10k"
    elif 10000 <= listeners_num < 50000:
        return "10k-50k"
    elif 50000 <= listeners_num < 100000:
        return "50k-100k"
    elif 100000 <= listeners_num < 500000:
        return "100k-500k"
    elif 500000 <= listeners_num < 1000000:
        return "500k-1mil"
    elif 1000000 <= listeners_num < 5000000:
        return "1mil-5mil"
    elif 5000000 <= listeners_num < 10000000:
        return "5mil-10mil"
    elif 10000000 <= listeners_num < 20000000:
        return "10mil-20mil"
    elif 20000000 <= listeners_num < 30000000:
        return "20mil-30mil"
    else:
        return ">30mil"

# Get the category based on the monthly listeners value
listeners_category = get_listeners_category(monthly_listeners)


headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
def multi_select_value(value):
    # If value is already a list, return a list of dicts; otherwise, wrap it in a list.
    if isinstance(value, list):
        return [{"name": v} for v in value]
    else:
        return [{"name": value}]


#Prepare Notion request body
data = {
    "parent": {"database_id": NOTION_DATABASE_ID},
    "properties": {
        "Creator Name": {"title": [{"text": {"content": artist_name}}]},
        "Role": {"multi_select": [{"name": role_name} for role_name in role]},
        "Genre": {"multi_select": [{"name": genre} for genre in genres]},
        "Monthly Listens": {"select": {"name": listeners_category}},
        "Label": {"multi_select": multi_select_value(label)},
        "Manager": {"rich_text": [{"text": {"content": manager}}]},
        "Location": {"multi_select": multi_select_value(location)},
    }
}


response = requests.post(NOTION_URL, headers=headers, json=data)

# Print response
if response.status_code == 200:
    print("✅ Data added successfully!")
else:
    print("❌ Failed to add data:", response.text)


# Print extracted data
# print(f"Artist: {artist_name}")
# print(f"Monthly Spotify Listeners: {monthly_listeners}")
# print(f"Manager: {manager}")
# print(f"Label: {label}")
# print(f"Genres: {genres}")
# print(f"Location: {location}")

