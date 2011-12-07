#!/usr/bin/env python
# -*- coding:utf-8 -*-
__version__ = '0.0.2'

from urllib2 import urlopen, Request, build_opener,\
    install_opener, HTTPCookieProcessor
from urlparse import parse_qsl, urlsplit
from re import findall, compile, M
from cookielib import CookieJar
from urllib import urlencode
from time import sleep
import logging
import xml.etree.ElementTree as Tree

# create logger
logger = logging.getLogger('lastm2planet')
logger.setLevel(logging.DEBUG)

lh = logging.FileHandler('www/lastm2planet.log')
lh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

lh.setFormatter(formatter)
logger.addHandler(lh)


class LastFM(object):
    """Last.fm parser class

    Keyword arguments:
    user -- login on http://last.fm
    key -- last.km api key

    """
    def __init__(self, user, key):
        self.user = user
        self.key = key

    def get_track(self):
        """Get text post for forum"""
        page = urlopen("http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&limit=1" % (self.user, self.key))
        p = Tree.fromstring(page.read())

        if 'nowplaying' in p.find('recenttracks/track').attrib:
            return '[url=http://www.lastfm.ru/music/{0}/_/{1}]{0} - {1}[/url]'.format(p.find('recenttracks/track/artist').text.encode('utf-8'),
                p.find('recenttracks/track/name').text.encode('utf-8'))
        else:
            return None


class SMachine(object):
    """Simplemagine forum poster

    Keyword arguments
    username -- login on forum
    password -- password on forum
    topic -- topic on forum

    """
    def __init__(self, username, password, topic):
        self.topic = topic
        self.regexp = compile(r'<input type="hidden" name="last_msg" value="(.*?)" />|<input type="hidden" name="seqnum" value="(.*?)" />|<li><a\sclass="button_strip_mark_unread"\shref="(.*)">')
        cookie = CookieJar()
        opener = build_opener(HTTPCookieProcessor(cookie))
        install_opener(opener)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.121 Safari/535.2"}
        send_data = urlencode({"user": username,
                               "passwrd": password,
                               "cookieneverexp": "checked"})
        urlopen(Request("http://www.forum.l2planet.ws/index.php?PHPSESSID=b25e07ab7c03cc08ee1635d4cfa3440d&action=login2", \
            send_data, headers)).read()

    def send_post(self, message):
        """Send post"""
        pr = urlopen('http://www.forum.l2planet.ws/index.php?topic=%s' % self.topic).read()
        data = findall(self.regexp, pr)
        session = parse_qsl(str(urlsplit(data[0][2]).query))[4]
        send_data = urlencode({"topic": self.topic,
                               "subject": "Re: Что у вас сейчас играет? =)",
                               "icon": "xx",
                               "from_qr": 1,
                               "notify": 0,
                               "not_approved": "",
                               "goback": 0,
                               "last_msg": data[3][1],
                                session[0]: session[1],
                               "seqnum": data[2][0],
                               "message": message,
                               "post": "Post"})
        request = Request("http://www.forum.l2planet.ws/index.php?board=23;action=post2", send_data)
        urlopen(request)


class Engine(object):
    def __init__(self, lastfm_username, api_key, forum_username,
                 forum_password, topic_id, time=30):
        """Engine

        Keyword arguments:
        lastfm_username -- last.fm username
        api_key -- key for api last.fm
        forum_username -- forum login
        forum_password -- forum password
        topic_id -- topic id(for posting)
        time -- pause in minutes. default(30)

        """
        self.time = time
        self.lastfm = LastFM(lastfm_username, api_key)
        self.forum = SMachine(forum_username, forum_password, topic_id)

    def action(self):
        """Get post text and send"""
        track = self.lastfm.get_track()
        if track:
            self.forum.send_post(track)
            logger.info(track)
        else:
            logger.warning("not playing")

    def start(self):
        """Start engine"""
        while True:
            self.action()
            sleep(60 * self.time)

if __name__ == '__main__':
    engine = Engine("name", "key", "login", "password", 16670, 30)
    engine.start()
