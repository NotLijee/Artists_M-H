import requests 
import sys
import re

#Notion Keys 


import re

# Sample email text
email_text = """
“marQ”

Monthly Spotify Listeners: 387K

Instagram Followers: 7.7K

TikTok Followers: 3.9K

Name: Hayden J. Marquardt

Location: New York City, NY

Age: N/A

Genre: R&B

Career Overview: Hayden Marquardt, known as marQ, started releasing music just over the last year, starting in 2023. Originally from Chicago, Illinois, marQ finds much inspiration from artists such as Steve Lacy and Dominic Fike. His first single “Whats Wrong?” was released in 2023, and since then he has released single after single until the release of his debut EP “Hayden’s Demos” He’s since continued to release hit after hit, with each of these singles since then surpassing over 1 million streams. His last EP “Rhodie” was released back in November of 2024, and he has just released his single “Yesterday” this month. He has consistently worked with producer Adam Bross.

Standout Songs: On & Off ; Farewell

Editorial Playlist: Fresh Finds ; Fresh Finds Indie

Assessment: Over the last month, marQ has seen a +29.26K increase in New Monthly Spotify Listeners. Along with his massive growth in Spotify Listeners, he has also amassed over 228K playlist counts in just the last month alone. With a growing following on both TikTok and Instagram, and multiple songs with over 1 million streams, marQ is surely securing his spot as an up and coming artist. 

% Growth:
1 MONTH: +29.26K +8.16%

3 MONTHS: +157.41K +68.77%

1 YEAR: +160.12K +70.79%

Contacts:

Management: Unsigned

Label: Unsigned

Relevant Links:

Website

Credits

Rhodie (Official Video)
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

