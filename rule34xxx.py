import requests
import re
from urllib.parse import urlparse
from urllib.parse import parse_qs
from bs4 import BeautifulSoup
from post import Post
from sitebase import SiteBase
import urllib.parse
import time

SLEEP = 2
HEADERS = {
    'authority': 'rule34.xxx',
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
    'accept-language': 'en-US,en;q=0.9'
}

def convert_rating(rating):
    if rating == 'Questionable':
        return 'questionable'
    elif rating == 'Safe':
        return 'safe'
    elif rating == 'Explicit':
        return 'explicit'
    raise Exception(":fuck")

class Rule34xxx(SiteBase):
    def get_post(post_id):
        url = "https://rule34.xxx/index.php?page=post&s=view&id={}".format(post_id)
        print(url)
        r = requests.get(url, verify=False)
        time.sleep(SLEEP) # 1 sec
        soup = BeautifulSoup(r.text, 'html.parser')
        tags = soup.find_all(class_='tag')
        artist = None
        tag_list = []
        has_artist = False
        for tag in tags:
            tag_name = tag.a.text
            if 'tag-type-artist' in tag['class']:
                artist = "artist:{}".format(tag_name)
                tag_list.append(artist)
                has_artist = True
            elif tag_name != "tagme":
                tag_list.append(tag_name)
        try:
            rating = soup.find(text=re.compile("Rating: "))
            rating_tag = convert_rating(rating.split(': ')[1])
        except:
            rating_tag = 'explicit'
        tag_list.append(rating_tag)
        if len(tag_list) <= 2:
            tag_list.append("temptag")
        image_url = soup.find(text=re.compile("Original image")).parent['href']
        source = soup.find(text="\nSource")
        source_url = source.parent.input['value'] if source else url
        if "http://" not in source_url and "https://" not in source_url:
            source_url = url
        if source_url.startswith("雏田故事"):
            source_url = "https://www.pixiv.net/en/artworks/83340942"
        if source_url.startswith("Shellvi"):
            source_url = "https://twitter.com/ShellviArt/status/1319450178731102209"
        if source_url.startswith("MEGA DOOD"):
            source_url = "https://twitter.com/ichduhernz/status/1366594986905653249?s=20"
        if source_url.startswith("edit of: https://www.pixiv.net/member_illust.php?mode=medium&illust_id=74416284"):
            source_url = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id=74416284"


        print(source_url)
        score = soup.find(text=re.compile("Score:")).parent.span.text
        return Post(','.join(tag_list), image_url, source_url.strip(), score)

    def get_page(url):
        response = requests.get(url, headers=HEADERS, verify=False)
        time.sleep(SLEEP) # 1 sec

        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all(class_='thumb')
        ids = set()
        for image in images:
            href = image.a['href']
            id_ = re.match(".*id=(\d+)", href).group(1)
            ids.add(id_)
        return ids

    def get_url(tag_list):
        if (isinstance(tag_list, str)):
            raise Exception("input should be list")
        url = "https://rule34.xxx/index.php?page=post&s=list&tags="
        param = " ".join(tag_list)
        safe_string = urllib.parse.quote_plus(param, safe='', encoding=None, errors=None)
        return url + safe_string

    def get_all_urls(tag_list):
        url = Rule34xxx.get_url(tag_list)
        response = requests.get(url, headers=HEADERS, verify=False)
        time.sleep(SLEEP) # 1 sec
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            page = soup.find("div", class_="pagination").findChildren("a" , recursive=False) 
        except:
            # no pages
            return []
        try:
            last = page[-1]
        except:
            # only 1 page
            return [url]
        urlparsed = urlparse(last['href'])
        pid = parse_qs(urlparsed.query)['pid'][0]
        ret = []
        for i in range(0, int(pid) + 1, 42):
            ret.append("{}&pid={}".format(url, i))
        return ret

