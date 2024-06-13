import requests
import xml.etree.ElementTree as ET
import json
from typing import List, Dict
import os
from datetime import datetime

# Constants
CATEGORIES = ['Golang']
EXPERIENCE_LEVELS = ['0-1', '1-3', '3-5', '5plus']
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
OUTPUT_DIR = 'extracted_data'
CUMULATIVE_FILE = os.path.join(OUTPUT_DIR, 'cumulative_rss_feed.json')


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


def extract_rss_items(root: ET.Element, experience: str, category: str) -> List[Dict[str, str]]:
    rss_items = []
    for item in root.findall('./channel/item'):
        rss_items.append({
            'category': category,
            'title': item.find('title').text,
            'link': item.find('link').text,
            'experience': experience,
            'description': clean_text(item.find('description').text),
            'pub_date': item.find('pubDate').text,
            'guid': item.find('guid').text
        })
    return rss_items


def save_to_json(data: List[Dict[str, str]], filename: str):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)


def update_cumulative_file(new_data: List[Dict[str, str]], cumulative_file: str):
    if os.path.exists(cumulative_file):
        with open(cumulative_file, 'r', encoding='utf-8') as file:
            cumulative_data = json.load(file)
    else:
        cumulative_data = []

    cumulative_data.extend(new_data)
    save_to_json(cumulative_data, cumulative_file)


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    all_rss_items = []
    for category in CATEGORIES:
        for experience in EXPERIENCE_LEVELS:
            url = f'https://jobs.dou.ua/vacancies/feeds/?exp={experience}&category={category}'
            try:
                root = fetch_rss_feed(url, HEADERS)
                rss_items = extract_rss_items(root, experience, category)
                all_rss_items.extend(rss_items)
            except Exception as e:
                print(f"An error occurred while processing {url}: {e}")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_file = os.path.join(OUTPUT_DIR, f'{timestamp} rss_feed.json')
    save_to_json(all_rss_items, output_file)
    update_cumulative_file(all_rss_items, CUMULATIVE_FILE)


if __name__ == "__main__":
    main()
