"""
Project Cottoncandy

wav2tensor.py

Author : Byunghyun ban
Institute : Cheesecake Studio

Latest Modification : 2016. 10. 20.

"""
import os
import preproc

test = preproc.Preproc()

tensor = open('single_tensor.csv', 'w')


def normalize(vector):
	max = 0
	for i in range(len(vector)):
		max += float(vector[i])
	for i in range(len(vector)):
		vector[i] = float(vector[i])/max  # Normalizing
	return vector


count = 0
for filename in os.listdir('singlewav/'):
	if count != 0:
		tensor.write('\n')
	if filename.endswith('.wav'):
        	test.set_file('singlewav/' + filename)
        	test.decompose(0)
        	test.make_tuple()
        	vector = test.result[0]
        	norm = normalize(vector)
		for el in norm:
			tensor.write(str(el) + ',')
		
		rt = [0]*12
		for i in range(88):
			rt[i%12] = int(filename[i]) | rt[i%12]
			
		for j in range(11):
			tensor.write(str(rt[j]) + ',')
		tensor.write(str(rt[-1]))
		count += 1
	
tensor.close()






