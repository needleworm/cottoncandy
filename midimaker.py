"""
Project Cottoncandy

midi_and_label_gen.py

Author : Byunghyun ban & Yunei Jeong
Institute : Cheesecake Studio

Latest Modification : 2016. 10. 20.

"""

"""
This tool saves midi file and their labels.
"""


import music21.chord as ch
import music21.instrument as inst
import music21.midi.translate as conv
import music21.note as nt
import music21.stream as st

INSTs = [
    inst.Accordion(), inst.AcousticBass(), inst.AcousticGuitar(), inst.Agogo(), inst.Alto(), inst.AltoSaxophone(), inst.Bagpipes(),
    inst.Banjo(), inst.Baritone(), inst.BaritoneSaxophone(), inst.Bass(), inst.BassClarinet(), inst.Bassoon(), inst.BassTrombone(),
    inst.BrassInstrument(), inst.Celesta(), inst.ChurchBells(), inst.Clarinet(), inst.Clavichord(), inst.Contrabass(), inst.Dulcimer(),
    inst.ElectricBass(), inst.ElectricGuitar(), inst.ElectricOrgan(), inst.EnglishHorn(), inst.Flute(), inst.FretlessBass(), inst.Glockenspiel(),
    inst.Guitar(), inst.Harmonica(), inst.Harp(), inst.Harpsichord(), inst.Horn(), inst.Kalimba(), inst.Koto(), inst.Lute(), inst.Mandolin(),
    inst.Marimba(), inst.MezzoSoprano(), inst.Oboe(), inst.Ocarina(), inst.Organ(), inst.PanFlute(), inst.Piano(), inst.Piccolo(), inst.PipeOrgan(),
    inst.Recorder(), inst.ReedOrgan(), inst.Saxophone(), inst.Shakuhachi(), inst.Shamisen(), inst.Shehnai(),
    inst.Soprano(), inst.SopranoSaxophone(), inst.SteelDrum(), inst.StringInstrument(),
    inst.Taiko(), inst.Tenor(), inst.TenorSaxophone(),
    inst.Timpani(), inst.Trombone(), inst.Trumpet(), inst.Tuba(), inst.TubularBells(), inst.Ukulele(),
    inst.Vibraphone(), inst.Viola(), inst.Violin(), inst.Violoncello(), inst.Vocalist(),
    inst.Whistle(), inst.Woodblock(), inst.Xylophone()
]


keys = {
    0: 'A',
    1: 'A#',
    2: 'B',
    3: 'C',
    4: 'C#',
    5: 'D',
    6: 'D#',
    7: 'E',
    8: 'F',
    9: 'F#',
    10: 'G',
    11: 'G#'
}


def chord2notes(index):
    for i in range(len(index)):
        octave = str(int((index[i] + 9) / 12))
        key = keys[index[i] % 12]
        index[i] = key + octave
    return index


def Vector2Name(keyVector):
    name = "0"* (88-len(keyVector))
    for k in keyVector:
        name +=str(k)

    return name
    
    


def note2Midi(note, keyVector):
    for INST in INSTs:
        result_note = nt.Note(note[0])
        result_note.quarterLength = 0.125

        result = st.Stream()
        result.append(INST)
        result.append(result_note)

        filename = Vector2Name(keyVector) + str(INST.bestName())
        midi = conv.streamToMidiFile(result)
        midi.open('./singledata/' + filename + '.mid', 'wb')
        midi.write()
        midi.close()

        

def chord2Midi(notes, keyVector):
    for INST in INSTs:
        result_chord = ch.Chord(notes)
        result = st.Stream()

        result.append(INST)
        result.append(result_chord)

        filename = Vector2Name(keyVector) + str(INST.bestName())

        midi = conv.streamToMidiFile(result)
        midi.open('./tripledata/' + filename + '.mid', 'wb')
        midi.write()
        midi.close()



def vector2Chord(keyVector):
    cp = []
    for keys in keyVector:
        cp.append(keys)
    chord = []
    while 1 in cp:
        key = cp.index(1)
        cp[key] = 0
        chord.append(key)
    return chord


def vector2midi(keyVector):
    chord = vector2Chord(keyVector)
    notes = chord2notes(chord)
    if keyVector.count(1) == 1:
        note2Midi(notes, keyVector)
    elif keyVector.count(1) > 1:
        chord2Midi(notes, keyVector)


def Single():
    for i in range(88):
        keyVector = []
        for j in range(88):
            keyVector.append(0)
        keyVector[i] = 1

        vector2midi(keyVector)


def Double():
    for i in range(88):
        for j in range(i, 88):
            keyVector = []
            for k in range(88):
                keyVector.append(0)
            keyVector[i] = 1
            keyVector[j] = 1

            vector2midi(keyVector)


def Triple():
    for i in range(88):
        for j in range(i, 88):
            for k in range(j, 88):
                keyVector = []
                for z in range(88):
                    keyVector.append(0)
                keyVector[i] = 1
                keyVector[j] = 1
                keyVector[k] = 1

                vector2midi(keyVector)


Single()
#Double()




