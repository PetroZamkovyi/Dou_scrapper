import requests
import xml.etree.ElementTree as ET
import json
from typing import List, Dict

# Constants
RSS_FEED_URL = 'https://jobs.dou.ua/vacancies/feeds/?category=Golang'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def fetch_rss_feed(url: str, headers: Dict[str, str]) -> ET.Element:
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return ET.fromstring(response.content)
    except requests.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        raise


def clean_text(text: str) -> str:
    return text.replace('\xa0', ' ').strip()


def extract_rss_items(root: ET.Element) -> List[Dict[str, str]]:
    rss_items = []
    for item in root.findall('./channel/item'):
        rss_items.append({
            'title': item.find('title').text,
            'link': item.find('link').text,
            'description': clean_text(item.find('description').text),
            'pub_date': item.find('pubDate').text,
            'guid': item.find('guid').text
        })
    return rss_items


def main():
    try:
        root = fetch_rss_feed(RSS_FEED_URL, HEADERS)
        rss_items = extract_rss_items(root)
        rss_json = json.dumps(rss_items, indent=4, ensure_ascii=False)
        print(rss_json)
        with open('rss_feed.json', 'w', encoding='utf-8') as json_file:
            json_file.write(rss_json)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
