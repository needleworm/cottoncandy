from music21 import midi


class Track:
    def __init__(self):
        self.name = ""
        self.inst = -1
        self.tempo = -1
        self.events = None

    def __init__(self, track):
        self.name = self.getTrackName(track)
        self.inst = self.getInstrument(track)
        self.tempo = self.getTempo(track)
        self.key = self.getKeySignature()
        self.time = self.getTimeSignature()
        self.events = track.events
        print(self.tempo)
        print(self.name)
        for event in self.events:
            print(event)

    def resolveEvents(self, events):
        block = []
        active_pitch = []
        for event in events:
            if event.isNoteOn():
                active_pitch.append(event.pitch)
            elif event.isNoteOff():
                if event.pitch in event.velocity:
                    active_pitch.remove(event.pitch)
            if event.type == "DeltaTime":
                if active_pitch:
                    for pitch in active_pitch:
                        pass

    def getKeySignature(self, track):
        for event in track.events:
            if event.type == "KEY_SIGNATURE":
                try:
                    return event.data.decode('ASCII')
                except UnicodeDecodeError:
                    pass

    def getTimeSignature(self, track):
        for event in track.events:
            if event.type == "TIME_SIGNATURE":
                try:
                    return event.data.decode('ASCII')
                except UnicodeDecodeError:
                    pass

    def getTempo(self, track):
        for event in track.events:
            if event.type == "SET_TEMPO":
                try:
                    return event.data.decode('ASCII')
                except UnicodeDecodeError:
                    pass

    def getTrackName(self, track):
        for event in track.events:
            if event.type == "SEQUENCE_TRACK_NAME":
                try:
                    return event.data.decode('ASCII')
                except UnicodeDecodeError:
                    pass
                except midi.MidiException:
                    pass

    def getInstrument(self, track):
        for event in track.events:
            if event.type == "PROGRAM_CHANGE":
                inst = event.data
                if inst == None:
                    return None
                else:
                    return inst

    def isTrackBase(self, inst):
        if inst == None:
            return False
        if 32 <= inst <= 39:
            return True
        else:
            return False
