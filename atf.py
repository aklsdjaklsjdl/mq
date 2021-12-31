import requests
import re
from bs4 import BeautifulSoup
from post import Post
from urllib.parse import urljoin, urlparse

class Atf:
    def get_post(post_id):
        url = "https://booru.allthefallen.moe/posts/{}".format(post_id)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        tags = soup.find(class_='tag-list').findChildren('li' , recursive=True)
        artist = None
        tag_list = []
        has_artist = False
        for tag in tags:
            tag_name = tag.findChildren('a', recursive=False)[1].text
            if 'tag-type-1' in tag['class']:
                artist = "artist:{}".format(tag_name)
                tag_list.append(artist)
                has_artist = True
            elif tag != "tagme":
                tag_list.append(tag_name)
        tag_list.append('explicit')
        image_url = soup.find(text="Download").parent['href']
        stripped_image_url = urljoin(image_url, urlparse(image_url).path)
        source = soup.find(text=re.compile("Source:"))
        source_url = "" if not source.nextSibling else source.nextSibling['href']
        score = soup.find(text=re.compile("Score:")).parent.span.text.strip()
        return Post(','.join(tag_list), stripped_image_url, source_url, score)

    def get_page(url):
        headers = {
            'authority': 'booru.allthefallen.moe',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': 'user_id=68163; tag_blacklist=guro%2520asd; pass_hash=aa568dc05324edbb98cf836b28457fe768f81641; fringeBenefits=yup; comment_threshold=0; post_threshold=0; PHPSESSID=gd7nlh2lqqar995n8sgbvlsip1',
        }

        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all(class_='post-preview')
        ids = set()
        for image in images:
            href = image.a['href']
            id_ = re.match(".*\/(\d+)", href).group(1)
            ids.add(id_)
        return ids
