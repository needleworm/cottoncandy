"""Library for decomposing a raw wave file into 2-dimensional array.

 decomposer.py

 Project Cinnamon
 Institute: Cheesecake Studio
 Author: Yuneui Jeong, Byunghyun Ban
 Final Release: Oct 13, 2016

"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile


class Preproc(object):
    def __init__(self):
        self.input_file_name = ''
        self.signal = None
        self.result_file_name = 'result.png'
        self.sampling_freq = 0
        self.number_of_channel = 0
        self.wave_length = 0
        self.music_length = 0
        self.time_chunk = 0.8
        self.freq_interval = 0
        self.max_len = int(6000 / 10)  # Maximum 6000Hz
        self.result = []

    def set_file(self, filename):
        self.input_file_name = filename
        self.result = []

    def decompose(self, channel):
        self.sampling_freq, wave_data = wavfile.read(self.input_file_name)
        wave_data = wave_data.astype(float)
        wave_data /= 2.**15
        self.wave_length, self.number_of_channel = wave_data.shape
        self.music_length = float(self.wave_length / self.sampling_freq)
        self.signal = wave_data[:, channel]

    def entire_plot(self):
        fig = plt.figure(figsize=(9, 5))
        axes = fig.add_axes([0.1, 0.1, 0.88, 0.88])

        axes.specgram(self.signal, Fs=self.sampling_freq, scale='dB', mode='magnitude')
        axes.set_xlim(0, 600)
        axes.set_ylim(0, 11000)

        plt.savefig(self.result_file_name)

    def fft_db(self, signal, sampling_freq):
        length = len(signal)
        window = np.hamming(length)
        signal *= window

        fft_result = np.fft.rfft(signal)
        frequency = np.arange((length / 2) + 1) / (float(length) / sampling_freq)

        spectrum_magnitude = np.abs(fft_result) * 2 / np.sum(window)
        spectrum_frequency = 20 * np.log10(spectrum_magnitude)

        return frequency, spectrum_frequency + 120

    def make_tuple(self):
        chunk = int(self.sampling_freq * self.time_chunk)
        final_index = chunk * int(self.music_length / self.time_chunk)
        current_index = 0

        while current_index + chunk != final_index:
            #print '%d chunk calculating...' % (current_index / chunk)
            frequency, db = self.fft_db(self.signal[current_index:current_index + chunk], self.sampling_freq)
            temp_result = []
            for index in range(len(frequency) - 1):
                intensity = db[index]
                if intensity < 0:
                    intensity = 0.
                temp_result.append(intensity)
            self.result.append(temp_result)
            current_index += chunk

        #print 'The last chunk calculating...'
        frequency, db = self.fft_db(self.signal[current_index:], self.sampling_freq)
        temp_result = []
        for index in range(len(frequency)):
            intensity = db[index]
            if intensity < 0:
                intensity = 0.
            temp_result.append(intensity)
        self.result.append(temp_result)

        index = 0
        for el in self.result:
            if len(el) > self.max_len:
                self.result[index] = el[:self.max_len]
            else:
                diff = self.max_len - len(el)
                if diff > 0:
                    self.result[index] = np.append(el, np.zeros(diff))
            index += 1

        for index in range(len(self.result)):
            self.result[index] = np.array(["%.3f" % i for i in self.result[index]])

        #print 'Done.'

    def plot(self):
        for index in range(len(self.result)):
            self.result[index] = np.square([float(i) for i in self.result[index]])
        dx = self.time_chunk
        dy = 10.
        y_axis, x_axis = np.mgrid[slice(0, self.max_len * 10 + dy, dy), slice(0, self.music_length, dx)]
        value = np.column_stack(tuple(self.result))

        plt.pcolormesh(x_axis, y_axis, value, cmap=plt.cm.get_cmap('YlOrRd'))
        plt.colorbar()
        plt.show()

    def report_result(self):
        filename = './res/' + self.input_file_name[:-3] + 'txt'
        #print 'Reporting the result (' + filename + ') ...'
        f = open(filename, 'w+')
        f.write(str(self.result[0]))
        f.write('\n')
        f.close()
        #print 'Done.'
