#!/usr/bin/env python3

from optparse import OptionParser

def getOptionParser():
    optparse = OptionParser(usage="")

    optparse.add_option("--open", dest="open", metavar="PATH")

    optparse.add_option("--tokenizer", dest="tokenizer", metavar="PATH", default="efselab")
    optparse.add_option("--tagger", dest="tagger", metavar="PATH", default="efselab")
    optparse.add_option("--parser", dest="parser", metavar="PATH", default="maltparser")
    optparse.add_option("--spellchecker", dest="spellchecker", metavar="PATH", default="histnorm")
    optparse.add_option("--compounds-method", dest="compounds_method", metavar="PATH", default="rule_based")

    optparse.add_option("--tokenize", dest="tokenize", metavar="boolean", action="store_true")
    optparse.add_option("--tag", dest="tag", metavar="boolean", action="store_true")
    optparse.add_option("--parse", dest="parse", metavar="boolean", action="store_true")
    optparse.add_option("--normalize", dest="normalize", metavar="boolean", action="store_true")

    optparse.add_option("--tagger-model", dest="tagger_model", metavar="PATH", default="suc3")
    optparse.add_option("--parser-model", dest="parser_model", metavar="PATH", default="maltmodel-UD_Swedish.mco")

    optparse.add_option("--columns", dest="columns", metavar="int,int-int (like cut)")

    optparse.add_option("--preserve-paragraphs", dest="preserve_paragraphs", metavar="bool", default="True")
    optparse.add_option("--preserve-metadata", dest="preserve_metadata", metavar="bool", default="True")
    optparse.add_option("--metadata-format", dest="metadata_format", metavar="regex", default="<.*>")
    return optparse
