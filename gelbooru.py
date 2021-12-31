import requests
import time
import re
from bs4 import BeautifulSoup
from post import Post
from sitebase import SiteBase
from urllib.parse import urlparse
from urllib.parse import parse_qs
import urllib.parse
import time

SLEEP = 2
HEADERS = {
    'authority': 'gelbooru.com',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': 'PHPSESSID=c93n406b1iciqi59ao036tg594',
}

def convert_rating(rating):
    if rating == 'Questionable':
        return 'questionable'
    elif rating == 'Safe':
        return 'safe'
    elif rating == 'Explicit':
        return 'explicit'
    raise Exception(":fuck")

class Gelbooru:
    def get_headers():
        return HEADERS
    def get_post(post_id):
        url = "https://gelbooru.com/index.php?page=post&s=view&id={}".format(post_id)
        r = requests.get(url, headers=HEADERS, verify=False)
        time.sleep(SLEEP) # 1 sec
        soup = BeautifulSoup(r.text, 'html.parser')
        tags = soup.find(class_='tag-list').findChildren('li' , recursive=False)
        artist = None
        tag_list = []
        has_artist = False
        for tag in tags:
            if tag.a is None:
                break
            tag_name = tag.findChildren('a', recursive=False)[0].text
            if 'tag-type-artist' in tag['class']:
                artist = "artist:{}".format(tag_name)
                tag_list.append(artist)
                has_artist = True
            elif tag != "tagme":
                tag_list.append(tag_name)
        try:
            rating = soup.find(text=re.compile("Rating: "))
            rating_tag = convert_rating(rating.split(': ')[1])
        except:
            rating_tag = 'explicit'
        tag_list.append(rating_tag)
        tag_list.append('hentai')
        if len(tag_list) <= 2:
            tag_list.append("temptag")
        image_url = soup.find(text="Original image").parent['href']
        source = soup.find(text=re.compile("Source: "))
        if source and source.parent and source.parent.a.text.startswith("www."):
            source = "http://" + source.parent.a.text
        elif not source or not source.parent.a or "http://" not in source.parent.a.text:
            source = url
        else:
            source = source.parent.a.text
        score = soup.find(text=re.compile("Score:")).parent.span.text
        return Post(','.join(tag_list), image_url, source, score)

    def get_url(tag_list):
        if (isinstance(tag_list, str)):
            raise Exception("input should be list")
        url = "https://gelbooru.com/index.php?page=post&s=list&tags="
        param = " ".join(tag_list)
        safe_string = urllib.parse.quote_plus(param, safe='', encoding=None, errors=None)
        return url + safe_string

    def get_page(url):
       response = requests.get(url, headers=HEADERS, verify=False)
       time.sleep(SLEEP) # 1 sec

       soup = BeautifulSoup(response.text, 'html.parser')
       images = soup.find_all(class_='thumbnail-preview')
       ids = set()
       for image in images:
           href = image.a['href']
           id_ = re.match(".*id=(\d+)", href).group(1)
           ids.add(id_)
       return ids

    def get_all_urls(tag_list):
        url = Gelbooru.get_url(tag_list)
        response = requests.get(url, headers=HEADERS, verify=False)
        time.sleep(SLEEP) # 1 sec
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            page = soup.find("div", class_="pagination").findChildren("a" , recursive=True) 
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

if __name__ == '__main__':
    print(Gelbooru.get_all_urls(['takemura_sessyu', 'rating:explicit']))
