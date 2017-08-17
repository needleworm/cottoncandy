from os import listdir
from os.path import isfile, join

from music21 import *

from midi_bach.ChordProgression import ChordProgression
from midi_bach.Song import *


def main():
    vocal = 0
    melody = 0
    both = 0
    process = 0
    all = 0
    files = []

    us = environment.UserSettings()
    us.getSettingsPath()
    # us['musicxmlPath'] = 'C:\\Program Files (x86)\\MuseScore 2\\bin\\MuseScore.exe'
    # mypath = 'C:\\Users\\noble\\Google 드라이브\\Cheesecake Studio\\Projects\\Reindeer\\MIDI\\김범수_보고싶다.mid'
    mypath = '/home/bhban/cheesecake/bach'
    from_pass = '/home/bhban/cheesecake/bach/gold/goldberg.mid'
    passed = False

    # L M N O P Q R

    if isfile(mypath):
        files.append(mypath)
    else:
        files = [f for f in listdir(mypath)]

    # print(files)
    while files:
        file = join(mypath, files.pop(0))
        if not from_pass:
            passed = True
        if not passed and file == from_pass:
            passed = True
            continue
        if not isfile(file):
            files.extend([file + '/' + f for f in listdir(file)])
            continue
        if '.mid' not in file:
            continue
        if not passed:
            continue
        print("opening " + file)
        process += 1
        if process == 100:
            print(file, vocal, melody, all)
            process = 0
        all += 1
        mf = midi.MidiFile()
        mf.open(file, 'rb')
        try:
            mf.read()
        except:
            pass
        removeDrums(mf)
        track_num = removeUselessTrack(mf)
        # if not checkHasMelody(mf):
        #     print(file + " doensn't have melody")
        #     continue

        try:
            s = midi.translate.midiFileToStream(mf)
        except exceptions21.StreamException:
            print(file + " doesn't have stream")
            continue

        # s.show('text', addEndTimes=True)
        print(s.duration.quarterLength)

        k = s.analyze('key')
        print(k.mode)
        if k.mode == 'minor':
            i = interval.Interval(k.tonic, pitch.Pitch('A'))
        else:
            i = interval.Interval(k.tonic, pitch.Pitch('C'))
        s.transpose(i, inPlace=True)

        song = Song(s.duration.quarterLength, mf, os.path.basename(file), s)
        print(len(s))
        chordPros = []
        for part in s:
            chordPros.append(ChordProgression(part, s.duration.quarterLength))
        # chordPros[song.bass_tracks[0]].print_notes()
        # chordPros[song.melody_num].print_notes()

        # for i, chordP in enumerate(chordPros):
        #     print('wow' + str(i))
        #     chordP.print_notes()
        song.calculate_chord(chordPros)

        mf.close()


def checkHasMelody(mf):
    for track in mf.tracks:
        name = getTrackName(track).lower()
        is_vocal = 'vocal' in name
        is_melody = 'melody' in name

        if is_vocal or is_melody:
            return True
    return False


def getTrackName(track):
    for event in track.events:
        if event.type == "SEQUENCE_TRACK_NAME":
            try:
                return event.data.decode('ASCII')
            except:
                return ""
    return ""


def removeDrums(mf):
    for i, track in enumerate(mf.tracks):
        if 10 in track.getChannels():
            mf.tracks.remove(track)


def removeUselessTrack(mf):
    num = 0
    remove_track = []
    for i, track in enumerate(mf.tracks):
        if i == 0:
            continue
        if not track.hasNotes():
            remove_track.append((i, track))
            num += 1

    for trackh in remove_track:
        mf.tracks.remove(trackh[1])
        print('removed' + str(trackh[0]))
    return num


def removeBass(mf):
    bass_tracks = []
    for i, track in enumerate(mf.tracks):
        inst = getInstrument(track)
        if not inst:
            print("null")
            continue
        if 32 <= inst <= 39:
            print("track", i, "removed")
            mf.tracks.remove(track)
            bass_tracks.append(track)
            continue
        else:
            print("pass", inst)
            continue
    return bass_tracks


def getInstrument(track):
    for event in track.events:
        if event.type == "PROGRAM_CHANGE":
            inst = event.data
            if not inst:
                return None
            else:
                return inst


if __name__ == '__main__':
    main()
