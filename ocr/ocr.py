__author__ = 'ania'

import numpy as np
from numpy.fft import fft2, ifft2
import os, sys
from math import sqrt, floor, ceil

from scipy import misc
import matplotlib.pyplot as plt
import re
from mahotas import colors  # library for rgb2gray
import Image

# global variables
letters = {}


def load_image(filename):  # returns image as ndarray in grayscale and negative
    image = colors.rgb2grey(misc.imread(filename))
    image = 255 - image  # creating a negative
    return image


def load_letters(directory):  # returns basic width and height for characters
    basic_width, basic_height = 0, 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            letter = re.sub(r'\.png', '', file)
            letters[letter] = load_image(root + '/' + file)

            if basic_width == 0:
                basic_width = letters[letter].shape[1]

            if basic_height == 0:
                basic_height = letters[letter].shape[0]  # the same for all letters

    return basic_height, basic_width


def detect_letter(letter, image, table_of_maxes, text):  # modifies text, finds pattern in image
    imp = letters[letter]
    [h, w] = image.shape
    C = ifft2(fft2(image) * fft2(np.rot90(imp, 2), s=[h, w])).real  # convolution
    threshold = np.max(np.max(C)) * 0.975
    Z = C > threshold

    for i in xrange(h):
        for j in xrange(w):
            if Z[i][j] == True:
                if C[i][j] > table_of_maxes[i][j]:
                    table_of_maxes[i][j] = C[i][j]
                    text[i][j] = letter


def order_text(text, height, width):  # puts text in order
    new_text = []
    k = 0

    h = len(text)
    w = len(text[0])

    k = 0
    previous_y = 0
    for i in xrange(h):
        previous_x = 0
        for j in xrange(w):
            if text[i][j] != '':
                if i == previous_y:
                    spaces = int(floor(float(j - previous_x) / width))
                else:
                    spaces = int(floor(float(j) / width))

                for l in xrange(spaces - 1):
                    new_text.append(' ')

                new_text.append(text[i][j])

                previous_x = j
                previous_y = i
        if k == height:
            new_text.append('\n')
            k = 0
        k += 1

    return new_text


def character_recognition(filename, directory_with_patterns):  # detects all letters and puts them into text
    basic_height, basic_width = load_letters(directory_with_patterns)
    image = load_image(filename)

    [h, w] = image.shape
    text = [['' for i in xrange(w)] for j in xrange(h)]
    table_of_maxes = [[0 for i in xrange(w)] for j in xrange(h)]

    for k in letters.keys():
        detect_letter(k, image, table_of_maxes, text)

    string = ''.join(order_text(text, basic_height, basic_width))

    return string


if __name__ == '__main__':
    font = raw_input("Which font do you want to test? [liberation mono, free sans, ubuntu bold] ")
    if font in ['liberation mono', 'free sans', 'ubuntu bold']:
        sample = font.replace(' ', '') + '_sample.png'
        directory = './' + font.replace(' ', '')
    else:
        print 'error: wrong font'
        sys.exit(0)
    recognized_text = character_recognition(sample, directory)
    print 'Recognized text:'
    print recognized_text
    print '\nWait for image to load.'
    Image.open(sample).show()



