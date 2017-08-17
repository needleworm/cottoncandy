import operator
import os
import pickle

from music21 import harmony
from music21.chord import Chord

from midi_bach.Block import Block
from midi_bach.Sample import Sample


class Song:
    def __init__(self, length, mf, filename, s):
        # self.key = self.get_key_sig(s)
        # if self.key:
        #     self.sharps = self.key.sharps
        # else:
        #     self.sharps = None
        self.filename = filename
        self.length = int(length / 2 + 1)
        self.blocks = [Block() for i in range(int(length / 2 + 1))]
        self.chord_dict = []
        self.bass_tracks = []
        self.melody_num = 0
        self.key = s.analyze('key')
        print(self.key)

    # def get_key_sig(self, s):
    #     keys = s.keySignature
    #     # if len(keys) > 1 or not keys:
    #     #     print('more than 1 key')
    #     #     print(keys)
    #     #     return None
    #     # else:
    #     #     return keys[0]
    #     return keys

    def get_bass_num(self, mf):
        bass_tracks = []
        for i, track in enumerate(mf.tracks):
            inst = self.getInstrument(track)
            if not inst:
                continue
            if 32 <= inst <= 39:
                print('bass' + str(i))
                bass_tracks.append(i - 1)
                continue
            else:
                continue
        return bass_tracks

    def getInstrument(self, track):
        for event in track.events:
            if event.type == "PROGRAM_CHANGE":
                inst = event.data
                if not inst:
                    return None
                else:
                    return inst

    def get_melody_num(self, mf):
        for i, track in enumerate(mf.tracks):
            name_lower = self.getTrackName(track).lower()
            if 'vocal' in name_lower or 'melody' in name_lower:
                print("melody", i)
                return i - 1

    def getTrackName(self, track):
        for event in track.events:
            if event.type == "SEQUENCE_TRACK_NAME":
                try:
                    return event.data.decode('ASCII')
                except:
                    return ""
        return ""

    def calculate_chord(self, chord_pros):
        previous = [[] for i in range(len(chord_pros))]
        for i in range(self.length):
            # for j in range(1):
            tempDict = {}
            for j, chord_pro in enumerate(chord_pros):
                # print('well')
                # chord_pro.print_notes()
                block = chord_pro.chord[i]
                for k in range(8):
                    # print(block)
                    note_list = block[k]
                    if not note_list:
                        continue
                    if note_list[0] == 128:
                        for note_pitch in previous[j]:
                            if note_pitch not in tempDict:
                                tempDict[note_pitch] = 1
                            else:
                                tempDict[note_pitch] += 1
                    else:
                        previous[j].clear()
                        for note_pitch in note_list:
                            if note_pitch not in tempDict:
                                tempDict[note_pitch] = 1
                                previous[j].append(note_pitch)
                            else:
                                tempDict[note_pitch] += 1
                                previous[j].append(note_pitch)

            # print(tempDict)
            self.chord_dict.append(sorted(tempDict.items(), key=operator.itemgetter(1)))
        self.resolve_chord(chord_pros)

    def resolve_chord(self, chord_pros):
        sample = Sample(self.length)
        # sample.key = self.key
        # sample.sharps = self.sharps
        for i, dict in enumerate(self.chord_dict):
            # print(i, ': ', dict, end="")
            sample_block = sample.blocks[i]
            if self.bass_tracks:
                chordP = chord_pros[self.bass_tracks[0]]
                block = chordP.chord[i]
                for j, t_chord in enumerate(block):
                    if t_chord:
                        sample_block.bass[j] = max(t_chord)
            block = chord_pros[self.melody_num].chord[i]
            for j, t_chord in enumerate(block):
                if t_chord:
                    sample_block.melody[j] = max(t_chord)
            note_list = []
            all = 0
            for set in dict:
                all += set[1]
            for set in dict:
                if set[1] / all >= 0.1:
                    note_list.append(set[0])
            chord = Chord(note_list)
            chord.removeRedundantPitchNames(inPlace=True)
            # chord.closedPosition(inPlace=True)
            chord.simplifyEnharmonics(inPlace=True)
            # print(chord, end="")
            if chord:
                try:
                    chord_text = harmony.chordSymbolFigureFromChord(chord)
                    print(chord.commonName, harmony.chordSymbolFigureFromChord(chord))
                except:
                    chord_text = ''
                if 'Cannot' not in chord_text:
                    sample_block.chord = chord_text
            else:
                pass
                # print()
            # sample_block.print_block()
        dir = 'out/' + self.filename[0].lower() + '/'
        if not os.path.exists(dir):
            os.makedirs(dir)
        f = open(dir + self.filename + '.pkl', 'wb')
        print('saved to ' + dir + self.filename + '.pkl')
        pickle.dump(sample, f)
        f.close()


# def insert_not_or_chord_to_bass(self, note):
#     if note.isNote:
#         # this is for note
#         offset_start = int(note.offset / 2)
#         offset_end = int((note.offset + note.duration.quarterLength) / 2)
#         index_start = self.round_to_upper_16th(note.offset / 2.0 - offset_start)
#         index_end = self.round_to_upper_16th((note.offset + note.duration.quarterLength) / 2.0 - offset_end)
#         self.insert_notes_to_bass_block(note, offset_start, index_start, offset_end, index_end)
#
#     if note.isChord:
#         # this is for chord
#         pass
#
#
# def round_to_upper_16th(self, num):
#     result = round(num * 8 + 0.5)
#     if result == 8:
#         return -1
#     return result
#
#
# def insert_notes_to_bass_block(self, note, offset_start, index_start, offset_end, index_end):
#     num = int(note.pitch.ps - 7 + 1)
#     if num > 88:
#         print('this is strange', self.filename)
#
#     for offset in range(offset_start, offset_end + 1):
#         block = self.blocks[offset]
#         sindex = 0
#         findex = 8
#         if offset == offset_start:  # first block
#             sindex = index_start
#         if offset == offset_end:  # last block
#             findex = index_end
#         for index in range(sindex, findex):
#             if index == sindex:
#                 block.bass[index] = num
#             else:
#                 block.bass[index] = 89


def print_notes(self):
    for block in self.blocks:
        print(block.bass)
