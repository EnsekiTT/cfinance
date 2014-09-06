# -*- coding: utf8 -*-

import urllib
import BeautifulSoup as bs
import re
import time
import random

class YahooFinance:
	def __init__(self):
		self.stocks_address = 'http://stocks.finance.yahoo.co.jp/'
		self.crawl_span_min = 0.0
		self.crawl_span_max = 1.0
		self.retry_time = 60

	def processing_stock_history_page(self,soup,stock_code):
		datalist = []
		for _tr in soup.findAll('tr'):
			td_list = _tr.findAll('td')
			if len(td_list) == 7:
				dataset = [td.string for td in td_list]
				dataset[0] = dataset[0].replace(u'年','-')
				dataset[0] = dataset[0].replace(u'月','-')
				dataset[0] = dataset[0].replace(u'日','')
				for i in range(1,7):
					dataset[i] = dataset[i].replace(',','')
				datalist.append(tuple([stock_code.split(',')[0]] + dataset))
		return datalist

	def processing_index_history_page(self,soup, stock_code):
		datalist = []
		for _tr in soup.findAll('tr'):
			td_list = _tr.findAll('td')
			if len(td_list) == 5:
				dataset = [td.string for td in td_list]
				dataset[0] = dataset[0].replace(u'年','-')
				dataset[0] = dataset[0].replace(u'月','-')
				dataset[0] = dataset[0].replace(u'日','')
				for i in range(1,4):
					dataset[i] = dataset[i].replace(',','')
				datalist.append(tuple([stock_code.split(',')[0]] + dataset))
		return datalist

	def processing_stock_list_page(self,soup):
		datalist = []
		for _td in soup.findAll('td'):
			a_list = _td.find('a')
			if a_list == None:
				continue
			link = a_list.get("href")
			link_array = link.split('=')
			if len(link_array) > 1:
				datalist = datalist + [link_array[1]]

		return datalist

	def download_stocks_lists(self):
		page = 1
		url = 'http://info.finance.yahoo.co.jp/ranking/?kd=3' + str(page)
		soup = bs.BeautifulSoup(urllib.urlopen(url))

		#count page
		tpages = soup.find('span',{"class":"rankdataPageing yjS"}).string
		pages = int(tpages.split('/')[1].replace(u'件中',''))/50 + 1

		#get data
		stocks_list = []
		for page in range(1, pages)[::-1]:
			url = 'http://info.finance.yahoo.co.jp/ranking/?kd=3&p=' + str(page)
			soup = self.download_soup(url)
			datalist = self.processing_stock_list_page(soup)
			stocks_list = stocks_list + datalist
			#Sleep
			sleeptime = random.uniform(self.crawl_span_min,self.crawl_span_max)
			time.sleep(sleeptime)
			#log
			print 'page:' + str(page) + '/' + str(pages) + ' sleep:' + str(sleeptime)
		return stocks_list

	def download_stocks_history(self, stock_code_list, function):
		done_number = 0
		for stock_code in stock_code_list:
			print 'done:' + str(done_number) + '/' + str(len(stock_code_list))
			done_number = done_number + 1
			self.download_stock_history(stock_code, function)

	def download_soup(self,url):
		for i in range(10):
			while True:
				try:
					soup = bs.BeautifulSoup(urllib.urlopen(url))
				except IOError:
					print "Error: Retry"
					time.sleep(self.retry_time)
					continue
				break
		return soup

	def download_stock_history(self, stock_code, function):
		page = 1
		url = 'http://info.finance.yahoo.co.jp/history/?code=' + stock_code + '&sy=1983&sm=1&sd=1&ey=2013&em=12&ed=10&tm=d&p=' + str(page)
		soup = bs.BeautifulSoup(urllib.urlopen(url))

		#count page
		tpages = soup.find('span',{"class":"stocksHistoryPageing yjS"})
		if tpages == None:
			pages = 2
		else:
			pages = int(tpages.string.split('/')[1].replace(u'件中',''))/50 + 1

		#get data
		new_time = time.time()
		old_time = new_time
		for page in range(1, pages)[::-1]:
			url = 'http://info.finance.yahoo.co.jp/history/?code=' + stock_code + '&sy=1983&sm=1&sd=1&ey=2013&em=12&ed=10&tm=d&p=' + str(page)
			datalist = self.processing_stock_history_page(soup, stock_code)
			soup = self.download_soup(url)
			function(datalist)
			#Sleep
			old_time = new_time
			new_time = time.time()
			sleeptime = random.uniform(self.crawl_span_min,self.crawl_span_max)
			time.sleep(sleeptime)
			#log
			print 'time:' + time.asctime() + ',stock_code:' + stock_code + ',page:' + str(page) + '/' + str(pages) + ',sleep:' + str(sleeptime) + ',span:' + str(new_time-old_time)

	def download_stocks_detail(self, stock_code):
		url = self.stocks_address + 'stocks/detail/?code=' + stock_code
		soup = self.download_soup(url)
			
		stocks_detail_dict = {}
		stocks_detail_dict['stocks_price'] = int(soup.find('td',{'class': 'stoksPrice'}).string)
		counter = 0
		for _dl in soup.findAll('dl'):
			ddTag = _dl.dd
			if ddTag == None:
				continue
			strongTag = ddTag.strong
			if strongTag == None:
				continue
			if counter == 0:
				stocks_detail_dict['last_close'] = int(strongTag.string)
			elif counter == 1:
				stocks_detail_dict['opening'] = int(strongTag.string)
			elif counter == 2:
				stocks_detail_dict['high'] = int(strongTag.string)
			elif counter == 3:
				stocks_detail_dict['low'] = int(strongTag.string)
			elif counter == 4:
				stocks_detail_dict['turnover'] = int(strongTag.string.replace(',',''))
			elif counter == 5:
				stocks_detail_dict['sales_value'] = int(strongTag.string.replace(',','')) * 1000
			elif counter == 6:
				price_movement_limit = strongTag.string.split(u"～")
				stocks_detail_dict['price_movement_low_limit'] = int(price_movement_limit[0])
				stocks_detail_dict['price_movement_high_limit'] = int(price_movement_limit[1])
			elif counter == 7:
				stocks_detail_dict['market_capitalization'] = int(strongTag.string.replace(',','')) * 1000000
			elif counter == 8:
				stocks_detail_dict['all_issued_stocks'] = int(strongTag.string.replace(',',''))
			elif counter == 9:
				stocks_detail_dict['dividend_yield'] = float(strongTag.string)
			elif counter == 10:
				stocks_detail_dict['dividend_par_stock'] = float(strongTag.string)
			elif counter == 11:
				nums = re.search("([1-9]\d*|0)(\.\d+)",strongTag.string)
				stocks_detail_dict['PER'] = float(nums.group())
			elif counter == 12:
				nums = re.search("([1-9]\d*|0)(\.\d+)",strongTag.string)
				stocks_detail_dict['PBR'] = float(nums.group())
			elif counter == 13:
				nums = re.search("([1-9]\d*|0)(\.\d+)",strongTag.string)
				stocks_detail_dict['EPS'] = float(nums.group())
			elif counter == 14:
				nums = re.search("([1-9]\d*|0)(\.\d+)",strongTag.string)
				stocks_detail_dict['BPS'] = float(nums.group())
			elif counter == 15:
				stocks_detail_dict['minimum_purchase_amount'] = int(strongTag.string.replace(',',''))
			elif counter == 16:
				stocks_detail_dict['share_unit_number'] = int(strongTag.string.replace(',',''))
			elif counter == 17:
				stocks_detail_dict['yearly_high'] = int(strongTag.string.replace(',',''))
			elif counter == 18:
				stocks_detail_dict['yearly_low'] = int(strongTag.string.replace(',',''))

			counter = counter + 1
		return stocks_detail_dict

def printdata(dataset):
	print dataset

if __name__ == '__main__':
	yf = YahooFinance()
	yf.download_stock_history('6701.t', printdata)
