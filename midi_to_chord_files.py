# Setting for the path and sample files
import os

import helper

label = ['A','B','C','D','E','F','G']


def is_valid_chord(chord_name):
    if not chord_name or 'pedal' in chord_name or 'power' in chord_name:
        return False
    if check_in_label(chord_name[0]):
        return True
    return False


def check_in_label(letter):
    if letter == 'A' or letter == 'B' or letter == 'C' or letter == 'D' or letter == 'E' or letter == 'F' or letter == 'G' :
        return True
    return False


def save_to_txt_file(dir, file_name, contents):
    if not os.path.exists(dir):
        os.makedirs(dir)
    file = open(dir+file_name, 'w')
    # print(file)
    file.write(contents)
    file.close()


def main():
    current_dir = os.getcwd()
    sample_dir = current_dir + '/midi_bach/out'
    save_dir = '/home/bhban/cheesecake/kimchi/bach_out/'
    os.chdir(sample_dir)
    folders = [f for f in os.listdir(sample_dir)]
    file_names = []
    for folder in folders:
        for file in os.listdir(folder):
            file_names.append(folder + '/' + file)

    # file_names= ['h/houseofsun.mid.pkl']

    print('opening ' + str(len(file_names)) + ' files...')
    # file_names = [file for file in os.listdir(sample_dir)]

    # Gets list of whole sample.

    # os.chdir(current_dir + '/midi_chord')

    for name in file_names:
        if(name == 'd/dreaming2.mid.pkl'):
            continue
        print('doing ' + name)
        samples = []
        sample_blocks = helper.open_pickle(name).blocks

        for block in sample_blocks:
            samples.append(block.chord)

        content = ''
        file_num = 0

        for sample_ in samples:
            sample = sample_.split('add')[0].split('/')[0]
            if is_valid_chord(sample):
                # print('valid ' + sample)
                content += sample
                content += ','
            else:
                # print('invalid ' + sample)
                if content:
                    content = content[:-1]
                    save_to_txt_file(save_dir + name.split('/')[0] + '/'+name.split('/')[1].split('.')[0]+'/',
                                     'C' + name.split('/')[1] + '_' + str(file_num) + '.txt', content)
                    content = ''
                    file_num += 1
        print('done ' + name)




if __name__ == '__main__':
    main()


