import pickle

f = open('out/Beatles_Dig_It.mid.pkl','rb')
a = pickle.load(f)
a.print_blocks()