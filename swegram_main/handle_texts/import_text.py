#!/usr/bin/env python
# -*- coding: utf-8 -*-

import statistics as statistics
import os
from helpers import rm_blanks, get_md5
from ..config import METADATA_DELIMITER, METADATA_INITIAL, METADATA_FINAL
from django.http import HttpResponse
from datetime import datetime
import filesize

from django.db import IntegrityError

# This counts erroneously split compounds as one word when calculating paragraph count if set to True, otherwise as two words.
paragraph_count_norm_based = True

class Metadata:
    metadata = {}

class Textfile:
    filename = ""
    metadata_labels = None
    raw_contents = None
    raw_contents_list = None
    file_id = None
    file_size = None
    date_added = None

    activated = None

    has_metadata = None
    eligible = None

    meta_added = False

    normalized = False

    texts = []

    def toggle_activate(self):
        self.activated = False if self.activated == True else True
        return self

    def __init__(self, filename, eligible, normalized):
        self.raw_contents = open(filename, 'r').read()
        self.raw_contents_list = open(filename, 'r').readlines()
        self.raw_contents_list = [r.replace('\r', '') for r in self.raw_contents_list]
        self.filename = os.path.basename(filename)
        self.file_id = id(self)
        self.file_size = filesize.size(os.path.getsize(filename))
        self.date_added = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.eligible = eligible
        self.activated = eligible
        self.normalized = normalized

class Token:
    id = None

    text_id  = None
    token_id = None
    form     = None
    norm     = None
    lemma    = None
    upos     = None
    xpos     = None
    feats    = None
    ufeats   = None
    head     = None
    deprel   = None
    deps     = None
    misc     = None
    length   = None

    normalized = False

    def __init__(self):
        self.id = id(self)

    part_of_fundament = False

    # If corrected compound, include the original tokens
    compound_originals = None

class Sentence:
    tokens = []

class Text:
    text = []
    sentences = []

    # file_id is used to associate a text to a file, used when removing a file
    file_id = None
    filename = None
    id = 0
    metadata = []
    metadata_labels = []
    zip_meta_labels = []

    pos_counts = {}

    total_word_len = 0
    total_token_len = 0

    token_count = 0
    word_count = 0
    sentence_count = 0
    lix = 0
    ovix = 0
    nq_full = 0
    nq_simple = 0
    ttr = 0
    compounds = 0
    misspells = 0
    avg_word_len = 0
    avg_sent_len = 0
    freqlist_form = {}
    freqlist_norm = {}
    freqlist_lemma = {}

    paragraphs = [] # contains ints of lengths for each paragraph
    paragraph_sents = []

    eligible = False
    activated = False

    normalized = False

    def toggle_activate(self):
        self.activated = False if self.activated == True else True
        return self

    content_words = [] # non-MAD,PAD,MID words

    def __init__(self, file_id, eligible, normalized):
        self.file_id = file_id
        self.id = id(self)
        self.eligible = eligible
        self.activated = eligible
        self.normalized = normalized

def get_text_stats(request, text):
    # Saker som måste optimeras:
    # läsbarhetsberäkning
    # frekvenslistor

    if request.session['language'] == 'en':
        line_length = 12
    else:
        line_length = 13

    def create_sentences(text):

        def new_token(t, compound_originals=False):
            token = Token()
            token.text_id  = t[0]
            token.compound_originals = compound_originals
            token.token_id = t[1]
            token.form     = t[2].strip()
            if compound_originals:
                token.norm     = "_"
                token.lemma    = "_"
                token.upos     = "_"
                token.xpos     = "_"
                token.feats    = "_"
                token.ufeats   = "_"
                token.head     = "_"
                token.deprel   = "_"
                token.deps     = "_"
                token.misc     = "_"
            else:
                if request.session['language'] == 'en':
                    token.norm     = t[3]
                    token.lemma    = t[4]
                    token.upos     = t[6]
                    token.xpos     = t[5]
                    token.feats    = t[7]
                    token.head     = t[8]
                    token.deprel   = t[9]
                    token.deps     = t[10]
                    token.misc     = t[11]
                else:
                    token.norm     = t[3]
                    token.lemma    = t[4]
                    token.upos     = t[5]
                    token.xpos     = t[6]
                    token.feats    = t[7]
                    token.ufeats   = t[8]
                    token.head     = t[9]
                    token.deprel   = t[10]
                    token.deps     = t[11]
                    token.misc     = t[12]

            token.length = len(token.norm)

            if token.form != token.norm:
                token.normalized = True

            return token

        sentences = []
        sentence = Sentence()
        sentence.tokens = []

        for x in range(len(text.text)):
            split_line = text.text[x].split("\t")
            if len(split_line) == line_length:
                token = new_token(split_line)
                sentence.tokens.append(token)
            elif len(split_line) == 3:
                token = new_token(split_line, True)
                sentence.tokens.append(token)
            elif split_line[0] == '\n':
                if sentence.tokens:
                    # Check for fundament
                    if request.session['language'] == 'sv':
                        for x in range(len(sentence.tokens)):
                            t = sentence.tokens[x]
                            if 'VerbForm=Fin' in t.ufeats:
                                for tok in sentence.tokens[:x]:
                                    tok.part_of_fundament = True
                                break
                    sentences.append(sentence)
                    sentence = Sentence()
                    sentence.tokens = []
        return sentences



    text.sentences = create_sentences(text)
    text.token_count = statistics.token_count_text(text)
    text.word_count = statistics.word_count_text(text)
    text.avg_word_len = statistics.avg_word_len_text(text)
    text.sentence_count = len(text.sentences)
    text.avg_sent_len = statistics.avg_sent_len_text(text)

    text.lix, _ = statistics.lix([text])
    text.ovix, _, text.ttr, _ = statistics.ovix_ttr([text])
    text.nq_simple, text.nq_full, _, _ = statistics.nominal_quota([text])

    text.total_token_len
    text.total_word_len

    text.misspells = statistics.misspells_text(text)
    text.compounds = statistics.compound_count_text(text)

    text.freqlist_form = statistics.freq_list(text, 'form')
    text.freqlist_norm = statistics.freq_list(text, 'norm')
    text.freqlist_lemma = statistics.freq_list(text, 'lemma')

    paragraphs = []
    paragraph_sents = []
    paragraph_token_count = 0
    current_paragraph = 1
    current_sent_count = 0

    for sentence in text.sentences:
        for token in sentence.tokens:
            if int(token.text_id.split(".")[1]) > current_sent_count:
                current_sent_count = int(token.text_id.split(".")[1])
            if not paragraph_count_norm_based:
                if '-' in token.token_id:
                    paragraph_token_count += 1
            if int(token.text_id.split(".")[0]) > current_paragraph:
                paragraph_sents.append(current_sent_count)
                current_sent_count = 0
                paragraphs.append(paragraph_token_count)
                if token.upos not in ['PUNCT']:
                    paragraph_token_count = 1
                current_paragraph += 1
            elif token.upos not in ['PUNCT']:
                paragraph_token_count += 1
    paragraph_sents.append(current_sent_count)
    paragraphs.append(paragraph_token_count)


    text.paragraphs = paragraphs
    text.paragraph_sents = paragraph_sents

    for sentence in text.sentences:
        for token in sentence.tokens:
            if token.upos in ['PUNCT']:
                text.total_token_len += token.length
            else:
                text.content_words.append(token)
                text.total_token_len += token.length
                text.total_word_len += token.length

    return text

def import_textfile(request, path, eligible, normalized, check_if_normalized=False):

    T = Textfile(path, eligible, normalized)

    text_list = T.raw_contents_list

    file_id = T.file_id

    list_of_texts = []

    text_list = rm_blanks(text_list)

    #if text_list[0].strip().startswith(METADATA_INITIAL) and\
    #text_list[0].strip().endswith(METADATA_FINAL):
    if METADATA_INITIAL in text_list[0] and METADATA_FINAL in text_list[0]:
        use_metadata = True
        T.has_metadata = True
    else:
        use_metadata = False
        T.has_metadata = False
    if use_metadata:
        metadata_labels = text_list[0].split("<")[1].strip().strip("<>")
        #metadata_labels = text_list[0].strip().strip('<>')
        T.metadata_labels = metadata_labels.split(METADATA_DELIMITER)

        del text_list[0]

        new_text_contents = []
        new_text_metadata = None

        for line in text_list:
            if line.strip().startswith(METADATA_INITIAL) and\
            line.strip().endswith(METADATA_FINAL): # If we found some metadata

                # If the metadata of a text doesn't match the labels,
                # return false and the erroneous metadata
                if len(line.strip('<> \n').split(METADATA_DELIMITER)) != len(metadata_labels.split(METADATA_DELIMITER)):
                    return line.strip('<> \n')

                if new_text_metadata: # If there's already a text to add
                    t = Text(file_id, eligible, normalized)
                    t.text = new_text_contents
                    t.metadata = new_text_metadata.split(METADATA_DELIMITER)
                    t.metadata_labels = metadata_labels.split(METADATA_DELIMITER)
                    if eligible:
                        t = get_text_stats(request, t)
                    list_of_texts.append(t)

                    new_text_contents = []
                    new_text_metadata = line.strip().strip('<>')

                else: # If it's the first encounter
                    new_text_metadata = line.strip().strip('<>')

            else: # If not metadata, just add the line to the text
                 new_text_contents.append(line)
        t = Text(file_id, eligible, normalized)
        t.filename = T.filename
        t.text = new_text_contents
        t.metadata = new_text_metadata.split(METADATA_DELIMITER)
        t.metadata_labels = metadata_labels.split(METADATA_DELIMITER)
        if eligible:
            t = get_text_stats(request, t)
        list_of_texts.append(t)

    else: # If we aren't using metadata
        t = Text(file_id, eligible, normalized)
        t.filename = T.filename
        t.metadata = None         # Change this?
        t.metadata_labels = None  # Change this?
        t.text = text_list
        if eligible:
            t = get_text_stats(request, t)
        list_of_texts.append(t)

    for text in list_of_texts:
        pos_counts = {}
        for sentence in text.sentences:
            for token in sentence.tokens:
                if token.xpos != '_':
                    if token.xpos in pos_counts:
                        pos_counts[token.xpos] += 1
                    else:
                        pos_counts[token.xpos] = 1

        #text.pos_counts = sorted(pos_counts, key=pos_counts.get, reverse=True)
        text.pos_counts = pos_counts
        for key in text.pos_counts:
            percentage = str(round(float(text.pos_counts[key]) / text.token_count * 100, 2))
            if len(percentage.split(".")[1]) == 1:
                percentage += '0'
            percentage += '%'
            text.pos_counts[key] = (text.pos_counts[key], percentage)
        pos_counts = {}

    T.texts = list_of_texts

    return T
