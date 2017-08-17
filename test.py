from helper import *
from modules import Chord

# Setting for the path and sample files
owd = os.getcwd()
sample_dir = os.getcwd() + '/samples'
os.chdir(sample_dir)
file_names = [file for file in os.listdir(sample_dir)]

# Gets the list of every possible variant in the samples.
var_list = []
for name in file_names:
    if 'txt' not in name:
        continue
    variant_list(name, var_list)

# Model initialization.
num_states = 7
labels = ('1', '2', '3', '4', '5', '6', '7')
model = Chord(num_states, labels, 4, var_list)

# Gets list of whole sample.
samples = []
for name in file_names:
    if 'txt' not in name:
        continue
    samples += text_to_sample(name)

# Training
model.fit(samples)

os.chdir(owd)
f = open('7_state_chord_midi.pkl', 'wb')
pickle.dump(model, f)

# Print results
print(model.transmat_)
print(translate_to_chord(model.random_gen()))
