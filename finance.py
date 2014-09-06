# -*- coding: utf8 -*-

import numpy as np
import matplotlib.pyplot as plt
import pymysql
import pymysql.cursors
import YahooFinance as yf
import KabuCom as kc
import datetime
import json
import hashlib
import config
	
class CurbFinanceMySQL:
	def __init__(self):
		self.host = mysql_config['host']
		self.port = mysql_config['port']
		self.db = mysql_config['db']
		self.user = mysql_config['user']
		self.passwd = mysql_config['passwd']
		self.sqlconfig = pymysql.connect(host = self.host,
										 port = self.port,
										 unix_socket = '/tmp/mysql.sock',
										 user = self.user,
										 passwd = self.passwd,
										 db = self.db)
		self.sqlcursor = self.sqlconfig.cursor()
		self.brand_table = 'brand'
		self.stocks_table = 'stock'

	def showdb(self):
		self.sqlcursor.execute('SHOW TABLES')
		rows = self.sqlcursor.fetchall()
		print rows

	def insert_brand_init(self, arg_code, arg_name):
		u"""銘柄を保存するデータベースを初期化する。
		arg_code: 企業コード, arg_name: 企業名
		"""
		if len(self.select_brand(arg_brand)) != 0:
			return False
		insert_statement = "INSERT " + self.db + "." + self.brand_table + "(brand) VALUES(%s)"
		self.sqlcursor.execute(insert_statement, \
								(arg_brand))
		self.sqlconfig.commit()

	def insert_stock(self, arg_code, arg_date, arg_first, arg_high, arg_low, arg_close, arg_turnover, arg_fixclose):
		u"""株式情報を1つ保存する
		arg_code: 企業コード, arg_date: 日付, arg_first: 始値, arg_high: 高値, arg_low: 低値, arg_close: 終値, arg_turnover: 出来高, arg_fixclose調整後補正値
		"""
		stock_hash = hashlib.md5(arg_code + arg_date).hexdigest()
		if len(self.select_stock(stock_hash)) != 0:
			return False
		insert_statement = "INSERT " + self.db + "." + self.stocks_table + "(stock_hash, code, date, first, high, low, close, turnover, fixclose) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
		self.sqlcursor.execute(insert_statement, \
								(stock_hash, arg_code, arg_date,\
								 arg_first, arg_high, arg_low,\
								 arg_close, arg_turnover, arg_fixclose))
		self.sqlconfig.commit()

	def insert_stocks(self, stocks_list):
		insert_statement = "INSERT " + self.db + "." + self.stocks_table + "(stock_hash, code, date, first, high, low, close, turnover, fixclose) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
		for stock in stocks_list:
			stock_hash = hashlib.md5(stock[0] + stock[1]).hexdigest()
			if len(self.select_stock(stock_hash)) != 0:
				continue
			insert_tupple = (stock_hash,) + stock
			self.sqlcursor.execute(insert_statement, insert_tupple)
		self.sqlconfig.commit()

	def select_stock(self, stock_hash):
		select_statement = "SELECT 'stock_hash' FROM " + self.stocks_table + "WHERE stock_hash = '" + stock_hash + "'LIMIT 0, 5"
		self.sqlcursor.execute(select_statement)
		self.sqlconfig.commit()
		select_data = self.sqlcursor.fetchall()
		return select_data

	def write_json_campany_list(self, data):
		d = datetime.datetime.today()
		date = d.strftime('%Y%m')
		FILEOUT = str(date) + 'campany_list.json'
		f = open(FILEOUT, 'w')
		json.dump(data, f)
		f.close()

	def read_json_campany_list(self):
		d = datetime.datetime.today()
		date = d.strftime('%Y%m')
		FILEIN = str(date) + 'campany_list.json'
		try:
			f = open(FILEIN, 'r')
			data = json.load(f)
			f.close()
			return data
		except IOError:
			return False


if __name__ == '__main__':
	cf = CurbFinanceMySQL()
	yfc = yf.YahooFinance()
	campany_list = cf.read_json_campany_list()
	if campany_list == False:
		campany_list = yfc.download_stocks_lists()
		cf.write_json_campany_list(campany_list)
		print 'List downloaded'
	yfc.download_stocks_history(campany_list, cf.insert_stocks)
	