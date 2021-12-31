import requests
import re
import redis
import os
import json
import time
import io, urllib.request

from bs4 import BeautifulSoup
from post import Post
from urllib.parse import urlparse
from PIL import Image
from PIL import UnidentifiedImageError
from io import BytesIO

from rule34xxx import Rule34xxx
from gelbooru import Gelbooru
from atf import Atf
from paheal import Paheal
from e621 import E621
from webm_converter import Converter
from upload import Uploader

import PIL
PIL.Image.MAX_IMAGE_PIXELS = 933120000

# redis
PORT= 6379
# server
API_KEY= "rkO70sKjvlhSkV0JoIJW" 
HOST =  "https://www.rule34.lol" # "http://localhost:8080" 

# local
#API_KEY= "ygsDHiKlsESBG3ynE2oA" 
#HOST = "http://localhost:8080"  

def download(url, path):
    with urllib.request.urlopen(url) as response, open(path, 'wb') as out_file:
        length = response.getheader('content-length')
        blockSize = 1000000  # default value

        if length:
            length = int(length)
            blockSize = max(4096, length // 20)

        print("UrlLib len, blocksize: ", length, blockSize)

        bufferall = io.BytesIO()
        size = 0
        while True:
            buffernow = response.read(blockSize)
            if not buffernow:
                break
            bufferall.write(buffernow)
            size += len(buffernow)
            if length:
                percent = int((size / length)*100)
                print(f"download: {percent}% {url}")
        print("Buffer All len:", len(bufferall.getvalue()))
        print("Writing to ", path)
        out_file.write(bufferall.getvalue())

#def get_image():
    #url = "https://www.rule34.lol/api/v1/json/images/3702?key=rkO70sKjvlhSkV0JoIJW"
    #r = requests.get(url)
    #print(r.text)

def is_tall(url, booru):
    print(url)
    if booru == 'gelbooru':
        response = requests.get(url, headers=Gelbooru.get_headers(), verify=False)
    else:
        response = requests.get(url, verify=False)
    time.sleep(1) # 1 sec
    if response.status_code != 200:
        print("can't get image ", url)
        raise ValueError("can't get image")
    f = BytesIO(response.content)
    try:
        img = Image.open(f)
    except:
        raise ValueError("can't get image")
    width, height = img.size
    if width / height < 0.45:
        return True
    return False

def filter_tags(tags):
    s = tags.split(",")
    if "explicit" in s:
        if "suggestive" in s:
            s.remove("suggestive")
        if "questionable" in s:
            s.remove("questionable")
        if "safe" in s:
            s.remove("safe")
    if "questionable" in s:
        if "suggestive" in s:
            s.remove("suggestive")
        if "safe" in s:
            s.remove("safe")
    if "suggestive" in s:
        if "safe" in s:
            s.remove("safe")
    if "alex" in s:
        s.remove("alex")
        s.append("alex_(totally_spies)")
    if "chi chi" in s:
        s.remove("chi chi")
        s.append("chi_chi_(gumball)")
    banned_tags = ['gwen', 'apex', 'sky', 'wattson', 'jenny', 'jinx', 'millie', 'tigress', 'cream', 'morty', 'wrath', 'gwen', 'wendy', 'sasha', 'annie', 'jessica', 'kenny', 'fate', 'max', 'sakura','jessica', 'fiona']
    s = [ x for x in s if x not in banned_tags ]
    return ','.join(s)

class Booru:
    @staticmethod
    def can_skip(key, id_, skip_webm):
        red = redis.Redis(port=PORT)
        if red.sismember(key + "mp4", id_):
            if not skip_webm and red.sismember(key + "mp4converted", id_):
                print("Not skipping webm, found mp4 but have converted")
                if red.sismember(key, id_):
                    print("Key/Value {}:{} already in redis".format(key, id_))
                    return True
                else:
                    print("Key not found in redis")
                    return False
            else:
                print("MP4 Key/Value already in redis")
                return True
        if red.sismember(key + "swf", id_):
            print("SWF Key/Value already in redis")
            return True
        if red.sismember(key + "fail", id_):
            print("FAILURE Key/Value already in redis")
            return True
        if skip_webm and red.sismember(key + "webm", id_):
            print("WEBM Key/Value already in redis")
            return True
        if red.sismember(key + "tall", id_):
            print("Tall Key/Value already in redis")
            return True
        if red.sismember(key + "blacklist", id_):
            print("Blacklisted Key/Value")
            return True
        if red.sismember(key, id_):
            print("Key/Value {}:{} already in redis".format(key, id_))
            return True
        return False

    @staticmethod
    def get_converted_url(key, id_):
        return "https://s3-us-west-1.amazonaws.com/webms-mp4convertedllmao/{}-{}.webm".format(key, id_)

    @staticmethod
    def convert_mp4(post, key, id_, dry_run = False):
        url = Booru.get_converted_url(key, id_)
        red = redis.Redis(port=PORT)
        if red.sismember(key + "mp4converted", id_):
            print("{}:{}".format(key, id_), "already converted")
            return url
        dir_ = os.path.dirname(os.path.realpath(__file__)) 
        file_name = "{}-{}.mp4".format(key, id_)
        inpath = "{}/input/{}".format(dir_, file_name)
        outdir = "{}/output".format(dir_)
        download(post.image_url, inpath)
        path = Converter().convert(file_name)
        Uploader().upload(outdir, file_name.replace('mp4', 'webm'))
        red.sadd(key + "mp4converted", id_)
        return url

    def get_mp4s(key, ignore_converted=False):
        red = redis.Redis(port=PORT)
        s = set()
        for id_ in red.smembers(key + "mp4"):
            if ignore_converted and red.sismember(key + "mp4converted", id_):
                print(id_, "is converted already")
                continue
            s.add(id_)
        return s

    @staticmethod
    def post_image(post, key, id_, dry_run = False, skip_webm = True):
        if Booru.can_skip(key, id_, skip_webm):
            return
        red = redis.Redis(port=PORT)
        path = urlparse(post.image_url).path
        ext = os.path.splitext(path)[1][1:]
        if ext == "swf":
            red.sadd(key + "swf", id_)
            print('Skipping cause swf')
            return
        if ext == "mp4":
            if not dry_run:
                red.sadd(key + "mp4", id_)
            if not skip_webm and red.sismember(key + "mp4converted", id_):
                print("found converted webm!")
                url = Booru.get_converted_url(key, id_)
                print(post)
                post.image_url = url
                ext = "webm"
            else:
                print('Skipping cause mp4')
                return
        if skip_webm and ext == "webm":
            if not dry_run:
                red.sadd(key + "webm", id_)
            print('Skipping cause webm')
            return
        tall = False
        if ext == 'webm':
            if ext == "webm" and not skip_webm:
                print("Processing webm")
        else:
            try:
                tall = is_tall(post.image_url, key)
            except ValueError as e:
                print(e)
                raise e
                red.sadd(key + "fail", id_)
                print("Can't get image, oops, adding to fail set")
                return
        if ext != "webm" and tall:
            if not dry_run:
                red.sadd(key + "tall", id_)
            print("Skipping cause too tall")
            return
        url = "{}/api/v1/json/images?key={}".format(HOST, API_KEY)
        j = {
          "image": {
            "description": "",
            "tag_input": filter_tags(post.tags),
            "source_url": post.source_url
          },
          "url": post.image_url
        }
        headers = {'content-type': 'application/json'}
        if dry_run:
            print("dry_run, not posting")
            return
        r = requests.post(url, json=j)
        time.sleep(1) # 1 sec
        if r.status_code == 200:
            red.sadd(key, id_)
            print('Successfully posted {}:{}'.format(key, id_))
            return
        elif r.status_code == 400:
            j = json.loads(r.text) 
            if j["errors"] and "image_orig_sha512_hash" in j["errors"]:
                print('Image already posted successfully.')
                red.sadd(key, id_)
                return (True, "Already in redis")
            else:
                print("no idea what error, ", r.text)
                raise ValueError("Error posting, weird error")
        else:
            print("error posting ", "{}:{}".format(key, id_), r, r.text)
            print("a", url, j)
            raise ValueError ("Error posting image (maybe image too big)")

    @staticmethod
    def post(booru, id_, webm=False):
        if booru == "gelbooru":
            if not Booru.can_skip(booru, id_, not webm):
                return Booru.post_image(Gelbooru.get_post(id_), booru, id_, False, not webm)
        elif booru == "rule34xxx":
            if not Booru.can_skip(booru, id_, not webm):
                return Booru.post_image(Rule34xxx.get_post(id_), booru, id_, False, not webm)
        elif booru == "atf":
            if not Booru.can_skip(booru, id_, not webm):
                return Booru.post_image(Atf.get_post(id_), booru, id_, False, not webm)
        elif booru == "paheal":
            if not Booru.can_skip(booru, id_, True):
                return Booru.post_image(Paheal.get_post(id_), "paheal", id_)
        elif booru == "e621":
            if not Booru.can_skip(booru, id_, not webm):
                return Booru.post_image(E621.get_post(id_), "e621", id_, False, not webm)

def convert_webms():
    red = redis.Redis(port=PORT)
    s = set()
    for key in ["rule34xxx"]:
        for id_ in red.smembers(key + "mp4"):
            post = Rule34xxx.get_post(id_.decode("utf-8"))
            Booru.convert_mp4(post, "rule34xxx", id_.decode("utf-8"))

if __name__ ==  '__main__':
    def f():
        red = redis.Redis(port=PORT)
        #red.delete("gelboorufail")
        #id_ = '1499489' 
        #post = E621.get_post(id_)
        #Booru.post("e621", id_, True)
        #return

        for key in ["gelbooru", "rule34xxx"]:
            all_ = []
            done = []
            for id_ in red.smembers(key + "webm"):
                if red.sismember(key, id_):
                    done.append(id_)
                else:
                    all_.append(id_)
            print("found ", len(done), "already uploaded")
            print("found ", len(all_), "to upload")
            if len(all_) == 0:
                print("none found")
                break
            do = 5
            for id_ in all_:
                if key == 'gelbooru':
                    post = Gelbooru.get_post(id_.decode("utf-8"))
                else:
                    post = Rule34xxx.get_post(id_.decode("utf-8"))
                x = Booru.post(key, id_.decode("utf-8"), True)
                if x:
                    print("THIS ONE IS ALREADY IN REDIS")
                    print(do)
                else:
                    do-=1 
                if do < 1:
                    break
        return

        #red.srem('rule34xxx', '3693009')
        #id_ = '3693009' 
        #post = Rule34xxx.get_post(id_)
        #Booru.convert_mp4(post, "rule34xxx", id_)
        #Booru.post("rule34xxx", id_, True)

        #s = set()
        #for key in ["rule34xxx"]:
            #for id_ in red.smembers(key + "mp4"):
                #post = Rule34xxx.get_post(id_.decode("utf-8"))
                #Booru.convert_mp4(post, "rule34xxx", id_.decode("utf-8"))
        #print(Booru.get_mp4s("rule34xxx", True))

        #this posts new webm every time
        for key in ["rule34xxx"]:
            all_ = []
            done = []
            for id_ in red.smembers(key + "mp4converted"):
                if red.sismember(key, id_):
                    done.append(id_)
                else:
                    all_.append(id_)
            print("found ", len(done), "already uploaded")
            print("found ", len(all_), "to upload")
            if len(all_) == 0:
                print("none found")
                break
            do = 5
            for id_ in all_:
                post = Rule34xxx.get_post(id_.decode("utf-8"))
                Booru.convert_mp4(post, "rule34xxx", id_.decode("utf-8"))
                x = Booru.post("rule34xxx", id_.decode("utf-8"), True)
                if x:
                    print("THIS ONE IS ALREADY IN REDIS")
                    print(do)
                else:
                    do-=1 
                if do < 1:
                    break
        convert_webms()
    f()
