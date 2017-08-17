"""Helper functions for processing text files of chord progression

helper.py

Author: Yuneui Jeong @ Cheesecake Studio
        Minsu Jang @ Cheesecake Studio
Final Update: Jan 20th, 2017

"""
import os
import pickle
import random

import _pickle
from music21 import stream, note, midi, harmony, pitch, instrument, expressions

vocab_pitch = {'C': 0, 'D': 1, 'E': 2, 'F': 2.5, 'G': 3.5, 'A': 4.5, 'B': 5.5, '#': 0.5, 'b': -0.5}
vocab_value = {0.0: 'C', 1.0: 'D', 2.0: 'E', 2.5: 'F', 3.5: 'G', 4.5: 'A', 5.5: 'B'}
vocab_interval = {0.0: '1', 1.0: '2', 2.0: '3', 2.5: '4', 3.5: '5', 4.5: '6', 5.5: '7'}

# Print transposed samples?
is_print_samples = False


def shift_pitch(pitch, interval, mode='#'):
    """Shifts a pitch with a given interval.

    Args:
        pitch: Previous pitch.
        interval: Interval between previous pitch and resulting pitch.
        mode: Selects whether the output will be represented with '#' or 'b'

    Returns:
        Shifted pitch.
    """
    assert interval % 0.5 == 0.0
    assert mode == '#' or mode == 'b'

    value = vocab_pitch[pitch[0]]
    if len(pitch) == 2:
        value += vocab_pitch[pitch[1]]

    new_value = (value + interval) % 6.0
    if new_value in vocab_value:
        result = vocab_value[new_value]
    else:
        if mode == '#':
            result = vocab_value[new_value - 0.5]
        else:
            result = vocab_value[new_value + 0.5]
        result += mode

    return result


def calc_interval(lhs, rhs):
    """Calculates the interval length between two pitches.

    Args:
        lhs: A pitch name.
        rhs: A pitch name.

    Returns:
        The length of interval, which is a multiple of 0.5.
    """
    lhs_value = vocab_pitch[lhs[0]]
    if len(lhs) == 2:
        lhs_value += vocab_pitch[lhs[1]]

    rhs_value = vocab_pitch[rhs[0]]
    if len(rhs) == 2:
        rhs_value += vocab_pitch[rhs[1]]

    return rhs_value - lhs_value


def transpose(chords, prev_key, res_key):
    """Transposes the key of a chord progression to a target key.

    Args:
        chords: List of a chord progression.
        prev_key: Original key of the chords.
        res_key: Resulting key.

    Returns:
        Transposed chord progression.

    Notes:
        Supports transposition between major keys only.
    """
    result = []
    interval = calc_interval(prev_key, res_key)

    for chord in chords:
        if not chord:
            continue

        if len(chord) == 1 or (chord[1] != '#' and chord[1] != 'b'):
            name_index = 1
            if chord[0] == 'F':
                mode = 'b'
            else:
                mode = '#'
        else:
            name_index = 2
            mode = chord[1]

        result_chord = shift_pitch(chord[:name_index], interval, mode) + chord[name_index:]
        result.append(result_chord)

    if is_print_samples:
        print('origin : ' + str(chords))
        print('output : ' + str(result))
        print()

    return result


def set_print_samples(bool):
    global is_print_samples
    is_print_samples = bool


def make_interval_chord(chords, key):
    """Represents a chord progression using interval chord notation.

    Args:
        chords: List of a chord progression.
        key: Key of the chords.

    Returns:
        Interval chord notation of the chords.
    """
    result = []
    c_transposed = transpose(chords, key, 'C')

    for chord in c_transposed:
        if len(chord) == 1 or (chord[1] != '#' and chord[1] != 'b'):
            name_index = 1
            if chord[0] == 'F':
                mode = 'b'
            else:
                mode = '#'
        else:
            name_index = 2
            mode = chord[1]

        interval = calc_interval('C', chord[:name_index])

        if interval in vocab_value:
            result_chord = vocab_interval[interval]
        else:
            if mode == '#':
                interval -= 0.5
            else:
                interval += 0.5
            result_chord = vocab_interval[interval] + mode

        result.append(result_chord + chord[name_index:])

    return result


def make_interval_chord_midi(chords, key):
    """Represents a chord progression using interval chord notation.

    Args:
        chords: List of a chord progression.
        key: Key of the chords.

    Returns:
        Interval chord notation of the chords.
    """
    result = []
    c_transposed = transpose(chords, key, 'C')

    for chord in c_transposed:
        if chord[0] == 'H':
            result.append('-1')
            continue

        if len(chord) == 1 or (chord[1] != '#' and chord[1] != 'b'):
            name_index = 1
            if chord[0] == 'F':
                mode = 'b'
            else:
                mode = '#'
        else:
            name_index = 2
            mode = chord[1]

        interval = calc_interval('C', chord[:name_index])

        if interval in vocab_value:
            result_chord = vocab_interval[interval]
        else:
            if mode == '#':
                interval -= 0.5
            else:
                interval += 0.5
            result_chord = vocab_interval[interval] + mode

        result.append(result_chord + chord[name_index:])

    return result


def open_pickle(pkl_name):
    """Gets a pickle file

    Args:
        pkl_name: Name of a pickle file.

    Returns:
        List of variants.
    """
    pkl_file = open(pkl_name, 'rb')
    model = _pickle.load(pkl_file)
    return model


def text_to_sample(input_name):
    """Reads a text file and turns it into a chord progression with interval chord notation.

    Args:
        input_name: Name of a text file.

    Returns:
        Interval chord notation of the chords.
    """
    assert 'txt' in input_name

    input_file = open(input_name, 'r')
    if input_name[1] == 'b' or input_name[1] == '#':
        key = input_name[0:2]
    else:
        key = input_name[0]
    sample = []

    for line in input_file:
        sample += line.strip().split(',')

    return make_interval_chord(sample, key)


def text_to_sample_midi(input_name):
    """Reads a text file and turns it into a chord progression with interval chord notation.

    Args:
        input_name: Name of a text file.

    Returns:
        Interval chord notation of the chords.
    """
    assert 'txt' in input_name

    input_file = open(input_name, 'r')
    # if input_name[1] == 'b' or input_name[1] == '#':
    #     key = input_name[0:2]
    # else:
    #     key = input_name[0]
    key = 'C'
    sample = []

    for line in input_file:
        sample += line.strip().split(',')

    return make_interval_chord(sample, key)


def variant_list_midi(input_name, var_list):
    """Reads text files of chord progression and stores all possible variants on a list.

    Args:
        input_name: Name of a text file.
        var_list: List of variants.

    Yields:
        A list of variants.
    """
    chord_prog = text_to_sample_midi(input_name)

    for chord in chord_prog:
        if len(chord) == 1 and '' not in var_list:
            var_list.append('')
        else:
            trait = chord[1:]
            if trait not in var_list:
                var_list.append(trait)

    return var_list



def variant_list(input_name, var_list):
    """Reads text files of chord progression and stores all possible variants on a list.

    Args:
        input_name: Name of a text file.
        var_list: List of variants.

    Yields:
        A list of variants.
    """
    chord_prog = text_to_sample(input_name)

    for chord in chord_prog:
        if len(chord) == 1 and '' not in var_list:
            var_list.append('')
        else:
            trait = chord[1:]
            if trait not in var_list:
                var_list.append(trait)

    return var_list


def translate_to_chord(state_prog):
    """Translate state (numbered) data to chord data

    Args:
        state_prog: A chord progression starts with a number

    Returns:
        Translated chord progression
    """
    list = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    result = []
    for state in state_prog:
        word = ""
        for i, p in enumerate(state):
            if i == 0:
                word += list[int(p) - 1]
            else:
                word += p
        result.append(word)

    return result


def make_banju_8bit(chord_prog, qlen):
    """Maku banju from chord progression

    Args:
        chord_prog: A chord progression

    Returns:
        Banju made from chord_progression with patterns from random file of /banju
    """
    part = stream.Part()

    print(chord_prog)

    # Setting for the path and sample files
    current_dir = os.getcwd()
    sample_dir = current_dir + '/banju'
    os.chdir(sample_dir)
    file_names = [file for file in os.listdir(sample_dir)]
    # file_to_open = random.choice(file_names)
    file_to_open = '8bit/condense_001.txt'
    file = open(file_to_open, 'r', encoding="utf-8")

    file2 = file.readline().replace(' ', '')
    banju_list = [int(f) for f in file2.split(',')]

    on_list = []

    print(banju_list)

    for i, banju in enumerate(banju_list):
        if (banju == -1):
            on_list.append(-1)
            continue
        isOn = [1 if 8 & banju else 0, 1 if 4 & banju else 0, 1 if 2 & banju else 0, 1 if 1 & banju else 0]
        on_list.append(isOn)

    print(on_list)

    for i, chord in enumerate(chord_prog):  # C, Dm, G7, etc....
        offset = i * 4
        if i > qlen / 4:
            break
        c = harmony.ChordSymbol(chord)
        previous = []
        for j, is_on in enumerate(on_list):  # [1, 0, 0, 1]
            if is_on == -1:
                for note_temp in previous:
                    note_temp.quarterLength += 0.5
            else:
                previous.clear()
                for k, on in enumerate(is_on):
                    if on:
                        if k < len(c.pitches):
                            note_temp = note.Note(c.pitches[k], quarterLength=0.5)
                            part.insert(offset + j * 0.5, note_temp)
                            previous.append(note_temp)
                        elif k == 3 and k == len(c.pitches):
                            note_temp = note.Note(c.pitches[0], quarterLength=0.5)
                            note_temp.octave += 1
                            part.insert(offset + j * 0.5, note_temp)
                            previous.append(note_temp)

    part.show('text', addEndTimes=True)
    return part


def make_banju_16bit(chord_prog, qlen, owd):
    """Maku banju from chord progression

    Args:
        chord_prog: A chord progression

    Returns:
        Banju made from chord_progression with patterns from random file of /banju
    """
    part = stream.Part()

    #print(chord_prog)

    # Setting for the path and sample files
    os.chdir(owd)
    current_dir = os.getcwd()
    sample_dir = current_dir + '/banju/16bit'
    os.chdir(sample_dir)
    file_names = [file for file in os.listdir(sample_dir) if file != ".DS_Store"]
    file_to_open = random.choice(file_names)
    # file_to_open = '16bit/chord_001.txt'\
    file = open(file_to_open, 'r', encoding="utf-8")

    file2 = file.read().replace(' ', '')
    banju_list = [int(f) for f in file2.split(',')]
# Done
    on_list = []

    #print('banju is  ', banju_list)

    for i, banju in enumerate(banju_list):
        if (banju == -1):
            on_list.append(-1)
            continue
        isOn = [1 if 8 & banju else 0, 1 if 4 & banju else 0, 1 if 2 & banju else 0, 1 if 1 & banju else 0]
        on_list.append(isOn)

    print('banju is  ', on_list)

    for i, chord in enumerate(chord_prog):  # C, Dm, G7, etc....
        offset = i * 4
        if i > qlen / 4:
            break
        c = harmony.ChordSymbol(chord)
        previous = []
        for j, is_on in enumerate(on_list):  # [1, 0, 0, 1]
            if is_on == -1:
                for note_temp in previous:
                    note_temp.quarterLength += 0.25
            else:
                previous.clear()
                for k, on in enumerate(is_on):
                    if on:
                        if k < len(c.pitches):
                            note_temp = note.Note(c.pitches[k], quarterLength=0.25)
                            part.insert(offset + j * 0.25, note_temp)
                            previous.append(note_temp)
                        elif k == 3 and k == len(c.pitches):
                            note_temp = note.Note(c.pitches[0], quarterLength=0.25)
                            note_temp.octave += 1
                            part.insert(offset + j * 0.25, note_temp)
                            previous.append(note_temp)

    part.insert(instrument.AcousticGuitar())
    # part.show('text', addEndTimes=True)
    return part


def make_banju_16bit_with_file(chord_prog, qlen, owd, file_to_open):
    """Maku banju from chord progression

    Args:
        chord_prog: A chord progression

    Returns:
        Banju made from chord_progression with patterns from random file of /banju
    """
    part = stream.Part()
    os.chdir(owd)
    current_dir = os.getcwd()
    sample_dir = current_dir + '/banju/16bit'
    os.chdir(sample_dir)
    file = open(file_to_open, 'r', encoding="utf-8")
    file2 = file.read().replace(' ', '')
    banju_list = [int(f) for f in file2.split(',')]
# Done
    on_list = []

    #print('banju is  ', banju_list)

    for i, banju in enumerate(banju_list):
        if (banju == -1):
            on_list.append(-1)
            continue
        isOn = [1 if 8 & banju else 0, 1 if 4 & banju else 0, 1 if 2 & banju else 0, 1 if 1 & banju else 0]
        on_list.append(isOn)

    print('banju is  ', on_list)

    for i, chord in enumerate(chord_prog):  # C, Dm, G7, etc....
        offset = i * 4
        if i > qlen / 4:
            break
        c = harmony.ChordSymbol(chord)
        previous = []
        for j, is_on in enumerate(on_list):  # [1, 0, 0, 1]
            if is_on == -1:
                for note_temp in previous:
                    note_temp.quarterLength += 0.25
            else:
                previous.clear()
                for k, on in enumerate(is_on):
                    if on:
                        if k < len(c.pitches):
                            note_temp = note.Note(c.pitches[k], quarterLength=0.25)
                            part.insert(offset + j * 0.25, note_temp)
                            previous.append(note_temp)
                        elif k == 3 and k == len(c.pitches):
                            note_temp = note.Note(c.pitches[0], quarterLength=0.25)
                            note_temp.octave += 1
                            part.insert(offset + j * 0.25, note_temp)
                            previous.append(note_temp)

    part.insert(instrument.AcousticGuitar())
    # part.show('text', addEndTimes=True)
    return part



def get_file_banju_16bit(owd):
    # Setting for the path and sample files
    os.chdir(owd)
    current_dir = os.getcwd()
    sample_dir = current_dir + '/banju/16bit'
    os.chdir(sample_dir)
    file_names = [file for file in os.listdir(sample_dir) if file != ".DS_Store"]
    file_to_open = random.choice(file_names)
    # file_to_open = '16bit/chord_001.txt'\
    return file_to_open


def export_to_part(num_list, instrument):
    """Make a stream part from the list of note numbers

    Args:
        num_list: A list of note numbers

    Returns:
        A stream part made of notes in num_list
    """
    len_list = [0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 1, 1, 1, 1, 2]
    part = stream.Part()
    part.insert(instrument)
    for num in num_list:
        note_temp = note.Note(num, quarterLength=1)
        part.append(note_temp)
    return part


def export_to_part_with_ex(num_list, instrument):
    """Make a stream part from the list of note numbers

    Args:
        num_list: A list of note numbers

    Returns:
        A stream part made of notes in num_list
    """
    exp_list = [expressions.Mordent(), expressions.InvertedMordent()]
    len_list = [0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 1, 1, 1, 1, 2]
    part = stream.Part()
    part.insert(instrument)
    for num in num_list:
        note_temp = note.Note(num, quarterLength=1)
        note_temp.expressions.append(get_random_expression());
        part.append(expressions.realizeOrnaments(note_temp))
    part.show('text', addEndTimes=True)
    return part


def get_random_expression():
    exp_list = [expressions.Appoggiatura(), expressions.Mordent(), expressions.Schleifer(),
                expressions.Tremolo(), expressions.Shake(), expressions.Trill(), expressions.Turn()]
    return random.choice(exp_list)


def play_stream(s):
    """Play the given stream

    Args:
        s: stream

    Returns:
        None
    """
    sp = midi.realtime.StreamPlayer(s)
    sp.play()


def fit_to_chord(num_list, chord_prog):
    new_num_list = []
    for i, num in enumerate(num_list):
        chord_index = int(i/4)
        pitch_midi_list = get_chord_midi(chord_prog[chord_index])

        pitch_temp = pitch.Pitch(num)
        temp_midi = pitch_temp.midi % 12

        if temp_midi not in pitch_midi_list:
            if i+1 < len(num_list):
                if (i % 4 != 3 and num_list[i+1] % 12 in pitch_midi_list) and \
                        (num_list[i-1] <= num_list[i] <= num_list[i+1] or num_list[i-1] >= num_list[i] >= num_list[i+1] ):
                    # or (i % 4 == 3 and num_list[i+1] %12 in get_chord_midi(chord_prog[chord_index+1])) or

                    new_num_list.append(num)
                    # print(i, num)
                    continue

            nearest = min(pitch_midi_list, key=lambda x: abs(x - temp_midi))
            new_num_list.append(num - temp_midi + nearest)
        else:
            new_num_list.append(num)

    return new_num_list


def get_chord_midi(chord):
    chord_here = harmony.ChordSymbol(chord)
    pitch_midi_list = []
    for pitch_ in chord_here.pitches:
        pitch_midi_list.append(pitch_.midi % 12)
    return pitch_midi_list
