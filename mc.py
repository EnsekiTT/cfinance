import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

def MCE(S, K, sigma, T, flag):
	norm = stats.norm.rvs(0,1,size=10000)
	stock_price = [np.exp(-0.5*sigma**2*T+norm[normi]*sigma*np.sqrt(T))*S for normi in range(10000)]
	if flag==True:
		filterd_stock_price = filter(lambda x: x>K, stock_price)
		sum_stock_price = reduce(lambda a,b: a+b-K, filterd_stock_price)
	else:
		filterd_stock_price = filter(lambda x: x<K, stock_price)
		sum_stock_price = reduce(lambda a,b: a-b+K, filterd_stock_price)
	return sum_stock_price/10000


print MCE(10000.0,9500.0,0.1,1.0,True)
