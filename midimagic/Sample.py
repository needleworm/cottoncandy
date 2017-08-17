from midimagic.Block import Block


class Sample:
    filename = ""
    key = None
    sharps = None
    blocks = []
    length = 0

    def __init__(self, length):
        self.length = length
        self.blocks = [Block() for i in range(self.length)]

    def insert_bass(self):
        pass

    def insert_melody(self):
        pass

    def print_blocks(self):
        for block in self.blocks:
            print(block.chord, block.melody, block.bass)
