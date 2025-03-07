import requests
from supabase import create_client, Client

# API Key and Database ID
NOTION_API_KEY = "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"
NOTION_DATABASE_ID = "246410551efb4b10a7b8450f51fe278c"

#Supabase connection key 
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh6bW15ZHd6ZHh1aHdvcnZuanloIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MTI5MDgzNSwiZXhwIjoyMDU2ODY2ODM1fQ.p6bqB3No6vJ8d7tL5NI2eIy3Is1NujOxifo5tPRtkdg"
SUPABASE_URL = "https://xzmmydwzdxuhworvnjyh.supabase.co"

supabase: Client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)



# API Endpoint
url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"

# Headers
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
def update_all_roles():
    has_more = True
    next_cursor = None
    idx = 1

    while has_more:
        payload = {"start_cursor": next_cursor} if next_cursor else {}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            results = response.json()
            for result in results['results']:
                properties = result['properties']
                name_property = properties.get('Name', {}).get('title', [])
                role_property = properties.get('Role', {}).get('multi_select', [])
                if name_property:
                    name = name_property[0]['text']['content']
                    roles = ", ".join([role['name'] for role in role_property]) if role_property else "Unknown"
                    print(f"{idx}. Name: {name}, Roles: {roles}")
                    idx += 1

                    # Check for duplicates in Supabase
                    existing_entry = supabase.table("master_notion").select("artist_name").eq("artist_name", name).execute()
                    if not existing_entry.data:
                        # Insert into Supabase
                        response = supabase.table("master_notion").insert({"artist_name": name, "role": roles}).execute()
                        print(response)
                    else:
                        # Update roles in Supabase
                        response = supabase.table("master_notion").update({"role": roles}).eq("artist_name", name).execute()
                        print(response)
                else:
                    print(f"{idx}. Name: (No name found)")
                    idx += 1
            has_more = results.get('has_more', False)
            next_cursor = results.get('next_cursor', None)
        else:
            print(f"Failed to query Notion database. Status code: {response.status_code}, Response: {response.text}")
            break

# Run the function to print all roles for each artist in Notion and insert/update them in Supabase
# update_all_roles()

def update_all_genres():
    has_more = True
    next_cursor = None
    idx = 1

    while has_more:
        payload = {"start_cursor": next_cursor} if next_cursor else {}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            results = response.json()
            for result in results['results']:
                properties = result['properties']
                name_property = properties.get('Name', {}).get('title', [])
                genre_property = properties.get('Genre', {}).get('multi_select', [])
                if name_property:
                    name = name_property[0]['text']['content']
                    genres = ", ".join([genre['name'] for genre in genre_property]) if genre_property else "Unknown"
                    print(f"{idx}. Name: {name}, Genres: {genres}")
                    idx += 1

                    # Check for duplicates in Supabase
                    existing_entry = supabase.table("master_notion").select("artist_name").eq("artist_name", name).execute()
                    if not existing_entry.data:
                        # Insert into Supabase
                        response = supabase.table("master_notion").insert({"artist_name": name, "genre": genres}).execute()
                        print(response)
                    else:
                        # Update roles in Supabase
                        response = supabase.table("master_notion").update({"genre": genres}).eq("artist_name", name).execute()
                        print(response)
                else:
                    print(f"{idx}. Name: (No name found)")
                    idx += 1
            has_more = results.get('has_more', False)
            next_cursor = results.get('next_cursor', None)
        else:
            print(f"Failed to query Notion database. Status code: {response.status_code}, Response: {response.text}")
            break
# update_all_genres()

def update_all_locations():
    has_more = True
    next_cursor = None
    idx = 1

    while has_more:
        payload = {"start_cursor": next_cursor} if next_cursor else {}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            results = response.json()
            for result in results['results']:
                properties = result['properties']
                name_property = properties.get('Name', {}).get('title', [])
                loc_property = properties.get('Location', {}).get('multi_select', [])
                if name_property:
                    name = name_property[0]['text']['content']
                    locs = ", ".join([loc['name'] for loc in loc_property]) if loc_property else " "
                    print(f"{idx}. Name: {name}, Location(s): {locs}")
                    idx += 1

                    # Check for duplicates in Supabase
                    existing_entry = supabase.table("master_notion").select("artist_name").eq("artist_name", name).execute()
                    if not existing_entry.data:
                        # Insert into Supabase
                        response = supabase.table("master_notion").insert({"artist_name": name, "location": locs}).execute()
                        print(response)
                    else:
                        # Update roles in Supabase
                        response = supabase.table("master_notion").update({"location": locs}).eq("artist_name", name).execute()
                        print(response)
                else:
                    print(f"{idx}. Name: (No name found)")
                    idx += 1
            has_more = results.get('has_more', False)
            next_cursor = results.get('next_cursor', None)
        else:
            print(f"Failed to query Notion database. Status code: {response.status_code}, Response: {response.text}")
            break
update_all_locations()