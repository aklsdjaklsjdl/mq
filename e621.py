import requests
import re
import json
import itertools
from bs4 import BeautifulSoup
from post import Post
from urllib.parse import urljoin, urlparse

HEADERS = {
    'authority': 'e621.net',
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
}

class E621:
    def get_post(post_id):
        login = "roflcopter2"
        api_key = "8SNbALBeC6wLrdUoMmJ82rgC"
        url = "https://e621.net/posts/{}.json?api_key={}&login={}".format(post_id, api_key, login)
        r = requests.get(url, headers=HEADERS, verify=False)
        try:
            j = json.loads(r.text)["post"]
        except:
            print(r.text, "fucl")
            return
        tag_list = []
        for tags in list(j["tags"].values()):
            tag_list.extend(tags)
        artist = j["tags"]["artist"]
        tag_list.append('explicit')
        tag_list.append('furry')
        url = "https://e621.net/posts/{}".format(post_id)

        source_url = j["sources"][0] if j["sources"] else url
        if "http://" not in source_url:
            source_url =  url
        image_url =  j["file"]["url"]
        score = j["score"]["total"]
        return Post(','.join(tag_list), image_url, source_url, score)

    def get_page(url):
        response = requests.get(url, headers=HEADERS, verify=False)

        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all(class_='post-preview')
        ids = set()
        for image in images:
            href = image.a['href']
            id_ = re.match(".*\/(\d+)", href).group(1)
            ids.add(id_)
        return ids

