# -*- coding: utf8 -*-
class KabuCom:
	def __init__(self):
		#Tax
		self.consumption_tax = 1.05

		#Contracted Price
		self.contracted_price_rate = 0.0009
		self.contracted_price_offset = 90.0
		self.contracted_price_limit = 3874.0

	def calc_fee(self, contracted_price):
		fee = int(contracted_price * self.contracted_price_rate + self.contracted_price_offset)
		fee = fee * self.consumption_tax
		return min(fee, self.contracted_price_limit)


if __name__ == '__main__':
	kc = KabuCom()
	print kc.calc_fee(10000)