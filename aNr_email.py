import imaplib
import email
import requests
import re


# Email Credentials (Use environment variables for security)
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASS = "your_app_password"

# Notion API Keys
NOTION_API_KEY = "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"
NOTION_DATABASE_ID = "246410551efb4b10a7b8450f51fe278c"
NOTION_URL = "https://api.notion.com/v1/pages"

def fetch_unread_emails():
    """Fetch unread emails from inbox"""
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")  # Select the inbox folder
    
    # Search for unread emails
    result, data = mail.search(None, "UNSEEN")
    email_ids = data[0].split()

    emails = []
    for e_id in email_ids:
        result, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            emails.append(part.get_payload(decode=True).decode("utf-8"))
                else:
                    emails.append(msg.get_payload(decode=True).decode("utf-8"))
    
    mail.logout()
    return emails

def extract_data(email_text):
    """Extract relevant information from email text"""
    artist_match = re.search(r'“([^”]+)”', email_text)
    artist_name = artist_match.group(1) if artist_match else "Not found"

    spotify_match = re.search(r'Monthly Spotify Listeners:\s*([\d.,K]+)', email_text)
    monthly_listeners = spotify_match.group(1) if spotify_match else "Not found"

    label_match = re.search(r'Label:\s*(.+)', email_text)
    label = label_match.group(1).strip() if label_match else "Not found"

    return artist_name, monthly_listeners, label

def submit_to_notion(email_text):
    """Submit extracted data to Notion"""
    artist_name, monthly_listeners, label = extract_data(email_text)

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Creator Name": {"title": [{"text": {"content": artist_name}}]},
            "Monthly Listens": {"rich_text": [{"text": {"content": monthly_listeners}}]},
            "Label": {"rich_text": [{"text": {"content": label}}]}
        }
    }

    response = requests.post(NOTION_URL, headers=headers, json=data)

def process_emails():
    """Fetch unread emails and process each"""
    emails = fetch_unread_emails()
    if not emails:
        return

    for email_text in emails:
        submit_to_notion(email_text)