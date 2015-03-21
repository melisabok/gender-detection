#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re, unidecode

token_regex = re.compile(r'\w+|#[a-zA-Z0-9_]+|:\)|:\(|\w+\'\w+|\w+', re.U|re.I)

#repeat_regex = re.compile(r'(\w*)(\w)\2(\w*)')
repeat_regex = re.compile(r'(\w*)([abdefghijkmnñopqstuvwxyzABDEFGHIJKMNÑOPQSTUVWXYZáéíóúÁÉÍÓÚ])\2(\w*)')
replacement = r'\1\2\3'

token_regex_para_lev = re.compile(r'@\w+|#[a-zA-Z0-9_]+|:\)|:\(|\w+\'\w+|\w+|\?+', re.U|re.I)

#tweet_delimiters = re.compile(r"""<< |                               
                                  # >> |                               
                                  # >  |                               
                                  # <""", re.U|re.X)                   

#sentence_delimiters = re.compile(r"""\.|,|\bporque\b|\bcual\b|\bcuál\b|\bcuáles\b|\bcuales\b|\bquien\b|\bquién\b|\bquienes\b|\bque\b|\bqué\b|\bquiénes\b|\baunque\b|\bcuando\b|\bsi\b|\bpero\b|\by\b|\bo\b|:|[¿!¡;]+|(\?)+|\.\.\.""", re.U|re.X|re.I)

def q(s):
    return '"%s"' % s

def limpieza_inicial(s):
    # estos replaces están porque Freeling reemplaza estos signos (si están solos) por 'y'
    s = s.replace(u"'", '')
    s = s.replace(u'"', '')
    s = s.replace(u'¡', '.')
    s = s.replace(u'!', '.')
    s = s.replace(u'¿', '.')
    s = s.replace(u'“', '')
    s = s.replace(u'‘', '')
    s = s.replace(u'’', '')
    s = s.replace(u'…', '')
    s = s.replace(u'”', '')
    #s = s.replace(u'RT', '')
    s = s.replace(u'¿', '.')
    s = re.sub(r'\?+', u'?', s)
    s = re.sub(r'\bq\b', u' que ',s)
    s = s.replace(u'#', '')
    s = re.sub(r'http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?', u'', s)
    return s

def replace_repeated_letters(token):
    replaced_token = re.sub(repeat_regex, replacement, token)
    if replaced_token != token:
        return replace_repeated_letters(replaced_token)
    else:
        return replaced_token

def normalize_and_tokenize(text, regex=r'\w+'):
    return [unidecode.unidecode(w).lower() for w in re.findall(regex, text)]
