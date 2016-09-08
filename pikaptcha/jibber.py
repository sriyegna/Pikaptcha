#!/usr/bin/env python
import string
import random
import datetime

__all__ = ('generate_word', 'generate_words', 'random_birthday', 'random_email', 'random_string', 'random_account')

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


def generate_word():
    """Returns a random consonant-vowel-consonant pseudo-word."""
    return ''.join(random.choice(s) for s in (initial_consonants,
                                              vowels,
                                              final_consonants))


def generate_words(wordcount):
    """Returns a list of ``wordcount`` pseudo-words."""
    return ''.join([generate_word() for _ in xrange(wordcount)])

def random_birthday():
    start = datetime.datetime(1980, 1, 1)
    end = datetime.datetime(1990, 12, 31)
    diff = end - start
    random_duration = random.randint(0, diff.total_seconds())
    birthday = start + datetime.timedelta(seconds=random_duration)
    return "{year}-{month:0>2}-{day:0>2}".format(year=birthday.year, month=birthday.month, day=birthday.day)

def random_email(local_length=10, sub_domain_length=5, top_domain=".com"):
    return "{local}@{sub_domain}{top_domain}".format(
        local=random_string(local_length),
        sub_domain=random_string(sub_domain_length),
        top_domain=top_domain
    )

def random_string(length=15):
    return generate_words(3)

def random_account(username=None, password=None, email=None, count=1):
    username = random_string() if username is None else str(username)
    password = random_string() if password is None else str(password)
    email = random_email() if email is None else str(email)
    birthday = random_birthday()
    if count > 1:
        em = email.split("@")
        email = em[0] + "+" + username + "@" + em[1]
    return {'username':username, 'password':password, 'email':email, 'birthday':birthday}
    