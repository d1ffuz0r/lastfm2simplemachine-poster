#!/usr/bin/env python
# -*- coding:utf-8 -*-
__version__ = '0.0.4'

from urllib2 import urlopen, Request, build_opener,\
    install_opener, HTTPCookieProcessor
from urlparse import parse_qsl, urlsplit
from re import findall, compile, M
from cookielib import CookieJar
from urllib import urlencode
import logging
from os import path, curdir
import xml.etree.ElementTree as Tree
import sys
sys.path.append("./xmpppy.egg")
from xmpp import JID, Client, Message

logger = logging.getLogger('lastm2planet')
logger.setLevel(logging.DEBUG)
lh = logging.FileHandler('www/lastm2planet.log')
lh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
lh.setFormatter(formatter)
logger.addHandler(lh)


def send_psto(jid, password, message):
    jid = JID(jid)
    conn = Client(jid.getDomain(), debug=[])

    if not conn.connect():
        logger.error("not connect to jabber")
    if not conn.auth(jid.getNode(), password, "Lastfm2Jabber"):
        logger.error("error auth to jabber")
    try:
        conn.send(Message(to="psto@psto.net",
                          body="* bot, /mu/ // %s" % message))
    except:
        logger.error("error sending message")


def get_track(user, key):
    page = urlopen("http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&limit=1"
                   % (user, key))
    p = Tree.fromstring(page.read())

    if 'nowplaying' in p.find('recenttracks/track').attrib:
        return '{0} - {1}'.format(
            p.find('recenttracks/track/artist').text.encode('utf-8'),
            p.find('recenttracks/track/name').text.encode('utf-8')
        )
    else:
        return None


class SMachine(object):

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


def push(lastfm_username, api_key,
         forum_username, forum_password, topic_id,
         jabber_jid, jabber_pass):
    forum = SMachine(forum_username, forum_password, topic_id)
    track = get_track(lastfm_username, api_key)

    if track:
        forum.send_post(track)
        send_psto(jabber_jid, jabber_pass, track)
        logger.info(track)
    else:
        logger.warning("not playing")


if __name__ == '__main__':
    push("lastfm_login", "lastfm_key_api",
         "forum_login", "forum_password", 16670,
         "jid", "jabber_password")
