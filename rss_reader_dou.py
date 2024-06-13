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
        pub_date_str = item.find('pubDate').text
        pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')

        rss_items.append({
            'category': category,
            'experience': experience,
            'title': item.find('title').text,
            'link': item.find('link').text,
            'description': clean_text(item.find('description').text),
            'pub_date': pub_date_str,
            'guid': item.find('guid').text,
            'pub_date_obj': pub_date  # Add datetime object for sorting
        })
    return rss_items


def save_to_json(data: List[Dict[str, str]], filename: str):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)


def load_cumulative_data(cumulative_file: str) -> List[Dict[str, str]]:
    if os.path.exists(cumulative_file):
        with open(cumulative_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []


def update_cumulative_file(new_data: List[Dict[str, str]], cumulative_file: str):
    cumulative_data = load_cumulative_data(cumulative_file)
    cumulative_guids = {entry['guid'] for entry in cumulative_data}

    filtered_new_data = [entry for entry in new_data if entry['guid'] not in cumulative_guids]

    cumulative_data.extend(filtered_new_data)
    cumulative_data.sort(key=lambda x: datetime.strptime(x['pub_date'], '%a, %d %b %Y %H:%M:%S %z'))
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

    all_rss_items.sort(key=lambda x: x['pub_date_obj'])
    for item in all_rss_items:
        del item['pub_date_obj']  # Remove datetime object before saving to JSON

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_file = os.path.join(OUTPUT_DIR, f'{timestamp} rss_feed.json')
    save_to_json(all_rss_items, output_file)
    update_cumulative_file(all_rss_items, CUMULATIVE_FILE)


if __name__ == "__main__":
    main()
