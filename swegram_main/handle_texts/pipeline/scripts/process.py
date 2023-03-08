#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs, os, subprocess, re, shutil
from pycut import cut
from engGramp2 import enggram_spellcheck


# Strings with metadata or paragraphs are replaced with these to avoid
# them being processed, then restored
METADATA_TEMP_FORMAT    = "\nMETAMETADATADATA\n"
PARAGRAPH_TEMP_FORMAT   = "PARAGRAPH"

def str_to_bool(s):
    if type(s) == bool:
        return s
    return True if s.lower() == "true" else False

def list_to_file(list, file):
    f = open(file, 'w')
    f.write(''.join(map(lambda x: str(x), list)))
    f.close()

def file_to_list(file):
    f = open(file)
    list = f.readlines()
    return list

def split_len(l):
    if len(l.split("\t")) > 0:
        return len(l.split("\t"))
    return 0

def set_paragraphs(input_file):
    infile = file_to_list(input_file)
    for x in range(len(infile)):
        if infile[x] == "\n":
            del infile[x]
            infile.insert(x, "\n" + PARAGRAPH_TEMP_FORMAT + "\n\n")
    return infile

def restore_original_tokens(tagged_file, original_token_file):
    updated_tagged_file = []
    tagged = file_to_list(tagged_file)
    original = [l for l in file_to_list(original_token_file)\
                if l.strip() != PARAGRAPH_TEMP_FORMAT.strip()\
                and l.strip() != METADATA_TEMP_FORMAT.strip()\
                and l != '\n']

    for line in tagged:
        spl = line.split('\t')
        if len(spl) > 6:
            updated_line = ""
            updated_line += spl[0]
            updated_line += '\t'
            updated_line += original[0].strip()
            updated_line += '\t'
            updated_line += '\t'.join(spl[1:])
            del original[0]
            updated_tagged_file.append(updated_line)
        else:
            updated_tagged_file.append(line)

    list_to_file(updated_tagged_file, tagged_file)



def separate_pos(input_file):
    # Separates pos tags from the morphology
    infile = file_to_list(input_file)
    for x in range(len(infile)):
        if len(infile[x].split("\t")) > 5:
            columns = infile[x].split("\t")
            if "|" in columns[6]:
                columns[6] = columns[6].replace("|", "\t", 1)
            else:
                columns[6] = columns[6] + "\t_"
            new_line = '\t'.join(columns)
            del infile[x]
            infile.insert(x, new_line)
    return infile

def space_to_underscore(input_file):
    infile = file_to_list(input_file)
    outlist = []
    for l in infile:
        outlist.append(l.replace(" ", "_"))
    list_to_file(outlist, input_file)

def restore_paragraphs(input_file):
    decrement = 0
    infile = file_to_list(input_file)
    for x in range(len(infile)):
        x -= decrement

        if PARAGRAPH_TEMP_FORMAT in [l.strip() for l in infile[x].split("\t")]:

            del infile[x]
            decrement += 1
    return infile

def restore_paragraphs_en(input_file):
    decrement = 0
    infile = file_to_list(input_file)
    for x in range(len(infile)):
        x -= decrement
        if len(infile[x].split("\t")) > 1:
            if infile[x].split("\t")[0] == PARAGRAPH_TEMP_FORMAT:
                del infile[x]
                decrement += 1
    return infile

def set_metadata(input_file, meta_re):
    metadata_list = []
    infile = file_to_list(input_file)
    for x in range(len(infile)):
        if re.match(meta_re, infile[x]) is not None:
            metadata_list.append(infile[x])
            del infile[x]
            infile.insert(x, METADATA_TEMP_FORMAT)
    list_to_file(infile, input_file)
    return metadata_list

def restore_metadata(input_file, metadata_list):
    infile = file_to_list(input_file)

    for x in range(len(infile)):

        if METADATA_TEMP_FORMAT.strip() in infile[x]:
            del infile[x]
            infile.insert(x, metadata_list[0])
            del metadata_list[0]
    return infile

def list_enumeration(input_file, contains_metadata, metadata_format):
    # Enumerate the text
    infile = file_to_list(input_file)

    sentence    = 1
    paragraph   = 1
    first_sentence = False # Keep track of whether it's the first sentence

    if contains_metadata == True:
        for x in range(len(infile)-1):
            if re.match(metadata_format, infile[x]):
                sentence = 1
                paragraph = 1
                first_sentence = True
            elif infile[x] == "\n" and not first_sentence:
                if x < len(infile) and infile[x+1] == "\n":
                    sentence = 0
                    paragraph += 1
                else:
                    sentence += 1
            elif infile[x] != "\n":
                first_sentence = False
                enum_line = str(paragraph) + "." + str(sentence) + "\t" + infile[x]
                del infile[x]
                infile.insert(x,enum_line)
    else:
        first_sentence = True
        for x in range(len(infile)-1):
            if infile[x] == "\n" and not first_sentence:
                if x < len(infile) and infile[x+1] == "\n":
                    sentence = 0
                    paragraph += 1
                else:
                    sentence += 1
            elif infile[x] != "\n":
                first_sentence = False
                enum_line = str(paragraph) + "." + str(sentence) + "\t" + infile[x]
                del infile[x]
                infile.insert(x,enum_line)

    # Remove an empty line if 3 in a row
    decrement = 0
    for x in range(len(infile)-2):
        x -= decrement
        if infile[x] == '\n' and infile[x+1] == '\n' and infile[x+2] == '\n':
            del infile[x+2]
            decrement += 1
    return infile


PYTHON3_DIR     = '/usr/bin/python3.4'
PIPE_DIR        = os.path.realpath(__file__).replace(os.path.basename(os.path.realpath(__file__)), '').replace('scripts/', '')
EFSELAB_DIR     = PIPE_DIR + "nlp/efselab/swe_pipeline.py"
HISTNORM_DIR    = PIPE_DIR + "nlp/HistNorm/"

def tokenize(filename, tokenizer, TMP_DIR, tokenized_file):
    if tokenizer.lower() == "efselab":
        subprocess.call([PYTHON3_DIR, EFSELAB_DIR, '--tokenized', '-o', TMP_DIR, filename])
        return True
    elif tokenizer.lower() == 'udpipe':
        f = open(tokenized_file, 'w')
        subprocess.call([PIPE_DIR + 'nlp/udpipe/udpipe', '--tokenize', PIPE_DIR + 'nlp/udpipe/en/english-ud-2.0-170801.udpipe', filename], stdout=f)
        f.close()

def spellcheck(tokenized_file, spellchecked_file, spellchecker):
    if spellchecker.lower() == 'histnorm':
        f = open(spellchecked_file, 'w')
        subprocess.call(['perl', '-CSAD', HISTNORM_DIR + 'scripts/normalise_levenshtein_elevtexter.perl', tokenized_file, HISTNORM_DIR + 'resources/swedish/levenshtein/swedish.dic', HISTNORM_DIR + 'resources/swedish/levenshtein/swedish.train.txt', HISTNORM_DIR + 'resources/swedish/levenshtein/swedish.corp', 'noweights', HISTNORM_DIR + 'resources/swedish/levenshtein/threshold.swedish.elevtexter.txt'], stdout=f)
    elif spellchecker.lower() == 'histnorm_en':
        enggram_spellcheck(tokenized_file, spellchecked_file)

def compound_check(spellchecked_file, compounds_file, compounds_method):
    pass

def pos_tag(compounds_file, tagged_file, pos_tagger, TMP_DIR):
    cf = file_to_list(compounds_file)

    if pos_tagger.lower() == "efselab":
        subprocess.call([PYTHON3_DIR, EFSELAB_DIR , '--tagged', '--lemmatized', '--parsed', '--skip-tokenization', '-o', TMP_DIR, compounds_file])
        return True
    elif pos_tagger.lower() == 'udpipe':
        f = open(tagged_file, 'w')
        subprocess.call([PIPE_DIR + 'nlp/udpipe/udpipe', '--tag', '--input=vertical', '--parse', PIPE_DIR + 'nlp/udpipe/en/english-ud-2.0-170801.udpipe', compounds_file], stdout=f)
        f.close()
    return False

def pos_tag_en(spellchecked_file, tagged_file, pos_tagger, TMP_DIR):
    if pos_tagger.lower() == "efselab":
        f = open(tagged_file, 'w')
        subprocess.call([PIPE_DIR + 'nlp/efselab/udt_en', 'tag', '--input=vertical', spellchecked_file, PIPE_DIR + 'nlp/efselab/udt-en.bin'], stdout=f)
        f.close()
        return True
    return False
