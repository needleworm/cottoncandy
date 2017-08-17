"""Markov chain and its helper class

markovchain.py

Author: Yuneui Jeong @ Cheesecake Studio
Final Update: Feb 7th, 2017

"""
import numpy as np
import pickle
import random


class Markov(object):
    """Markov chain generator.

    Attributes:
        state_label_: Tuple for the name of states.
        inner_states_: The number of states.
        transmat_: Transition matrix.
        state_occurrence_: The number describing how much a state has occurred.
        order_: Order of Markov chain.

    Methods:
        get_state_offset_: Encodes the set of previous states into an integer.
        fit: Trains this melody_model so that parameters in self.transmat_ get updated.
        dump_model: Saves current melody_model in pickle form.
        transit_: Randomly transits from the current state to the next state along the transition matrix.
        random_gen: Randomly generates new series along the melody_model.

    """
    def __init__(self, num_states, label, order):
        """Constructor for Markov object.

        Args:
            num_states: An integer for the number of states.
            label: A tuple for the labels of states.
            order: Order of Markov chain.

        """
        self.state_label_ = tuple(label)
        self.inner_states_ = num_states ** order
        self.outer_states_ = num_states
        self.transmat_ = np.zeros((self.inner_states_, self.outer_states_))
        self.state_occurrence_ = np.zeros(self.inner_states_)
        self.order_ = order

    def get_state_offset_(self, states):
        """Encodes the set of previous states into an integer.

        Args:
            states: State transition history.

        Returns:
            An integer representing the state offset of transition matrix.
        """
        order = self.order_ - 1
        offset = 0

        for el in states:
            offset += (self.outer_states_ ** order) * el
            order -= 1

        return offset

    def fit(self, sample):
        """Trains this melody_model so that parameters in self.transmat_ get updated.

        Args:
            sample: List for test sample.
            line: Flag for melody module.

        """
        for state in range(self.inner_states_):
            self.transmat_[state] *= self.state_occurrence_[state]

        states = StateQueue(self.order_)

        for el in sample:
            if type(el) is str:
                curr_state = self.state_label_.index(el[0])
            elif type(el) is int:
                curr_state = self.state_label_.index(el)

            if len(states) < self.order_:
                states.enqueue(curr_state)
                continue

            prev_state = self.get_state_offset_(states.get_states())

            self.transmat_[prev_state][curr_state] += 1
            self.state_occurrence_[prev_state] += 1

            states.enqueue(curr_state)

        for state in range(self.inner_states_):
            if self.state_occurrence_[state] != 0:
                self.transmat_[state] /= self.state_occurrence_[state]

    def dump_model(self, pkl_name='markov.pkl'):
        """Saves current melody_model in pickle form.

        Args:
            pkl_name: File name for output pickle.

        Yields:
            A pickle file.

        """
        output_file = open(pkl_name, 'wb')
        pickle.dump(self, output_file, protocol=pickle.HIGHEST_PROTOCOL)
        output_file.close()

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

        if next_state == self.outer_states_:
            next_state = (self.outer_states_ - 1) // 2

        return next_state

    def decode_offset_(self, offset):
        result = []
        quotient = offset // self.outer_states_
        while offset >= self.outer_states_:
            result.append(quotient)
            offset %= self.outer_states_
        result.append(offset)

        return result

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
            next_state = self.transit_(offset)
            result.append(self.state_label_[next_state])
            states.enqueue(next_state)
            offset = self.get_state_offset_(states.get_states())
        return result


class StateQueue(object):
    """Queue data type for saving history of state transitions.

    Attributes:
        queue_: Actual data storage of the queue.
        order_: Marginal length of the queue.
        length_: Current number of elements.

    Methods:
        enqueue: Enqueues an element on the queue.
        clear_queue: Clears the queue.
        top: Gets the top of the queue.
        bottom: Gets the bottom of the queue.
        is_empty: Checks whether the queue is empty or not.
        undo: Restores state history to the one before the latest enqueue.
        get_states: Gets the tuple of current state history.
        get_calibrated_states: Gets calibrated states for the Line module.

    """
    def __init__(self, order):
        """Constructor for StateQueue object.

        Args:
            order: Marginal length of the queue.

        """
        self.queue_ = []
        self.order_ = order
        self.length_ = 0
        self.prev_state = None

    def __len__(self):
        return self.length_

    def enqueue(self, el):
        """Enqueues an element on the queue.

        Args:
            el: An object which is to be enqueued.

        """
        if len(self) < self.order_:
            self.queue_.append(el)
            self.length_ += 1
        else:
            self.prev_state = self.queue_[0]
            for i in range(1, self.order_):
                self.queue_[i - 1] = self.queue_[i]
            self.queue_[self.order_ - 1] = el

    def clear_queue(self):
        """Clears the queue."""
        self.queue_ = []
        self.length_ = 0
        self.prev_state = None

    def top(self):
        """Gets the top of the queue.

        Returns:
            Top element of the queue.

        """
        assert self.length_ > 0
        return self.queue_[self.length_ - 1]

    def bottom(self):
        """Gets the bottom of the queue.

        Returns:
            Bottom element of the queue.

        """
        return self.queue_[0]

    def is_empty(self):
        """Checks whether the queue is empty or not.

        Returns:
            Boolean which represents whether the queue is empty.
        """
        return self.length_ == 0

    def undo(self):
        """Restores state history to the one before the latest enqueue."""
        for i in range(1, self.order_):
            self.queue_[i] = self.queue_[i - 1]
        self.queue_[0] = self.prev_state
        self.prev_state = None

    def get_states(self):
        """Gets the tuple of current state history.

        Returns:
            Tuple of current state history.
        """
        assert len(self) == self.order_
        return self.queue_

    def get_calibrated_states(self, leap_range):
        """Gets calibrated states for the Line module.

        Returns:
            Tuple of current state history.
        """
        assert len(self) == self.order_
        return [leap_range + state - self.queue_[0] for state in self.queue_]
