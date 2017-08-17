from os import listdir
from os.path import isfile

import _pickle
import dill as dill
from helper import *
from modules import Chord

# Setting for the path and sample files
owd = os.getcwd()
sample_dir = '/home/bhban/cheesecake/kimchi/bach_out/'
os.chdir(sample_dir)
# file_names = [file for file in os.listdir(sample_dir)]
files = []

var_list = []

print('getting var list')

if isfile(sample_dir):
    files.append(sample_dir)
else:
    files = [f for f in listdir(sample_dir) ]

while files:
    file = files.pop(0)
    if not isfile(file):
        files.extend([file + '/' + f for f in listdir(file) ])
        continue
    elif isfile(file):
        if '.txt' not in file:
            continue
        print(file)
        variant_list_midi(file, var_list)


# Model initialization.
num_states = 7
labels = ('1', '2', '3', '4', '5', '6', '7')
model = Chord(num_states, labels, 4, var_list)

samples=[]

print('getting samples')

if isfile(sample_dir):
    files.append(sample_dir)
else:
    files = [f for f in listdir(sample_dir)]

while files:
    file = files.pop(0)
    if not isfile(file):
        files.extend([file + '/' + f for f in listdir(file) ])
        continue
    elif isfile(file):
        if '.txt' not in file:
            continue
        samples += text_to_sample_midi(file)

print('fitting')

# Training
model.fit(samples)

os.chdir(owd)
# with open('7_state_chord_1.pkl', 'wb') as fp:
#     dill.dump(melody_model, fp)
    # dill.load(fp)

# import adwaita

f = open('7_state_chord_bach_4.pkl', 'wb')
_pickle.dump(model, f, protocol=2)
# pickle.dump(melody_model, f)

# Print results
print(model.transmat_)
print(translate_to_chord(model.random_gen()))
