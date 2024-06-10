import requests
import xml.etree.ElementTree as ET
import json

# Step 1: Choose an RSS feed URL
rss_feed_url = 'https://jobs.dou.ua/vacancies/feeds/?category=Golang'

# Step 2: Set up headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Fetch the RSS feed
response = requests.get(rss_feed_url, headers=headers)
response.raise_for_status()  # Check that the request was successful

# Step 3: Parse the RSS feed with namespaces
root = ET.fromstring(response.content)


# Function to clean text from symbols
def clean_text(text):
    return text.replace('\xa0', ' ').strip()


# Step 4: Extract relevant information
rss_items = []
for item in root.findall('./channel/item'):
    title = item.find('title').text
    link = item.find('link').text
    description = clean_text(item.find('description').text)
    pub_date = item.find('pubDate').text
    guid = item.find('guid').text

    rss_items.append({
        'title': title,
        'link': link,
        'description': description,
        'pub_date': pub_date,
        'guid': guid
    })

# Step 5: Convert the extracted data to JSON
rss_json = json.dumps(rss_items, indent=4, ensure_ascii=False)  # ensure_ascii=False to handle non-ASCII characters

# Step 6: Output the JSON data
print(rss_json)

# Optional: Save to a file
with open('rss_feed.json', 'w', encoding='utf-8') as json_file:
    json_file.write(rss_json)
