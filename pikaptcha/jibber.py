#!/usr/bin/env python
import string
import random

__all__ = ('generate_word', 'generate_words', 'generate_password')

initial_consonants = list(set(string.ascii_lowercase) - set('aeiou')
                      # remove those easily confused with others
                      - set('qxc')
                      # add some crunchy clusters
                      | set(['bl', 'br', 'cl', 'cr', 'dr', 'fl',
                             'fr', 'gl', 'gr', 'pl', 'pr', 'sk',
                             'sl', 'sm', 'sn', 'sp', 'st', 'str',
                             'sw', 'tr', 'ch', 'sh'])
                      )

final_consonants = list(set(string.ascii_lowercase) - set('aeiou')
                    # remove the confusables
                    - set('qxcsj')
                    # crunchy clusters
                    | set(['ct', 'ft', 'mp', 'nd', 'ng', 'nk', 'nt',
                           'pt', 'sk', 'sp', 'ss', 'st', 'ch', 'sh'])
                    )

vowels = 'aeiou'

symbols = '#?!@$%%^&><+`*()-]'

def generate_word():
    """Returns a random consonant-vowel-consonant pseudo-word."""
    return ''.join(random.choice(s) for s in (initial_consonants,
                                              vowels,
                                              final_consonants))


def generate_words(wordcount):
    """Returns a list of ``wordcount`` pseudo-words."""
    return ''.join([generate_word() for _ in xrange(wordcount)])


def random_chars(chars, count):
    return [random.choice(chars) for _ in xrange(count)]


def generate_password(lowercase_length, uppercase_length, digit_length, symbol_length):
    chars = random_chars(string.ascii_lowercase, lowercase_length) +\
            random_chars(string.ascii_uppercase, uppercase_length) +\
            random_chars(string.digits, digit_length) +\
            random_chars(symbols, symbol_length)
    random.shuffle(chars)
    return ''.join(chars)
