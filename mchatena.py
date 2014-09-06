def MCE(S,K,sigma,T,flag):
	import random
	import math
	d=[]
	kabuka=[]
	sum=0
	for i in range(0,10001):
		d.append(random.normalvariate(0,1))

	for i in range(0,10001):
		kabuka.append(math.exp(-0.5*sigma**2*T+d[i]*sigma*math.sqrt(T))*S)

	j = 0
	if flag==1:
		for i in range(0,10001):
			if kabuka[i] > K:
				sum = sum + kabuka[i] - K
		for i in range(0,10001):
			if kabuka[i]<K:
				sum = sum + K - kabuka[i]
	print sum/10000

MCE(100,95,0.1,1,True)