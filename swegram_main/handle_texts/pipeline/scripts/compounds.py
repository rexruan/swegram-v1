#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from process import list_to_file, file_to_list
import os
from pycut import cut
from django.conf import settings

def find_compounds(tagged_file):
    debug = settings.DEBUG
    PIPE_DIR        = os.path.realpath(__file__).replace(os.path.basename(os.path.realpath(__file__)), '').replace('scripts/', '')

    require_dict_occurrence = True #Requires compounds to be present in a dict

    dict = file_to_list(PIPE_DIR + '/nlp/HistNorm/resources/swedish/levenshtein/saldo-total_wordforms.txt')

    """ Returns a list of integers. If the tokens at position 10 and 11 should
        be merged, 10 is added to the list. """
    def prepare_input(tagged_file):
        """ Returns a list only containing words, SUC tags + morphology, aswell
            as blank lines, to look for compounds to merge """
        return [line.replace('|', '\t', 1) for line in cut("2,5", file_to_list(tagged_file), False)]


    def rule_1(p1, m1, p2, m2):
        if p1 == "PM" and "GEN" in m1 and\
           p2 == "NN" and "DEF" in m2:
            return True
        return False

    def rule_2(p1, m1, p2, m2):
        if p1 == "NN" and "GEN" in m1 and\
           p2 == "NN" and "DEF" in m2:
            return True
        return False

    def rule_3(p1, m1, p2, m2):
        if p1 == "NN" and "NOM" in m1 and "DEF" not in m1 and\
           p2 == "NN" and "DEF" in m2:
            return True
        return False

    decrement = 0
    compounds_list = []
    input = prepare_input(tagged_file)

    for x in range(len(input)):
        if x < len(input) - 1:
            cmpnd = ''.join(input[x].split("\t")[0:1]).lower() +\
                    ''.join(input[x+1].split("\t")[0:1]).lower() + '\n'
            p1    = ''.join(input[x].split("\t")[1:2])
            m1    = ''.join(input[x].split("\t")[2:3])
            p2    = ''.join(input[x+1].split("\t")[1:2])
            m2    = ''.join(input[x+1].split("\t")[2:3])

            if rule_1(p1, m1, p2, m2):
                if require_dict_occurrence and cmpnd not in dict:
                    if debug:
                        print "Not in dict: ", cmpnd
                    pass

                else:
                    if debug:
                        print "In dict: ", cmpnd
                    compounds_list.append(x - decrement)
                    decrement += 1
            elif rule_2(p1, m1, p2, m2):
                if require_dict_occurrence and cmpnd not in dict:
                    if debug:
                        print "Not in dict: ", cmpnd
                    pass

                else:
                    if debug:
                        print "In dict: ", cmpnd
                    compounds_list.append(x - decrement)
                    decrement += 1
            elif rule_3(p1, m1, p2, m2):
                if require_dict_occurrence and cmpnd not in dict:
                    if debug:
                        print "Not in dict: ", cmpnd
                    pass

                else:
                    if debug:
                        print "In dict: ", cmpnd
                    compounds_list.append(x - decrement)
                    decrement += 1
    return compounds_list

def insert_originals(tagged_file, originals, compounds_list):

    # New enumeration for each compound, add the compound to the FORM (1st) column
    for n in compounds_list:
        n1 = tagged_file[n].split("\t")[0]
        n2 = str(int(tagged_file[n].split("\t")[0]) + 1)
        updated_string = n1 + "-" + n2 + '\t' + '\t' + '\t'.join(tagged_file[n].split("\t")[1:])
        del tagged_file[n]
        tagged_file.insert(n, updated_string)

    # Update the enumeration for tokens following compounds (+1)

    enum_increase = 0
    x_increase    = 0
    for x in range(len(tagged_file)):
        if '-' in tagged_file[x].split("\t")[0]:
            x_increase = 1
            while True:
                if "-" in tagged_file[x+x_increase].split("\t")[0]: # If there's more than one compound in a sentence
                    new_n1 = str(int(tagged_file[x+x_increase].split("\t")[0].split("-")[0]) + 1 + enum_increase)
                    new_n2 = str(int(tagged_file[x+x_increase].split("\t")[0].split("-")[1]) + 1 + enum_increase)
                    new_enum = new_n1 + "-" + new_n2
                    updated_string = new_enum + '\t' + '\t'.join(tagged_file[x+x_increase].split("\t")[1:])
                    del tagged_file[x+x_increase]
                    tagged_file.insert(x+x_increase, updated_string)
                    x_increase += 1
                    enum_increase += 1
                    break
                if tagged_file[x+x_increase] == "\n":
                    enum_increase = 0
                    break
                n1 = str(int(tagged_file[x+x_increase].split("\t")[0]) + 1 + enum_increase)
                updated_string = n1 + '\t' + '\t'.join(tagged_file[x+x_increase].split("\t")[1:])
                del tagged_file[x+x_increase]
                tagged_file.insert(x+x_increase, updated_string)
                x_increase += 1

    def is_compound(s):
        if s.split("\t"):
            return True if '-' in s.split("\t")[0] else False

    def get_enumeration(s, n):
        # Returns enumeration for compounds, s is the string, n is
        # whether the first (0) or second (1) number should be returned
        return s.split("\t")[0].split("-")[n]

    increment = 0
    new_list = []

    for x in range(len(tagged_file)):
        if is_compound(tagged_file[x]):
            new_list.append(tagged_file[x])
            n1 = get_enumeration(tagged_file[x], 0)
            n2 = get_enumeration(tagged_file[x], 1)
            new_list.append(n1 + "\t" + originals[x+increment].strip() + "\n")
            new_list.append(n2 + "\t" + originals[x+1+increment].strip() + "\n")
            increment += 1
        elif tagged_file[x] == "\n":
            new_list.append("\n")
        else:
            new_string = ""
            if len(tagged_file[x].split("\t")) > 1:
                enum = tagged_file[x].split("\t")[0]
                form = originals[x+increment].strip()
                new_string = enum + "\t" + form
                for col in tagged_file[x].split("\t")[1:]:
                    new_string += "\t" + col
            new_list.append(new_string)

    return new_list
