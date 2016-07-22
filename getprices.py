#!/usr/bin/python

import datetime
#from datetime import date
import httplib
import json
import pymysql.cursors

use_proxy = 1

def getHost(url):
	if url.startswith('http://') or url.startswith('https://'):
		pos = url.find(':')
		pos2 = url.find('/', pos+3)
		hostname = url[pos+3:pos2]
		return hostname
	else:
		return ""

def getUrlPath(url):
	if len(url) <= 5:
		return ""

	pos = url.find('/', 10)
	if pos >= 10:
		return url[pos:]
	else:
		return ""

def getOrders(url):
	if len(url) <= 10:
		return ""

	hostname = getHost(url)
	path = getUrlPath(url)
	if len(hostname) <= 0 or len(path) <= 0:
		return ""

	#print hostname
	#print path

        if use_proxy:
            conn = httplib.HTTPSConnection('168.219.61.252',8080)
        else:
            conn = httplib.HTTPSConnection(hostname)
	if not conn:
		return ""

        if use_proxy:
            conn.set_tunnel(hostname, 443)
            conn.request("GET", url)
        else:
            conn.request("GET", path)

	result = conn.getresponse()
	response = result.read()
	conn.close()
	return response

def getOrdersKorbit():
	url = 'https://api.korbit.co.kr/v1/orderbook'
	res = getOrders(url)
	if len(res) <= 0:
		return []
	js = json.loads(res)
	count = 2
	orders = []
	for i in range(0, count):
		bid = js['bids'][i]
		ask = js['asks'][i]
		#print bid[0], bid[1] #price, amount
		#print ask[0], ask[1] #price, amount
		orders.append([i+1, float(bid[0]), float(bid[1]), float(ask[0]), float(ask[1])])
	return orders

def getOrdersBithumb():
	url = 'https://api.bithumb.com/public/orderbook'
	res = getOrders(url)
	if len(res) <= 0:
		return []
	js = json.loads(res)
	data = js['data']
	count = 2
	orders = []
	for i in range(0, count):
		bid = data['bids'][i]
		ask = data['asks'][i]
		#print bid['price'], bid['quantity']
		#print ask['price'], ask['quantity']
		orders.append([i+1, float(bid['price']), float(bid['quantity']), float(ask['price']), float(ask['quantity'])])
	return orders

def insertOrders(market, now, orders):
	'''
	CREATE TABLE `prices` (
		`market` VARCHAR(10) NOT NULL,
		`date` DATETIME NOT NULL,
		`seq` SMALLINT(6) NOT NULL,
		`bid` FLOAT NOT NULL,
		`bid_amount` FLOAT NOT NULL,
		`ask` FLOAT NOT NULL,
		`ask_amount` FLOAT NOT NULL
	)
	COLLATE='utf8_general_ci'
	ENGINE=InnoDB
	;
	'''
	conn = pymysql.connect(host='localhost',
                             user='btcuser',
                             password='btcpassword',
                             db='btc',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


	try:
		with conn.cursor() as cursor:
			sql = "INSERT INTO `prices` (`market`, `date`, `seq`, `bid`, `bid_amount`, `ask`, `ask_amount`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
			for order in orders:
				print order
				cursor.execute(sql, (market, now, order[0], order[1], order[2], order[3], order[4]))

		conn.commit()
	finally:
		conn.close()

#main

now = datetime.datetime.now()
#print now.date()
#print now.time()
#print getOrdersKorbit()
#print getOrdersBithumb()

korbitOrder = getOrdersKorbit()
bithumbOrder = getOrdersBithumb()

insertOrders('korbit', now, korbitOrder)
insertOrders('bithumb', now, bithumbOrder)

