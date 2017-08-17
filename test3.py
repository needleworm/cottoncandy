import os
from time import strftime, gmtime

from music21 import stream, midi, instrument, environment

import helper

environment.set('musicxmlPath', '/usr/bin/musescore')

owd = os.getcwd()

s = stream.Score()
s_orn = stream.Score()

os.chdir(owd)
model = helper.open_pickle('order_4_cnt_note.pkl')
num_list = model.random_gen(length=100)
print(len(num_list))

os.chdir(owd)
model_bass = helper.open_pickle('order_4_cnt_note_bass.pkl')
num_list_bass = model_bass.random_gen(length=100)
print(len(num_list_bass))

# banju
model2 = helper.open_pickle('7_state_chord.pkl')
chord_prog = helper.translate_to_chord(model2.random_gen(length=32))
# chord_prog = ['C', 'G', 'Am', 'F', 'C', 'G', 'F', 'C', 'C', 'G', 'Am', 'F', 'C','G', 'G', 'Am', 'F', 'C', 'G', 'F',
#               'C', 'C', 'G', 'Am', 'F', 'C']

new_num_list = helper.fit_to_chord(num_list, chord_prog)
new_num_list_bass = helper.fit_to_chord(num_list_bass, chord_prog)

print('chord is  ', chord_prog)

print('main line ', num_list)
print('main tran ', new_num_list)

print('bass line ', num_list_bass)
print('bass tran ', new_num_list_bass)

# melody
banju = helper.make_banju_16bit(chord_prog, len(num_list))
s.insert(104, banju)
s_orn.insert(banju)

main_line = helper.export_to_part(new_num_list, instrument.Piano())
main_line_orn = helper.export_to_part_with_ex(new_num_list, instrument.Piano())
s.insert(104, main_line)
s_orn.insert(0, main_line_orn)

bass_line = helper.export_to_part(new_num_list_bass, instrument.AcousticBass())
s.insert(24, bass_line)
s_orn.insert(0, bass_line)

s.show('text')

# save to midi
os.chdir(owd)
mf = midi.translate.streamToMidiFile(s)
# # me1 = midi.MidiEvent(mf.tracks[0])
# # me1.type = 'PROGRAM_CHANGE'
# # me1.data = 25
# mf2 = midi.MidiFile()
# mf2.open('/home/bhban/cheesecake/midimagic/midi_130000/B/B/Beatles_And_I_Love_Her.mid','rb')
# # mf2.read()
# print(mf2.tracks[1])
# print(mf.tracks[0])
mf.open('out_midi/out' + strftime("%Y%m%d%H%M%S", gmtime()) + '.midi', 'wb')
mf.write()
# print(mf)
mf.close()


os.chdir(owd)
mf = midi.translate.streamToMidiFile(s_orn)
# # me1 = midi.MidiEvent(mf.tracks[0])
# # me1.type = 'PROGRAM_CHANGE'
# # me1.data = 25
# mf2 = midi.MidiFile()
# mf2.open('/home/bhban/cheesecake/midimagic/midi_130000/B/B/Beatles_And_I_Love_Her.mid','rb')
# # mf2.read()
# print(mf2.tracks[1])
# print(mf.tracks[0])
mf.open('out_midi/out' + strftime("%Y%m%d%H%M%S", gmtime()) + '_orn.midi', 'wb')
mf.write()
# print(mf)
mf.close()
# play
# helper.play_stream(s)
