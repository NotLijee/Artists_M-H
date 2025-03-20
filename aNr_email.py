import imaplib
import time
import schedule
import email
import requests
import re


# Email Credentials (Use environment variables for security)


def fetch_unread_emails():
    """Fetch unread emails from the inbox"""
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")  
        
        # Search for unread emails
        result, data = mail.search(None, "UNSEEN")
        if result != "OK":
            print("❌ Failed to search for unread emails.")
            return []

        email_ids = data[0].split()
        if not email_ids:
            print("✅ No unread emails found.")
            return []

        emails = []
        for e_id in email_ids:
            result, msg_data = mail.fetch(e_id, "(RFC822)")
            if result != "OK":
                print(f"❌ Failed to fetch email with ID {e_id}.")
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    email_text = extract_email_text(msg)
                    if email_text:
                        emails.append(email_text)
                    else:
                        print(f"⚠️ Failed to extract text from email with ID {e_id}.")

            # Mark email as read after processing
            mail.store(e_id, '+FLAGS', '\\Seen')

        mail.logout()
        print(f"✅ Successfully fetched {len(emails)} unread emails.")
        return emails
    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        return []

def extract_email_text(msg):
    """Extract text content from an email"""
    try:
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Extract only text-based content (ignore attachments)
                if "attachment" not in content_disposition and content_type in ["text/plain", "text/html"]:
                    return part.get_payload(decode=True).decode("utf-8", errors="ignore")
        else:
            return msg.get_payload(decode=True).decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"❌ Error extracting email text: {e}")
    return ""

def get_listeners_category(listeners_str):
    """Categorize monthly listeners"""
    try:
        if 'K' in listeners_str:
            listeners_num = float(listeners_str.replace('K', '')) * 1000
        elif 'M' in listeners_str:
            listeners_num = float(listeners_str.replace('M', '')) * 1000000
        else:
            listeners_num = float(listeners_str)

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
    except Exception:
        return "Unknown"

def extract_data(email_text):
    """Extract relevant information from email text"""
    try:
        # Extract artist name
        artist_match = re.search(r'“([^”]+)”', email_text)
        artist_name = artist_match.group(1) if artist_match else "Not found"

        # Extract Monthly Spotify Listeners
        spotify_match = re.search(r'Monthly Spotify Listeners:\s*([\d.,K]+)', email_text)
        monthly_listeners = spotify_match.group(1) if spotify_match else "Unknown"

        # Extract Label
        label_match = re.search(r'Label:\s*(.+)', email_text)
        label = label_match.group(1).strip() if label_match else "Unknown"

        # Extract Genre
        genre_match = re.search(r'Genre:\s*(.+)', email_text)
        genres = [g.strip() for g in re.split(r'[,/]', genre_match.group(1))] if genre_match else []

        # Extract Manager
        manager_match = re.search(r'Manager:\s*(.+)', email_text)
        manager = manager_match.group(1).strip() if manager_match else "Not found"

        # Extract Location
        location_match = re.search(r'Location:\s*([^,]+)', email_text)
        location = location_match.group(1).strip() if location_match else "Not found"

        #Role
        role = ['Artist']

        return artist_name, monthly_listeners, label, genres, role, manager, location
    except Exception as e:
        print(f"❌ Error extracting data from email text: {e}")
        return "Not found", "Unknown", "Unknown", []

def submit_to_notion(email_text):
    """Submit extracted data to Notion"""
    artist_name, monthly_listeners, label, genres, role, manager, location = extract_data(email_text)
    listeners_category = get_listeners_category(monthly_listeners)

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Creator Name": {"title": [{"text": {"content": artist_name}}]},
            "Role": {"multi_select": [{"name": role_name} for role_name in role]},
            "Monthly Listens": {"select": {"name": listeners_category}},  # Fixed to match Notion's `select` type
            "Label": {"multi_select": [{"name": lbl.strip()} for lbl in label.split(",")]},  # Fixed to match `multi_select`
            "Genre": {"multi_select": [{"name": genre} for genre in genres]},  # Added genres as `multi_select`
            "Manager": {"rich_text": [{"text": {"content": manager}}]},
            "Location": {"multi_select": [{"name": location}]},
        }
    }

    try:
        response = requests.post(NOTION_URL, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Data for {artist_name} added to Notion!")
        else:
            print(f"❌ Failed to add {artist_name} to Notion. Error: {response.text}")
    except Exception as e:
        print(f"❌ Error submitting data to Notion: {e}")

def process_emails():
    """Fetch unread emails and process each"""
    emails = fetch_unread_emails()
    
    if not emails:
        print("No new unread emails.")
        return

    for email_text in emails:
        submit_to_notion(email_text)

# Run the email processing function
def job():
    print("Running email processing...")
    process_emails()

# Schedule the job every 10 minutes
schedule.every(10).seconds.do(job)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)