import requests
import re
from bs4 import BeautifulSoup
from post import Post
HEADERS = {
    'authority': 'rule34.paheal.net',
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

class Paheal:
    def get_post(post_id):
        url = "http://rule34.paheal.net/post/view/{}".format(post_id)
        r = requests.get(url, headers=HEADERS) 
        soup = BeautifulSoup(r.text, 'html.parser')
        tags = soup.find_all(class_='tag_name')
        tag_list = []
        has_artist = False
        for tag in tags:
            tag_name = tag.text
            if tag_name != "tagme":
                tag_list.append(tag_name)
        tag_list.append("explicit")
        tag_list.append("paheal")
        print(url)
        image_url = soup.find(text=re.compile("File Only")).parent['href']
        source = soup.find(text=re.compile("Source\sLink"))
        source_url = source.parent['href'] if source else url
        if "http://" not in source_url:
            source_url = url
        return Post(','.join(tag_list), image_url, source_url, 0)

    def get_page(url):
        response = requests.get(url, headers=HEADERS)

        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all(class_='shm-thumb-link')
        ids = set()
        for image in images:
            href = image['href']
            id_ = re.match(".*/view/(\d+)", href).group(1)
            ids.add(id_)
        return ids
