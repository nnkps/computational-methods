__author__ = 'ania'

from pyPdf import PdfFileReader
import re
import numpy as np
import json

keywords = []  # all words from doc with indexes
bag_of_words = []

NUMBER_OF_PAGES = 1000 #1697


def get_words_from_page(doc, page):
    text = doc.getPage(page).extractText()
    text = re.sub('\d', '', text)
    words = re.compile('\w+').findall(text)  # searching for words only

    return words


def set_keywords(doc):
    for page in xrange(0, NUMBER_OF_PAGES):
        words = get_words_from_page(doc, page)
        for word in words:
            if len(word) > 2:  # we want to ignore words with one character
                new_word = word.encode('ascii','ignore').lower()
                if new_word not in keywords:
                    keywords.append(new_word)

    with open('keywords.json', 'w') as outfile:
        json.dump(keywords, outfile)


def create_bag_of_words(doc):
    # number_of_pages = doc.getNumPages()
    keywords_length = len(keywords)

    for page in xrange(0, NUMBER_OF_PAGES):
        page_vector = keywords_length * [0]  # creating vector representing this page

        words = get_words_from_page(doc, page)
        for word in words:
            if len(word) > 2:  # we want to ignore words with one character
                new_word = word.encode('ascii','ignore').lower()
                page_vector[keywords.index(new_word)] += 1

        bag_of_words.append(page_vector)  # for every page in doc we're adding this vector to bag_of_words

    with open('bag.json', 'w') as outfile:
        json.dump(bag_of_words, outfile)


def load_keywords():
    with open('keywords.json') as file:
        keywords = json.loads(file.read())
    return keywords


def load_bag():
    with open('bag.json') as file:
        bag_of_words = json.loads(file.read())
    return bag_of_words


def inverse_document_frequency():
    keywords_length = len(keywords)
    bag = np.array(bag_of_words)

    idf = lambda i: np.log(NUMBER_OF_PAGES / np.count_nonzero(bag[:, i]))

    for w in xrange(0, keywords_length):
        bag[:, w] *= idf(w)

    return bag


def make_query_vector(phrase):  # we want to transform phrase to bag of words form
    words = phrase.split()
    keywords_length = len(keywords)
    vector = keywords_length * [0]
    for word in words:
        if word.lower() in keywords:
            vector[keywords.index(word.lower())] += 1

    q = np.array(vector)
    return q


def search(phrase, bag, k):  # searching phrase
    q = make_query_vector(phrase)

    cos = [0] * NUMBER_OF_PAGES
    for i in xrange(NUMBER_OF_PAGES):
        tmp = np.dot(q, bag[i].T) / (np.linalg.norm(q) * np.linalg.norm(bag[i].T))
        cos[i] = tmp

    pages = range(NUMBER_OF_PAGES)
    cos, pages =  zip(*sorted(zip(cos, pages),reverse=True))
    print "Phrase '%s' can appear on following pages:" % phrase

    for i in xrange(0, k):
        print pages[i] + 1


def svd_and_approximation(bag, rank):
    SVD = np.linalg.svd(bag.T, full_matrices=False)
    u, s, v = SVD
    Ak = np.zeros((len(u), len(v)))

    rank = int((float(rank)/100) * NUMBER_OF_PAGES)
    for i in xrange(rank):
        Ak += s[i] * np.outer(u.T[i], v[i])
    return Ak.T


if __name__ == '__main__':
    #document = PdfFileReader(file("The Beatles.pdf", "rb"))
    #set_keywords(document)
    keywords = load_keywords()
    print len(keywords)
    #create_bag_of_words(document)
    bag_of_words = load_bag()

    bag_array = inverse_document_frequency()

    bag_array = svd_and_approximation(bag_array, 50)

    phrase = raw_input('Search: ')
    number = raw_input('Number of results: ')
    search(phrase, bag_array, int(number))

