#-*- coding: utf-8 -*-

import codecs, sys, re
from utils.csvwrapper import *
from utils.tokenize import *
import pymongo


class WordData:

    def __init__(self):
        self.adjetivos_femeninos = []
        self.adjetivos_masculinos = []
        self.calificativos = []
        self.conyuges = []
        self.infinitivos = []
        self.sustantivos_femeninos = []
        self.sustantivos_masculinos = []
        self.verbos = []
        self.verbos_modales = []
        self.vinculos_masculinos = []
        self.vinculos_femeninos = []
        self.read_gender_data_from_file()

    def words(self, f):
        """returns a list of words read from a file - one word per line"""
        return [w.strip() for w in codecs.open(f, 'r', 'utf-8').readlines()]
    
    def read_gender_data_from_file(self):
        self.vinculos_femeninos     = self.words("/Users/melisabok/tesis/data/vinculos_femeninos.txt")
        self.vinculos_masculinos    = self.words("/Users/melisabok/tesis/data/vinculos_masculinos.txt")
        self.conyuges               = self.vinculos_femeninos + self.vinculos_masculinos
        self.adjetivos_femeninos    = self.words("/Users/melisabok/tesis/data/adjetivos_femeninos_con_participios.txt")
        self.adjetivos_masculinos   = self.words("/Users/melisabok/tesis/data/adjetivos_masculinos_con_participios.txt")
        self.sustantivos_femeninos  = self.words("/Users/melisabok/tesis/data/sustantivos_femeninos.txt")
        self.sustantivos_masculinos = self.words("/Users/melisabok/tesis/data/sustantivos_masculinos.txt")
        self.calificativos          = self.adjetivos_femeninos + self.adjetivos_masculinos + self.sustantivos_femeninos + self.sustantivos_masculinos #words("../data/calificativos.txt")
        self.infinitivos            = self.words("/Users/melisabok/tesis/data/infinitivos.txt")
        self.verbos                 = self.words("/Users/melisabok/tesis/data/verbos.txt")
        self.verbos_modales         = self.words("/Users/melisabok/tesis/data/verbos_modales.txt")
        # sanity check : data files are not empty
        for x in [self.vinculos_femeninos, self.vinculos_masculinos, self.conyuges, self.adjetivos_femeninos, self.adjetivos_masculinos, self.sustantivos_femeninos, self.sustantivos_masculinos, self.calificativos, self.infinitivos, self.verbos_modales, self.verbos]:
            assert x != []

class SlotStructure(object):
    def __init__(self, sentence, gendered_words):
        self.calificativo = u''
        self.conyuge      = u''
        self.infinitivo   = u''
        self.posesivo     = u''
        self.verbo        = u''
        self.verbo_modal  = u''
        
        self.calificativo_i = -1
        self.conyuge_i      = -1
        self.infinitivo_i   = -1
        self.posesivo_i     = -1
        self.verbo_i        = -1
        self.verbo_modal_i  = -1

        self.nosotras = u''

        self.gendered_words = gendered_words
        self.gender = "UNKNOWN"
        self.posesivos = [u'mi', u'mis']
        self.sentence = sentence
        self.tokens = [t.lower() for t in token_regex.findall(self.sentence)]
        
    def llena_por_verbo(self):
        if (self.verbo != u'') and (self.calificativo != u''): # | soy | rica |
            return True
        if (self.verbo_modal != u'') and (self.infinitivo != u'') and (self.calificativo != u''): # | quiero | ser | rica |
            return True
        return False

    def llena_por_conyuge(self):
        if (self.posesivo != u'') and (self.conyuge != u''): # | mi | (ex-) mujer |
            return True
        return False

    def llena_por_calificativo(self):
        if (self.calificativo != u''):
            return True
        return False

    def fill_slots(self):

        def in_tokens(a_list, tokens):
            for e in a_list:
                if e in tokens:
                    return (e, tokens.index(e))
            return (u'', -1)

        n, ni   = in_tokens([u'nosotras',], self.tokens)
        vm, vmi = in_tokens(self.gendered_words.verbos_modales, self.tokens)
        i, ii   = in_tokens(self.gendered_words.infinitivos, self.tokens)
        v, vi   = in_tokens(self.gendered_words.verbos, self.tokens)
        c, ci   = in_tokens(self.gendered_words.calificativos, self.tokens)
        p, pi   = in_tokens(self.posesivos, self.tokens)
        co, coi = in_tokens(self.gendered_words.conyuges, self.tokens)
        #print 'n: ' + n
        #print 'verbos modales: ' + vm
        #print 'infinitivos: ' + i
        #print 'verbos: ' + v
        #print 'calificativos: ' + c
        #print 'posesivos: ' + p
        #print 'conyuges: ' + co
        
        if ni != -1:
            self.nosotras = n
            self.nosotras_i = ni
        if (pi < coi) and (coi - pi <= 2):
            self.posesivo = p
            self.conyuge  = co
            self.posesivo_i = pi
            self.conyuge_i  = coi
        if (vmi < ii) and (ii < ci) and (ci - ii <= 2):
            self.verbo_modal    = vm
            self.infinitivo     = i
            self.calificativo   = c
            self.verbo_modal_i  = vmi
            self.infinitivo_i   = ii
            self.calificativo_i = ci
        elif (vi < ci) and (ci - vi <= 2):
            self.verbo          = v
            self.calificativo   = c
            self.verbo_i        = vi
            self.calificativo_i = ci
        elif (ci != -1):
            self.calificativo   = c
            self.calificativo_i = ci

        
    def calculate_gender(self):
        if self.nosotras != u'':
            self.gender = "Female"
            return
        if self.llena_por_verbo():
            #print 'llena por verbo: ' + self.calificativo
            if (self.calificativo in self.gendered_words.adjetivos_femeninos) or (self.calificativo in self.gendered_words.sustantivos_femeninos):
                self.gender = "Female"
                return
            elif (self.calificativo in self.gendered_words.adjetivos_masculinos) or (self.calificativo in self.gendered_words.sustantivos_masculinos):
                self.gender = "Male"
                return
        if self.llena_por_conyuge():
            #print 'llena por conyuge: ' + self.conyuge
            if (self.conyuge in self.gendered_words.vinculos_femeninos):
                self.gender = "Male"
                return
            elif (self.conyuge in self.gendered_words.vinculos_masculinos):
                self.gender = "Female"
                return
        #if self.llena_por_calificativo():
        #    print 'llena por calificativo: ' + self.calificativo
        #    if (self.calificativo in self.gendered_words.adjetivos_femeninos) or (self.calificativo in self.gendered_words.sustantivos_femeninos):
        #        self.gender = "Female"
        #        return
        #    elif (self.calificativo in self.gendered_words.adjetivos_masculinos) or (self.calificativo in self.gendered_words.sustantivos_masculinos):
        #        self.gender = "Male"
        #        return
        else:
            self.gender = "UNKNOWN"

    def __repr__(self):
        if self.verbo != u'':
            slot2 = self.verbo
        elif self.infinitivo != u'':
            slot2 = self.infinitivo
        else:
            slot2 = u''
        return "| %s | %s | %s |" % (self.verbo_modal.encode('utf-8'), slot2.encode('utf-8'), self.calificativo.encode('utf-8'))
        # if self.llena_por_verbo():
        #     if self.verbo != u'':
        #         slot2 = self.verbo
        #     elif self.infinitivo != u'':
        #         slot2 = self.infinitivo
        #     else:
        #         slot2 = u''
        #     return "| %s | %s | %s |" % (self.verbo_modal.encode('utf-8'), slot2.encode('utf-8'), self.calificativo.encode('utf-8'))
        # if self.llena_por_conyuge():
        #     return "| %s | %s |" % (self.posesivo.encode('utf-8'), self.conyuge.encode('utf-8'))


class GenderSlots:
    def __init__(self):
        self.sentence_delimiters = re.compile(r"""\.|,|\bporque\b|\bcual\b|\bcuál\b|\bcuáles\b|\bcuales\b|\bquien\b|\bquién\b|\bquienes\b|\bque\b|\bqué\b|\bquiénes\b|\baunque\b|\bcuando\b|\bsi\b|\bpero\b|\by\b|\bo\b|:|[¿!¡;]+|(\?)+|\.\.\.""", re.U|re.X|re.I)
        self.gendered_words = WordData()

    def get_sentences(self, text):
        return [sentence.strip() for sentence in \
        self.sentence_delimiters.split(text) if sentence and (len(sentence) > 2)]

    def get_gender(self, text):
        text = limpieza_inicial(text)
        if text == u'':
            return u'UNKNOWN'
        text_sentences = self.get_sentences(text)
        for sentence in text_sentences:
            s = SlotStructure(sentence, self.gendered_words)
            s.fill_slots()
            s.calculate_gender()
            if s.gender != u'UNKNOWN':
                return s.gender
        return u'UNKNOWN'



#res = GenderSlots().get_gender("Soy programadora")
#print res

if __name__ == '__main__':
    var = raw_input("Please enter something: ")
    print "Get gender for: " + var
    print GenderSlots().get_gender(var)

