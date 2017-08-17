import os
import random
from time import strftime, gmtime

from music21 import stream, midi, instrument, meter
from music21.stream import Part

import helper
import helper_spring

owd = os.getcwd()

song = stream.Score()
ts0 = meter.TimeSignature('4/4')
song.append(ts0)

melody_part = Part()
bass_part = Part()
banju_part = Part()

os.chdir(owd)
melody_model = helper.open_pickle('order_4_cnt_note.pkl')
chord_model = helper.open_pickle('7_state_chord_bach_4.pkl')
bass_model = helper.open_pickle('order_4_cnt_note_bass.pkl')

# 오더
order = 4

# 블록 사이즈
block_size = 16

# 레벨1 의 평균 음 높이
ref_avg_pitch = 0

# [음높이, 멜로디 심볼, 변주?]
input = [[1, 'A', False], [3, 'B', False], [1, 'A', True], [3, 'B', False], [4, 'C', False], [3, 'B', False], [1, 'D', False]]

# [음높이, 멜로디 심볼, 변주?]
input_score = [[3, 'A', False], [4, 'B', False], [3, 'A', True], [4, 'B', False], [5, 'C', False], [4, 'B', False], [3, 'D', False]]


# [음높이, 멜로디 심볼, 시퀀스, 베이스, 반주]
melody_records = []

# [스코어 개수, 멜로디 심볼, 시퀀스, 베이스, 반주, 서브스코어]
melody_records_score = []

max_score = 3
for block in input_score:
    max_score = max(max_score, block[0])
sub_score_parts = []
for i in range(max_score - 3):
    score_part = Part()
    sub_score_parts.append(score_part)

instruments = [instrument.Violin(), instrument.Vibraphone(), instrument.ChurchBells(), instrument.Flute(), instrument.Harmonica(),
               instrument.Piano()]

chord_prog = helper.translate_to_chord(chord_model.random_gen(length=4+4*len(input)))[4:]


def get_melody_record_from_symbol(symbol):
    for record in melody_records:
        if record["melody_symbol"] == symbol:
            return record
    return None


def get_melody_record_from_symbol_score(symbol):
    for record in melody_records_score:
        if record["melody_symbol"] == symbol:
            return record
    return None


def make_block(i, block_info):
    global ref_avg_pitch
    global block_size
    global order
    global melody_records

    pitch_level = block_info[0]
    melody_symbol = block_info[1]
    is_ornament = block_info[2]

    print('making', melody_symbol)

    if not melody_records:  # first case
        melody_sequence = helper_spring.generate_block(order=order, prev_line=None, model=melody_model, length=block_size)
        bass_sequence = helper_spring.generate_block(order=order, prev_line=None, model=bass_model, length=block_size)
        ref_avg_pitch = sum(melody_sequence) / float(len(melody_sequence))

    else:
        record = get_melody_record_from_symbol(melody_symbol)
        if record:
            return
        prev_melody_record = get_melody_record_from_symbol(chr(ord(melody_symbol) - 1))
        melody_sequence = helper_spring.generate_block_with_pitch(order=order, prev_line=prev_melody_record["sequence"],
                                                                  model=melody_model, length=block_size,
                                                                pitch_level=pitch_level, ref_avg_pitch=ref_avg_pitch)
        bass_sequence = helper_spring.generate_block(order=order, prev_line=prev_melody_record["bass"], model=bass_model, length=block_size)

    chord = chord_prog[4 * i: 4 * i + 4]
    melody_records.append({"pitch_level": pitch_level, "melody_symbol": melody_symbol,
                           "sequence": melody_sequence, "bass": bass_sequence, "banju": helper.get_file_banju_16bit(owd)})


def make_block_score(i, block_info):
    global ref_avg_pitch
    global block_size
    global order
    global melody_records

    score_num = block_info[0]
    melody_symbol = block_info[1]
    is_ornament = block_info[2]

    sub_score_num = score_num - 3

    print(melody_symbol)

    if not melody_records:  # first case
        melody_sequence = helper_spring.generate_block(order=order, prev_line=None, model=melody_model, length=block_size)
        bass_sequence = helper_spring.generate_block(order=order, prev_line=None, model=bass_model, length=block_size)
    else:
        record = get_melody_record_from_symbol(melody_symbol)
        if record:
            return
        prev_melody_record = get_melody_record_from_symbol(chr(ord(melody_symbol) - 1))
        melody_sequence = helper_spring.generate_block(order=order, prev_line=prev_melody_record["sequence"],
                                                                  model=melody_model, length=block_size)
        bass_sequence = helper_spring.generate_block(order=order, prev_line=prev_melody_record["bass"], model=bass_model, length=block_size)

    sub_score = []
    for _ in range(sub_score_num):
        seq = helper_spring.generate_subscore(offset=4, melody_sequence=melody_sequence, model=melody_model, length=block_size)
        sub_score.append(seq)
        print('subscore', seq)

    melody_records_score.append({"score_num": score_num, "melody_symbol": melody_symbol,
                            "sequence": melody_sequence, "bass": bass_sequence, "banju": helper.get_file_banju_16bit(owd),
                            "sub_score":sub_score})


def generate_song():
    global song
    global melody_part
    global bass_part
    global banju_part

    for i, block in enumerate(input):
        os.chdir(owd)
        record = get_melody_record_from_symbol(block[1])
        index = ord(block[1]) - ord('A')
        chord = chord_prog[4*index:4*(index+1)]
        melody = helper.fit_to_chord(record["sequence"], chord)
        bass = helper.fit_to_chord(record["bass"], chord)
        print(chord)
        print(record["sequence"])
        print(melody)
        print(record["bass"])
        print(bass)
        mp = helper.export_to_part(melody, instrument.Piano())
        bp = helper.export_to_part(bass, instrument.AcousticBass())
        banp = helper.make_banju_16bit_with_file(chord, len(melody), owd, record["banju"])
        mp.shiftElements(block_size * i)
        bp.shiftElements(block_size * i)
        banp.shiftElements(block_size * i)
        # melody_part.offset = block_size * i
        # bass_part.offset = block_size * i
        # banju_part.offset = block_size *i
        for note in mp.notes:
            melody_part.insert(note.offset, note)
        for note in bp.notes:
            bass_part.insert(note.offset, note)
        for note in banp.notes:
            banju_part.insert(note.offset, note)


def generate_song_score():
    global song
    global melody_part
    global bass_part
    global banju_part
    global sub_score_parts

    for i, block in enumerate(input_score):
        os.chdir(owd)
        record = get_melody_record_from_symbol_score(block[1])
        index = ord(block[1]) - ord('A')
        chord = chord_prog[4*index:4*(index+1)]
        melody = helper.fit_to_chord(record["sequence"], chord)
        bass = helper.fit_to_chord(record["bass"], chord)
        print(block[1])
        print('Chord', chord)
        print('Sequence', record["sequence"])
        print('fit Sequ', melody)
        print('Bassline', record["bass"])
        print('fit bass', bass)
        mp = helper.export_to_part(melody, instrument.Piano())
        bp = helper.export_to_part(bass, instrument.AcousticBass())
        banp = helper.make_banju_16bit_with_file(chord, len(melody), owd, record["banju"])
        mp.shiftElements(block_size * i)
        bp.shiftElements(block_size * i)
        banp.shiftElements(block_size * i)

        for j, score in enumerate(record["sub_score"]):
            inst = random.choice(instruments)
            print("sub score", i, inst)
            score_fitted = helper.fit_to_chord(score, chord)
            print('score is', score_fitted)
            sp = helper.export_to_part(score_fitted, instrument.Piano())
            sp.shiftElements(block_size * i)
            # sub_score_parts[i].insert(block_size*i, inst)
            for note in sp.notes:
                sub_score_parts[j].insert(note.offset, note)
                # print(note.offset)
        # melody_part.offset = block_size * i
        # bass_part.offset = block_size * i
        # banju_part.offset = block_size *i
        for note in mp.notes:
            melody_part.insert(note.offset, note)
        for note in bp.notes:
            bass_part.insert(note.offset, note)
        for note in banp.notes:
            note.volume.velocity = 60
            banju_part.insert(note.offset, note)
            # print(note.volume)

def generate_song_p():
    global song
    i = 0
    os.chdir(owd)
    record = get_melody_record_from_symbol(block[1])
    chord = chord_prog[4*i:4*(i+1)]
    melody = helper.fit_to_chord(record["sequence"], chord)
    bass = helper.fit_to_chord(record["bass"], chord)
    print(chord)
    print(record["sequence"])
    print(melody)
    print(record["bass"])
    print(bass)
    song.insert(block_size * i, helper.export_to_part(melody, instrument.Piano()))
    song.insert(block_size * i, helper.export_to_part(bass, instrument.AcousticBass()))
    song.insert(block_size * i, helper.make_banju_16bit(chord, len(melody)))
    return song


for i, block in enumerate(input_score):
    make_block_score(i, block)

generate_song_score()

melody_part.insert(0, instrument.Piano())
bass_part.insert(0, instrument.AcousticBass())
banju_part.insert(0, instrument.AcousticGuitar())
song.insert(0, melody_part)
song.insert(0, bass_part)
song.insert(0, banju_part)
for part in sub_score_parts:
    part.insert(0, random.choice(instruments))
    song.insert(0, part)

song.show('text')


os.chdir(owd)
mf = midi.translate.streamToMidiFile(song)
mf.open('out_midi/out' + strftime("%Y%m%d%H%M%S", gmtime()) + '.midi', 'wb')
mf.write()
mf.close()

# play
# helper.play_stream(s)
