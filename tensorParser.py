"""
Project Cottoncandy

tensorParser.py

Author : Byunghyun ban
Institute : Cheesecake Studio

Latest Modification : 2016. 10. 24.

"""


tensor = open('double_tensor.csv', 'r')
parsed = open('parsed_double_tensor.csv', 'w')



for line in tensor:
	splits = line.strip().split(',')
	name = splits[-1].strip()
	for el in splits[:-1]:
		parsed.write(el + ',')
	if len(name) == 0:
		continue

	new = []
	for el in name:
		if el in ['0', '1', 0, 1]:
			new.append(el)

	newname = []
	for i in range(88-len(new)):
		newname.append(0)
	for el in new:
		newname.append(el)
		

	for el in newname:
		parsed.write(str(el) + ',')
	parsed.write('\n')

tensor.close()
parsed.close()
	
