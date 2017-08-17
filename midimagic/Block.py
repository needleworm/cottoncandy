class Block:
    chord = ""
    bass = []
    melody = []

    def __init__(self):
        self.chord = ""
        self.bass = [-1] * 8
        self.melody = [-1] * 8

    def print_block(self):
        print(self.chord, self.bass, self.melody)