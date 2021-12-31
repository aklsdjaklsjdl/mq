#!/usr/bin/env python
import pika
import sys
import time
import random
import redis
from gelbooru import Gelbooru
from atf import Atf
from paheal import Paheal
from rule34xxx import Rule34xxx
from booru import Booru

def get_booru(site):
    if site == "rule34xxx":
        return Rule34xxx
    elif site == "rule34xxx":
        return 
    elif site == "gelbooru":
        return Gelbooru
    elif site == "atf":
        return Atf
    else:
        return Shit


def send(message): 
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost',heartbeat=600,
                                               blocked_connection_timeout=300))
    channel = connection.channel()

    channel.queue_declare(queue='booru', durable=True, arguments={"x-max-priority": 255})

    random_number = random.randint(1, 100)
    channel.basic_publish(
        exchange='',
        routing_key='booru',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            priority=random_number
        ))
    print(" [x] Sent %r" % message)
    connection.close()

def queue(*commands):
    send(" ".join(commands))

class Cron():
    def __init__(self):
        self.red = redis.Redis()

    def have_key_for_id(self, site, id_):
        if self.red.sismember(site + "mp4", id_):
            #MP4 Key/Value already in redis
            return True
        if self.red.sismember(site + "webm", id_):
            #WEBM Key/Value already in redis
            return True
        if self.red.sismember(site + "tall", id_):
            #Tall
            return True
        if self.red.sismember(site + "blacklist", id_):
            #blacklisted
            return True
        return self.red.sismember(site, id_)

    def blacklist(self, site, id_):
        print("blacklisting ", site, id_)
        self.red.sadd(site + "blacklist", id_)

    def get_latest(self, site, tag_list):
        booru = get_booru(site)
        url = booru.get_url(tag_list)
        ids = [x for x in booru.get_page(url)]
        for id_ in ids:
            is_member = self.have_key_for_id(site, id_)
            if not is_member:
                queue(site, id_)
        max_id = max([int(id_) for id_ in ids]) if len(ids) > 0 else -1
        return max_id

    #def lookup_latest(site, tag_list):
    #    self.red = redis.Redis()
    #    key = site + "latest-" + ",".join(tag_list)
    #    print(key)
    #    r = self.red.get(key)
    #    print(r)

    def register(self, site, tag_list):
        if isinstance(tag_list, str):
            print("arg needs to be list")
            return
        key = site + "cron"
        tags = ",".join(tag_list)
        if self.red.sismember(key, tags):
            print(key, tags, "already registered")
        else:
            self.red.sadd(key, tags)

    def unregister(self, site, tag_list):
        if isinstance(tag_list, str):
            print("arg needs to be list")
            return
        key = site + "cron"
        tags = ",".join(tag_list)
        if self.red.sismember(key, tags):
            self.red.srem(key, tags)
        else:
            print(key, tags, "not registered, cant unregister")

    def list_registered(self, site):
        key = site + "cron"
        x = self.red.smembers(key)
        return x

    def clear_cache(self, key):
        self.red.delete(key)

    def do_the_cron(self):
        for site in ["rule34xxx"]:
            reg = self.list_registered(site)
            if reg is None:
                continue
            for tag_list in reg:
                print("Getting ", site, tag_list)
                decode = tag_list.decode("utf-8").split(',')
                # TODO(FUCK)
                self.get_latest(site, decode)
                time.sleep(2) # sleep 1 sec


if __name__ == "__main__":
    cron = Cron()
    cron.register("rule34xxx", ["peppermintwolf"])
    cron.register("rule34xxx", ["akirascrolls"])
    cron.register("rule34xxx", ["duxt"])
    cron.register("rule34xxx", ["jcm2"])
    cron.register("rule34xxx", ["hexanne"])
    cron.register("rule34xxx", ["blanclauz"])
    cron.register("rule34xxx", ["xiao_miao"])
    cron.register("rule34xxx", ["afrobull"])
    cron.register("rule34xxx", ["klimspree"])
    cron.register("rule34xxx", ["milkyverse"])
    cron.register("rule34xxx", ["andava"])
    cron.register("rule34xxx", ["astranger"])
    cron.register("rule34xxx", ["sfan"])
    cron.register("rule34xxx", ["incognitymous"])
    cron.register("rule34xxx", ["hackman"])
    cron.register("rule34xxx", ["badbrains"])
    cron.register("rule34xxx", ["apostle"])
    cron.register("rule34xxx", ["playzholder"])
    cron.register("rule34xxx", ["mid-fight_masses"])
    cron.register("rule34xxx", ["speedosausage"])
    cron.register("rule34xxx", ["optionaltypo"])
    cron.register("rule34xxx", ["unladylike"])
    cron.register("rule34xxx", ["butterflan01"])
    cron.register("rule34xxx", ["threetwigs"])
    cron.register("rule34xxx", ["qupostuv35"])
    cron.register("rule34xxx", ["felox08"])
    cron.register("rule34xxx", ["gaiidraws"])
    cron.register("rule34xxx", ["legoman"])
    cron.register("rule34xxx", ["pinkladymage"])
    cron.register("rule34xxx", ["drpizzaboi1"])
    cron.register("rule34xxx", ["noctz"])
    cron.register("rule34xxx", ["tisumira"])
    cron.register("rule34xxx", ["cubedcoconut"])
    cron.register("rule34xxx", ["mannysdirt"])
    cron.register("rule34xxx", ["blanclauz"])
    cron.register("rule34xxx", ["slappyfrog"])
    cron.register("rule34xxx", ["justisleo"])
    cron.register("rule34xxx", ["ghostmussa"])
    cron.register("rule34xxx", ["senor_gato"])
    cron.register("rule34xxx", ["demonlorddante"])
    cron.register("rule34xxx", ["saifergt750"])
    cron.register("rule34xxx", ["fireboxstudio"])
    cron.register("rule34xxx", ["succuboos"])
    cron.register("rule34xxx", ["hahaboobies"])
    cron.register("rule34xxx", ["chihunhentai"])
    cron.register("rule34xxx", ["fan_pixxx"])
    cron.register("rule34xxx", ["combos-n-doodles"])
    cron.register("rule34xxx", ["bload_esefo"])
    cron.register("rule34xxx", ["zveno"])
    cron.register("rule34xxx", ["spluckytama"])
    cron.register("rule34xxx", ["fatcat17"])
    cron.register("rule34xxx", ["rescraft"])
    cron.register("rule34xxx", ["slipperyt"])
    cron.register("rule34xxx", ["fpsblyck"])
    cron.register("rule34xxx", ["lechugansfw"])
    cron.register("rule34xxx", ["eroticphobia"])
    cron.register("rule34xxx", ["lasterk"])
    cron.register("rule34xxx", ["mandio_art"])
    cron.register("rule34xxx", ["thrumbo"])
    cron.register("rule34xxx", ["drremedy"])
    cron.register("rule34xxx", ["konni_alice"])
    cron.register("rule34xxx", ["keramagath"])
    cron.register("rule34xxx", ["tourbillon"])
    cron.register("rule34xxx", ["gkg"])
    cron.register("rule34xxx", ["twistedgrim"])
    cron.register("rule34xxx", ["kalia3see"])
    cron.register("rule34xxx", ["suelix"])
    cron.register("rule34xxx", ["lumineko"])
    cron.register("rule34xxx", ["mrsmutx"])
    cron.register("rule34xxx", ["shado3"])
    cron.register("rule34xxx", ["kenjanoishi"])
    cron.register("rule34xxx", ["ryoryo"])
    cron.register("rule34xxx", ["kimtoxic"])
    cron.register("rule34xxx", ["rizkitsuneki"])
    cron.register("rule34xxx", ["1609bell"])
    cron.register("rule34xxx", ["kittyplsaaa"])
    cron.register("rule34xxx", ["enia"])
    cron.register("rule34xxx", ["bestofnesia"])
    cron.register("rule34xxx", ["aleuz91"])
    cron.register("rule34xxx", ["gnomfist"])
    cron.register("rule34xxx", ["blushypixy"])
    cron.register("rule34xxx", ["shellvi"])
    cron.register("rule34xxx", ["soxciao"])
    cron.register("rule34xxx", ["damao_yu"])
    cron.register("rule34xxx", ["sinx"])
    cron.register("rule34xxx", ["kimoshi"])
    cron.register("rule34xxx", ["dude-doodle-do"])
    cron.register("rule34xxx", ["centinel303"])
    cron.register("rule34xxx", ["chrno"])
    cron.register("rule34xxx", ["beveledblock"])
    cron.register("rule34xxx", ["saneperson"])
    cron.register("rule34xxx", ["matsui_hiroaki"])
    cron.register("rule34xxx", ["felipe_godoy"])
    cron.register("rule34xxx", ["neocoill"])
    cron.register("rule34xxx", ["luminyu"])
    cron.register("rule34xxx", ["kuplo"])
    cron.register("rule34xxx", ["rsinnamonroll"])
    cron.register("rule34xxx", ["bayernsfm"])
    cron.register("rule34xxx", ["flick"])
    cron.register("rule34xxx", ["venusflowerart"])
    cron.register("rule34xxx", ["fridge_(artist)"])
    cron.register("rule34xxx", ["creeeen"])
    cron.register("rule34xxx", ["lewdamone"])
    cron.register("rule34xxx", ["lumineko"])
    cron.register("rule34xxx", ["mavolier"])
    cron.register("rule34xxx", ["blue-senpai"])
    cron.register("rule34xxx", ["sssir8"])
    cron.register("rule34xxx", ["sssir"])
    cron.register("rule34xxx", ["bluebreed"])
    cron.register("rule34xxx", ["pinkanimations"])
    cron.register("rule34xxx", ["beni_imo"])
    cron.register("rule34xxx", ["naso4"])
    cron.register("rule34xxx", ["theeshrimp"])
    cron.register("rule34xxx", ["cherrypix"])
    cron.register("rule34xxx", ["jailbait_knight"])
    cron.register("rule34xxx", ["animeflux"])
    cron.register("rule34xxx", ["jonathanpt"])
    cron.register("rule34xxx", ["metal_owl"])
    cron.register("rule34xxx", ["unladylike"])
    cron.register("rule34xxx", ["koichiko_(artist)"])
    cron.register("rule34xxx", ["milkysus"])
    cron.register("rule34xxx", ["nerdbayne"])
    cron.register("rule34xxx", ["sirfy"])
    cron.register("rule34xxx", ["playzholder"])
    cron.register("rule34xxx", ["kinto-bean"])
    cron.register("rule34xxx", ["roxley"])
    cron.register("rule34xxx", ["shado3"])
    cron.register("rule34xxx", ["koloo"])
    cron.register("rule34xxx", ["paper_megane"])
    cron.register("rule34xxx", ["dross"])
    cron.register("rule34xxx", ["jhiaccio"])
    cron.register("rule34xxx", ["koishiko_(artist)"])
    cron.register("rule34xxx", ["mushroompus"])
    cron.register("rule34xxx", ["alfa995"])
    cron.register("rule34xxx", ["javisuzumiya"])
    cron.register("rule34xxx", ["neronova"])
    cron.register("rule34xxx", ["thefuckingdevil"])
    cron.register("rule34xxx", ["masterohyeah"])
    cron.register("rule34xxx", ["bdone"])
    cron.register("rule34xxx", ["d-art"])
    cron.register("rule34xxx", ["whimsyghost"])
    cron.register("rule34xxx", ["misusart"])
    cron.register("rule34xxx", ["creambee"])


    cron.register("gelbooru", ["yellowroom"])
    cron.register("gelbooru", ["zen33n"])
    cron.register("gelbooru", ["pongldr"])
    cron.register("gelbooru", ["felipe_godoy"])
    cron.register("gelbooru", ["chris_armin"])
    cron.register("gelbooru", ["bikupan"])
    cron.register("gelbooru", ["moursho"])

    cron.register("rule34xxx", ["relatedguy"])
    cron.register("paheal", ["relatedguy"])

    cron.register("paheal", ["Hackman"])
    cron.register("paheal", ["creek12"])
    cron.register("paheal", ["MrClearEdits"])

    cron.blacklist("e621", "1034408")
    cron.blacklist("paheal", "3520981")
    cron.blacklist("rule34xxx", "4122841")
    cron.blacklist("rule34xxx", "4773690")
    cron.blacklist("rule34xxx", "4846193")
    cron.blacklist("rule34xxx", "5148811")
    cron.blacklist("rule34xxx", "4961759")
    cron.blacklist("rule34xxx", "4961835")
    cron.blacklist("rule34xxx", "5104967")
    cron.blacklist("rule34xxx", "5020809")
    cron.blacklist("rule34xxx", "3092048")
    cron.blacklist("rule34xxx", "4865624")
    cron.blacklist("rule34xxx", "3177971")
    cron.blacklist("rule34xxx", "3330953")
    cron.blacklist("rule34xxx", "3330951")
    # add feature where if dont have max id for user, go and download all of them
    cron.register("rule34xxx", ["crap-man", "-futanari"])
    #list_cron.registeself.red("rule34xxx")
    cron.do_the_cron()
