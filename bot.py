#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 
#  bot.py
#  lastfm2simplemachine poster
#  
#  Created by d1ffuz0r on 2011-10-04.
# 

from urllib2 import urlopen, Request, build_opener, install_opener, HTTPCookieProcessor
from urlparse import parse_qsl, urlsplit
from re import findall, compile, M
from cookielib import CookieJar
from urllib import urlencode
from time import sleep

class LastFM(object):
	def __init__(self, user, key):
		self.user = user
		self.key = key
		self.regexp = compile(r'<track\snowplaying="true">.\n............<artist.*>(.*?)</artist>\n<name>(.*?)</name>', M)
	
	def get_track(self):
		track_pre = urlopen('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=&limit=1' % (self.user, self.key)).read()
		try:
			track = findall(self.regexp, track_pre)[0]
			return '%s - %s' %(track[0], track[1])
		except:
			return None

class SMachine(object):
	def __init__(self, username, password, topic):
		self.topic = topic
		self.regexp = compile(r'<input type="hidden" name="last_msg" value="(.*?)" />|<input type="hidden" name="seqnum" value="(.*?)" />|<li><a\sclass="button_strip_mark_unread"\shref="(.*)">')
		cookie = CookieJar()
		opener = build_opener(HTTPCookieProcessor(cookie))
		install_opener(opener) 
		headers = {"User-Agent": "Mozilla/4.0 (compatible; MSIE 7; WindowsNT)"} 
		send_data = urlencode({"user": username,
							   "passwrd": password,
							   "cookieneverexp": "checked"})
		urlopen(Request("http://www.forum.forumname.ws/index.php?PHPSESSID=b25e07ab7c03cc08ee1635d4cfa3440d&action=login2", send_data, headers)).read()
		
	def send_post(self, message):
		pr = urlopen('http://www.forum.forumname.ws/index.php?topic=%s' %self.topic).read()
		data = findall(self.regexp, pr)
		session = parse_qsl(str(urlsplit(data[0][2]).query))[4]
		send_data = urlencode({"topic": self.topic,
							   "subject": "Re: Что у вас сейчас играет? =)",
							   "icon": "xx",
							   "from_qr": 1,
							   "notify": 0,
							   "not_approved": "",
							   "goback": 1,
							   "last_msg": data[3][1],
							    session[0]: session[1],
							   "seqnum": data[2][0],
							   "message": message})
		request = Request("http://www.forum.forumname.ws/index.php?board=11;action=post2", send_data)
		urlopen(request)
		
class Engine(object):
	def __init__(self, lastfm_username, lastfm_apikey, forum_username, forum_password, topic_id, time):
		"""
		lastfm_username: last.fm username
		lastfm_aplikey: last.fm apikey
		forum_username: forum login
		forum_password: forum password
		topic_id: topic id(for posting)
		time: pause(in minutes)
		"""
		self.time = time
		self.lastfm = LastFM(lastfm_username, lastfm_apikey)
 		self.forum = SMachine(forum_username,forum_password,topic_id)
		
	def action(self):
		track = self.lastfm.get_track()
		if track:
			print track
			self.forum.send_post(track)
		else:
			print "error"
		
	def start(self):
		while True:
			self.action()
			sleep(60*self.time)
		
if __name__ == '__main__':
	engine = Engine("name","key", "login", "password", 16670, 30)
	engine.start()
	