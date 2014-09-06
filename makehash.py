import hashlib
import pymysql
import pymysql.cursors

class makehash:
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

	def get_stocks(self):
		select_statement = "SELECT `code`,`date` FROM `stocks`"
		self.sqlcursor.execute(select_statement)
		self.sqlconfig.commit()
		select_data = self.sqlcursor.fetchall()
		return select_data

	def set_stock_hash(self, arg_code, arg_date):
		stock_hash = hashlib.md5(arg_code + arg_date).hexdigest()
		update_statement = "UPDATE `stocks` SET `stock_hash` = '" + stock_hash + "' WHERE `stocks`.`code` = '" + arg_code + "' AND `stocks`.`date` = '" + arg_date + "' LIMIT 1 "
		self.sqlcursor.execute(update_statement)
		self.sqlconfig.commit()

if __name__ == '__main__':
	mh = makehash()
	datas = mh.get_stocks()
	for data in datas:
		mh.set_stock_hash(data[0], str(data[1]))