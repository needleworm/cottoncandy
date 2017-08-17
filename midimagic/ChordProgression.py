class ChordProgression:
    chord = []
    filename = []

    def __init__(self, track, length):
        self.chord = []
        for i in range(int(length / 2 + 1)):
            temp = []
            for i in range(8):
                temp.append([])
            self.chord.append(temp)
        for note in track.notes:
            self.insert_note_or_chord(note)

    def insert_note_or_chord(self, note):
        if note.isNote:
            # this is for note
            offset_start = int(note.offset / 2)
            offset_end = int((note.offset + note.duration.quarterLength) / 2)
            index_start = self.round_to_upper_16th(note.offset / 2.0 - offset_start)
            index_end = self.round_to_upper_16th((note.offset + note.duration.quarterLength) / 2.0 - offset_end)
            self.insert_note(note, offset_start, index_start, offset_end, index_end)

        if note.isChord:
            # this is for chord
            offset_start = int(note.offset / 2)
            offset_end = int((note.offset + note.duration.quarterLength) / 2)
            index_start = self.round_to_upper_16th(note.offset / 2.0 - offset_start)
            index_end = self.round_to_upper_16th((note.offset + note.duration.quarterLength) / 2.0 - offset_end)
            self.insert_chord(note, offset_start, index_start, offset_end, index_end)

    def round_to_upper_16th(self, num):
        result = round(num * 8 + 0.5)
        if result == 8:
            return -1
        return result

    def insert_note(self, note, offset_start, index_start, offset_end, index_end):
        num = int(note.pitch.ps)

        first = True

        for offset in range(offset_start, offset_end + 1):
            block = self.chord[offset]
            sindex = 0
            findex = 8
            if offset == offset_start:  # first block
                sindex = index_start
            if offset == offset_end:  # last block
                findex = index_end
            for index in range(sindex, findex):
                if first:
                    block[index].append(num)
                    first = False
                else:
                    block[index].append(128)

    def insert_chord(self, chord, offset_start, index_start, offset_end, index_end):
        pitches = chord.pitches
        nums = []

        first = True

        for pitch in pitches:
            num = int(pitch.ps)
            nums.append(num)

        for offset in range(offset_start, offset_end + 1):
            block = self.chord[offset]
            sindex = 0
            findex = 8
            if offset == offset_start:  # first block
                sindex = index_start
            if offset == offset_end:  # last block
                findex = index_end
            for index in range(sindex, findex):
                if first:
                    block[index] += nums
                    first = False
                else:
                    block[index].append(128)

    def print_notes(self):
        for block in self.chord:
            print(block)
