from os.path import isfile, join, isdir

import helper
import modules
import os
import time

# Executing start
start_time = time.time()

# Setting for the path and sample files
current_dir = os.getcwd()
sample_dir = current_dir + '/out_cont'
os.chdir(sample_dir)
folders = [f for f in os.listdir(sample_dir)]
file_names = []
for folder in folders:
    for file in os.listdir(folder):
        file_names.append(folder+'/'+file)

print('opening ' + str(len(file_names)) + ' files...')
# file_names = [file for file in os.listdir(sample_dir)]

# Model initialization.
seed = (60, 62, 64, 55, 57, 59)
model = modules.Line(seed, len(seed))

# Gets list of whole sample.
samples = []
for name in file_names:
    sample_blocks = helper.open_pickle(name).blocks
    for block in sample_blocks:
        samples += block.melody

# Training
print('fitting data...')
model.fit(samples)

# Dump melody melody_model
print('dumping data...')
os.chdir(current_dir)
model.dump_model('order_6_cnt_note.pkl')

# Print results
print("Executing time: {}".format(time.time() - start_time))
