from argparse import ArgumentParser
from typing import List, Optional, Sequence
import requests
import json as json_file
import xml.etree.ElementTree as element_tree


class UnhandledException(Exception):
    pass


def rss_parser(
        xml: str,
        limit: Optional[int] = None,
        json: bool = False,
) -> List[str]:
    """
    RSS parser.

    Args:
        xml: XML document as a string.
        limit: Number of the news to return. if None, returns all news.
        json: If True, format output as JSON.

    Returns:
        List of strings.
        Which then can be printed to stdout or written to file as a separate lines.

    Examples:
        # >>> xml = '<rss><channel><title>Some RSS Channel</title><link>'/
        'https://some.rss.com</link><description>Some RSS Channel</description></channel></rss>'
        # >>> rss_parser(xml)
        ["Feed: Some RSS Channel",
        "Link: https://some.rss.com"]
        # >>> print("\\n".join(rss_parser(xmls)))
        Feed: Some RSS Channel
        Link: https://some.rss.com
    """
    channel_tag_list = ['title', 'link', 'lastBuildDate', 'pubDate', 'language',
                        'category', 'managinEditor', 'description']
    item_tag_list = ['title', 'author', 'pubDate', 'link', 'category', 'description']

    def parse_formatter(xml: str, limit) -> list:
        xml_root = element_tree.fromstring(xml)
        result = []
        channel_count = 0

        for channel in xml_root.findall('channel'):
            if channel_count == limit:
                break
            channel_dict = {tag.tag: tag.text for tag in channel if tag.tag in channel_tag_list}

            items_list = []
            for item_count, item in enumerate(channel.findall('item')):
                if item_count == limit:
                    break
                item_dict = {tag.tag: tag.text for tag in item if tag.tag in item_tag_list}
                items_list.append(item_dict)

            if items_list:
                channel_dict['items'] = items_list

            result.append(channel_dict)
            channel_count += 1

        return result

    def console_output(result: list) -> list:
        result_str = []
        ch_title_console = ['Feed', 'Link', 'Last Build Date', 'Date',
                            'Language', 'Categories', 'Editor', 'Description']
        item_title_console = ['Title', 'Author', 'Date', 'Link', 'Category', 'Description']

        for channel in result:
            for tag in channel_tag_list:
                if channel.get(tag):
                    index = channel_tag_list.index(tag)
                    result_str.append(f"{ch_title_console[index]}: {channel.get(tag)}")

            result_str.append('')
            if 'items' in channel:
                for item in channel['items']:
                    for tag in item_tag_list:
                        if item.get(tag):
                            index = item_tag_list.index(tag)
                            if tag == 'description':
                                result_str.append(f"\n{item.get(tag)}\n")
                            else:
                                result_str.append(f"{item_title_console[index]}: {item.get(tag)}")
        return result_str

    def json_output(result: list) -> List[str]:
        if len(result) == 1:
            json_string = json_file.dumps(result[0], indent=2, ensure_ascii=False)
        else:
            json_string = json_file.dumps(result, indent=2, ensure_ascii=False)

        json_array = json_string.splitlines()
        return json_array

    parsed_result = parse_formatter(xml, limit)

    if json:
        return json_output(parsed_result)
    else:
        return console_output(parsed_result)


def main(argv: Optional[Sequence] = None):
    """
    The main function of your task.
    """
    parser = ArgumentParser(
        prog="rss_reader",
        description="Pure Python command-line RSS reader.",
    )
    parser.add_argument("source", help="RSS URL", type=str, nargs="?")
    parser.add_argument(
        "--json", help="Print result as JSON in stdout", action="store_true"
    )
    parser.add_argument(
        "--limit", help="Limit news topics if this parameter provided", type=int
    )

    args = parser.parse_args(argv)

    # Set up headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    xml = requests.get(args.source, headers=headers).text
    try:
        print("\n".join(rss_parser(xml, args.limit, args.json)))
        return 0
    except Exception as e:
        raise UnhandledException(e)


if __name__ == "__main__":
    main()
