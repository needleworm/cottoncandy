"""Modules for Kimchi-Chord

modules.py

Author: Yuneui Jeong @ Cheesecake Studio
Final Update: Feb 7th, 2017

"""
from music21 import pitch, harmony

from markovchain import *


class Chord(Markov):
    """Learns and generates a chord progression.

    Attributes:
        var_list_: List of all possible variants.
        lookup_: Lookup table for generating variants.
        var_occurrence_: The number describing how much a variant has occurred.

    """

    def __init__(self, num_states, label, order, var_list):
        super().__init__(num_states, label, order)
        self.var_list_ = tuple(var_list)
        self.lookup_ = np.zeros((self.inner_states_, self.outer_states_, len(var_list)))
        self.var_occurrence_ = np.zeros((self.inner_states_, self.outer_states_))

    def fit(self, sample):
        """Trains this melody_model so that parameters in self.transmat_ get updated.

        Args:
            sample: List for test sample.

        """
        for state in range(self.inner_states_):
            self.transmat_[state] *= self.state_occurrence_[state]

        for l_index in range(self.inner_states_):
            for r_index in range(self.outer_states_):
                self.lookup_[l_index][r_index] *= self.var_occurrence_[l_index][r_index]

        states = StateQueue(self.order_)

        for el in sample:
            if el == '-1':
                continue
            curr_state = self.state_label_.index(el[0])
            variant = self.var_list_.index(el[1:])

            if len(states) < self.order_:
                states.enqueue(curr_state)
                continue

            prev_state = self.get_state_offset_(states.get_states())

            self.transmat_[prev_state][curr_state] += 1
            self.state_occurrence_[prev_state] += 1
            self.lookup_[prev_state][curr_state][variant] += 1
            self.var_occurrence_[prev_state][curr_state] += 1

            states.enqueue(curr_state)

        for state in range(self.inner_states_):
            if self.state_occurrence_[state] != 0:
                self.transmat_[state] /= self.state_occurrence_[state]

        for l_index in range(self.inner_states_):
            for r_index in range(self.outer_states_):
                if self.var_occurrence_[l_index][r_index] != 0:
                    self.lookup_[l_index][r_index] /= self.var_occurrence_[l_index][r_index]

    def transit_(self, current_state):
        """Randomly transits from the current state to the next state along the transition matrix.

        Args:
            current_state: Integer which represents the current state.

        Returns:
            Integer which represents the next state.

        """
        prob_degree = random.random()
        trans_degree = self.transmat_[current_state]
        next_state = 0

        while next_state < self.outer_states_:
            if prob_degree < trans_degree[next_state]:
                break
            else:
                prob_degree -= trans_degree[next_state]
                next_state += 1

        prob_var = random.random()
        trans_var = self.lookup_[current_state][next_state]
        variant = 0

        while variant < self.inner_states_:
            if prob_var < trans_var[variant]:
                break
            else:
                prob_var -= trans_var[variant]
                variant += 1

        return next_state, variant

    def random_gen(self, length=32):
        """Randomly generates new series along the melody_model.

        Args:
            length: Length of newly generated series of states.

        Returns:
            List of new series of states.

        """
        states = StateQueue(self.order_)
        for _ in range(self.order_):
            states.enqueue(0)

        offset = self.get_state_offset_(states.get_states())
        result = [self.state_label_[0] for _ in range(self.order_)]

        for _ in range(length - self.order_):
            next_state, variant = self.transit_(offset)
            result.append(self.state_label_[next_state] + self.var_list_[variant])
            states.enqueue(next_state)
            offset = self.get_state_offset_(states.get_states())
        return result




class Line(Markov):
    """Learns and generates lines for melody and bass.

    Attributes:
        leap_list_: Possible interval list of leap occurrence.
        seed_note_: Seed notes for initial state.
    """

    def __init__(self, seed_note, order):
        self.leap_range_ = 12
        self.leap_list_ = tuple(list(range(-self.leap_range_, self.leap_range_ + 1)))
        super().__init__(len(self.leap_list_), self.leap_list_, order)
        self.seed_note_ = seed_note

    @staticmethod
    def strip_(sample):
        """Strips empty element in a sample list.

        Args:
            sample: List of sample data.

        Returns:
            Stripped sample data.

        """
        result_sample = []

        for el in sample:
            if el == -1 or el == 128:
                continue
            result_sample.append(el)

        return result_sample

    def leap_check_(self, states, current_note):
        """Check whether high leap has occurred.

        Args:
            states: StateQueue of notes.
            current_note: Integer which represents the current note.

        Returns:
            Boolean which denotes whether high leap has occurred.

        """
        interval = current_note - states.bottom()

        return not -self.leap_range_ <= interval <= self.leap_range_

    def fit(self, sample):
        """Trains this melody_model so that parameters in self.transmat_ get updated.

        Args:
            sample: List for sample data.

        """
        sample = self.strip_(sample)

        elements = self.outer_states_ ** (self.order_ - 1)
        l_index = ((self.outer_states_ - 1) // 2) * elements
        r_index = l_index + elements

        for state in range(l_index, r_index):
            self.transmat_[state] *= self.state_occurrence_[state]

        states = StateQueue(self.order_)

        for el in sample:
            if not states.is_empty() and self.leap_check_(states, el):
                states.clear_queue()

            if len(states) < self.order_:
                states.enqueue(el)
                continue

            prev_state = self.get_state_offset_(states.get_calibrated_states(self.leap_range_))
            curr_state = self.state_label_.index(el - states.bottom())

            self.transmat_[prev_state][curr_state] += 1
            self.state_occurrence_[prev_state] += 1

            states.enqueue(el)

        for state in range(l_index, r_index):
            if self.state_occurrence_[state] != 0:
                self.transmat_[state] /= self.state_occurrence_[state]

        self.transmat_ = self.transmat_[l_index:r_index]

    def random_gen(self, length=32):
        """Randomly generates new series of melody along the melody_model.

        Args:
            length: Length of new melody.

        Returns:
            List of new melody.
        """
        states = StateQueue(self.order_)
        result = []

        elements = self.outer_states_ ** (self.order_ - 1)
        index = ((self.outer_states_ - 1) // 2) * elements

        for el in self.seed_note_:
            states.enqueue(el)
            result.append(el)

        offset = self.get_state_offset_(states.get_calibrated_states(self.leap_range_)) - index

        for _ in range(length - self.order_):
            while True:
                next_state = self.transit_(offset)
                next_note = result[len(states) - self.order_] + self.state_label_[next_state]
                result.append(next_note)
                states.enqueue(next_note)
                old_offset = offset
                offset = self.get_state_offset_(states.get_calibrated_states(self.leap_range_)) - index

                if 0 <= offset < elements:
                    break
                else:
                    states.undo()
                    del result[-1]
                    offset = old_offset

        return result

    def random_gen_by_chord(self, chord_prog, length=32):
        """Randomly generates new series of melody along the melody_model.

        Args:
            length: Length of new melody.

        Returns:
            List of new melody.
        """
        states = StateQueue(self.order_)
        result = []

        elements = self.outer_states_ ** (self.order_ - 1)
        index = ((self.outer_states_ - 1) // 2) * elements

        for el in self.seed_note_:
            states.enqueue(el)
            result.append(el)

        offset = self.get_state_offset_(states.get_calibrated_states(self.leap_range_)) - index

        for i in range(length - self.order_):
            chord_here = harmony.ChordSymbol(chord_prog[int(i / 4)])
            pitches_list = []
            for pitch_ in chord_here.pitches:
                pitches_list.append(pitch_.name)

            time = 0
            while True:
                next_state = self.transit_(offset)
                next_note = result[len(states) - self.order_] + self.state_label_[next_state]
                states.enqueue(next_note)
                old_offset = offset
                offset = self.get_state_offset_(states.get_calibrated_states(self.leap_range_)) - index

                pitch_here = pitch.Pitch(next_note)

                if 0 <= offset < elements and pitch_here.name in pitches_list:
                    result.append(next_note)
                    print(pitch_here, next_note, pitches_list)
                    break
                else:
                    states.undo()
                    offset = old_offset
                    if time == 0:
                        choice = int(random.choice(chord_here.pitches).ps)
                        states.enqueue(choice)
                        result.append(choice)
                    else:
                        time += 1

        return result

    def set_seed(self, seed_note):
        """update seed

        Args:
            seed_note: given seed note

        Returns:
            None
        """
        self.seed_note_ = seed_note
