#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import config

upload_location = config.UPLOAD_LOCATION

from django.core.signals import request_finished

from django.http import JsonResponse, HttpResponse

from tempfile import NamedTemporaryFile
from wsgiref.util import FileWrapper
from django.utils.encoding import smart_str

from datetime import datetime

import os, csv

import statistics

from ..models import UploadedFile

def median(lst):
    n = len(lst)
    if n < 1:
            return None
    if n % 2 == 1:
            return sorted(lst)[n//2]
    else:
            return sum(sorted(lst)[n//2-1:n//2+1])/2.0

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def syllable_count_en(word):
    word = word.lower()
    count = 0
    vowels = "aoueiy"
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count += 1
    return count

def download_all(request):


    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stats.csv"'

    writer = csv.writer(response, delimiter='\t')

    writer.writerow(['Statistik för enskilda texter, ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

    delimiter = 'period'
    include_pos = False
    include_general = False
    include_freq = False
    include_readability = False

    lessthan_n = 3
    morethan_n = 3
    equals_n = 3

    if request.session.get('freq_type'):
        freq_type = request.session.get('freq_type')
    else:
        freq_type = 'norm'

    freq_limit = 25
    if request.GET.get('freq_limit'):
        freq_limit = int(request.GET.get('freq_limit'))

    if request.GET.get('delimiter'):
        delimiter = request.GET.get('delimiter')

    delimiter = delimiter.replace('period', '.').replace('comma', ',')


    if request.session.get('lessthan_n'):
        lessthan_n = request.session['lessthan_n']
    if request.session.get('morethan_n'):
        morethan_n = request.session['morethan_n']
    if request.session.get('equals_n'):
        equals_n = request.session['equals_n']


    for text in request.session['text_list']:
        writer.writerow([])
        writer.writerow([])
        writer.writerow([' '.join(text.metadata)])
        writer.writerow([])

        if request.GET.get('general'):
            writer.writerow(['Allmän statistik'])
            def get_total_wordlen(t):
                lens = []
                for s in t.sentences:
                    for token in s.tokens:
                        if token.xpos not in ['MAD', 'MID', 'PAD']:
                            lens.append(len(token.norm))
                return lens
            def get_total_sentlen(t):
                lens = []
                for s in t.sentences:
                    lens.append(len([t for t in s.tokens if t.xpos not in ['MID','MAD','PAD']]))
                return lens

            wordlens = get_total_wordlen(text)
            sentlens = get_total_sentlen(text)

            writer.writerow(['Tokens'] + [text.token_count])
            writer.writerow(['Ord'] + [text.word_count])
            writer.writerow(['Ordlängd, medelvärde'] + [round(mean(wordlens), 2)])
            writer.writerow(['Ordlängd, median'] + [round(median(wordlens), 2)])
            writer.writerow(['Meningslängd, medelvärde'] + [round(mean(sentlens), 2)])
            writer.writerow(['Meningslängd, median'] + [round(median(sentlens), 2)])
            writer.writerow(['Felstavningar'] + [text.misspells])
            writer.writerow(['Särskrivningar'] + [text.compounds])
            writer.writerow(['Ord mer fler än ' + str(morethan_n) + ' tecken: '\
            + str(statistics.calculate_lengths([text], 'morethan', morethan_n, 'words'))])
            writer.writerow(['Ord mer färre än ' + str(lessthan_n) + ' tecken: '\
            + str(statistics.calculate_lengths([text], 'lessthan', lessthan_n, 'words'))])
            writer.writerow(['Ord mer exakt ' + str(equals_n) + ' tecken: '\
            + str(statistics.calculate_lengths([text], 'equal', equals_n, 'words'))])

        if request.GET.get('pos'):
            writer.writerow([])
            writer.writerow(['# Ordklasstatistik'])
            for key in sorted(text.pos_counts.keys(), key = lambda x: text.pos_counts[x][0], reverse = True):

                writer.writerow([key] + [text.pos_counts[key][0]] + [text.pos_counts[key][1].replace('.', delimiter)])
        if request.GET.get('freq'):
            writer.writerow([])
            writer.writerow(['# Frekvensordlista'])
            writer.writerow(['#'] + ['Token'] + ['POS'] + ['Antal'] + ['Andel'])
            freqs = getattr(text, 'freqlist_' + freq_type)
            if len(freqs) > freq_limit:
                for x in range(freq_limit):
                    writer.writerow(
                                    [str(freqs[x][0])] +
                                    [freqs[x][1].split('_')[0]] +
                                    [freqs[x][1].split('_')[1]] +
                                    [str(freqs[x][2])] +
                                    [str(freqs[x][3])]
                                    )

        if request.GET.get('readability'):
            writer.writerow([])
            writer.writerow(['# Läsbarhet'])
            writer.writerow(['LIX'] + [text.lix])
            writer.writerow(['OVIX'] + [text.ovix])
            writer.writerow(['Enkel nominalkvot'] + [text.nq_simple])
            writer.writerow(['Full nominalkvot'] + [text.nq_full])
            writer.writerow(['Type-token ratio'] + [text.ttr])



    return response

def download_stats(request):

    # Unfinished
    # Pure JS seems to be working fine so using that for the moment

    return JsonResponse({})

    translations = {
                    'Fullnominalkvot': 'Full nominalkvot',
    }

    pos = {}
    freq = {}
    general = {}
    readability = {}

    for prop in request.GET:
        split = prop.split("_")
        if split[0] == 'pos':
            pos[split[1]] = '\t'.join(request.GET[prop].replace('__', '_').split('_'))
        elif split[0] == 'freq':
            freq[split[1]] = '\t'.join(request.GET[prop].replace('__', '_').split('_'))
        elif split[0] == 'general':
            general[split[1]] = '\t'.join(request.GET[prop].replace('__', '_').split('_'))
        elif split[0] == 'readability':
            readability[split[1]] = '\t'.join(request.GET[prop].replace('__', '_').split('_'))

    stats = ''

    if general:
        stats += u'#Allmän statistik\n\n'
        for key in general:
            stats += key + '\t' + general[key] + '\n'

    if readability:
        stats += u'#Läsbarhet\n\n'
        for key in readability:
            stats += key + '\t' + readability[key] + '\n'

    return JsonResponse({})
    pass

def set_stats_type(request):
    text_id = None
    for prop in request.GET:
        if prop == 'id':
            text_id = request.GET[prop]

    if text_id == 'all_texts':
        if request.session['single_text']:
            del request.session['single_text']
        request.session['text_list'] = sum([[text for text in file.texts] for file in request.session['file_list']], [])
    else:
        texts = sum([file.texts for file in request.session['file_list']], [])
        request.session['single_text'] = [text for text in texts if text.id == int(text_id)]

    return JsonResponse({})

def visualise_text(request):
    t = None
    text_id = None

    for prop in request.GET:
        if prop == 'text_id':
            text_id = int(request.GET[prop])

    for text in request.session['text_list']:
        if text.id == text_id:
            t = text


    if t.metadata:
        metadata = ' '.join(t.metadata)
    else:
        metadata = config.NO_METADATA_STRING

    data = {
            'metadata': metadata,
            'sentences': [[token.__dict__ for token in sentence.tokens] for sentence in t.sentences],
            'pos_list': sorted(t.pos_counts.keys()),
            'text_id': t.id
           }


    return JsonResponse(data)

def set_filename(request):
    new_filename = None
    file_id = None

    for prop in request.GET:
        if prop == 'new_filename':
            new_filename = request.GET[prop]
        elif prop == 'file_id':
            file_id = int(request.GET[prop])

    for file in request.session.get('file_list'):
        if file.file_id == file_id:
            file.filename = new_filename

    context = statistics.basic_stats(request.session['text_list'], request)

    return JsonResponse(context)

def edit_token(request):
    text_id = None
    token_id = None
    set_type = None
    new_value = None

    for prop in request.GET:
        if prop == 'text_id':
            text_id = int(request.GET[prop])
        elif prop == 'token_id':
            token_id = int(request.GET[prop])
        elif prop == 'type':
            set_type = request.GET[prop]
        elif prop == 'new_value':
            new_value = request.GET[prop]

    if text_id == None or token_id == None or set_type == None or new_value == None:
        return JsonResponse({})

    text = None
    for t in request.session['text_list']:
        if t.id == text_id:
            for sentence in t.sentences:
                for token in sentence.tokens:
                    if token.id == token_id:
                        setattr(token, set_type, new_value.encode('UTF-8'))

    return JsonResponse({})

from django.utils.encoding import smart_str
def update_metadata(request):
    def invert(bool):
        return not bool

    meta = None
    for prop in request.GET:
        if prop == 'meta':
            meta = request.GET['meta']

    meta_label = smart_str(meta.split("_")[0])
    if '__' in meta:
        meta_prop = '_'
    else:
        meta_prop = smart_str(meta.split("_")[1])
    request.session['metadata'][meta_label][meta_prop][0] = invert(request.session['metadata'][meta_label][meta_prop][0])
    request.session.modified = True
    return JsonResponse({
                        'text_n': len([text for text in request.session['text_list'] if text.eligible]),
                        'texts_selected': 20})

def text_eligibility(request, text):
    if not text.activated:
        return False
    if text.eligible and not text.metadata:

        return True

    metadata_dict = request.session.get('metadata')

    for x in range(len(text.metadata_labels)):
        for y in range(len(text.metadata)):
            if metadata_dict[text.metadata_labels[x]][text.metadata[x]][0] == False:
                return False
    return True


def add_text_metadata(request, file_id):
    if not request.session.get('metadata'):
        request.session['metadata'] = {}

    for file in request.session.get('file_list'):
        if file.has_metadata and file.file_id == file_id and file.activated:
            file.meta_added = True
            for text in file.texts:
                for x in range(len(text.metadata_labels)):

                    if text.metadata_labels[x] in request.session['metadata']:
                        if text.metadata[x] in request.session['metadata'][text.metadata_labels[x]]:
                            request.session['metadata'][text.metadata_labels[x]][text.metadata[x]][1] += 1
                        else:
                            request.session['metadata'][text.metadata_labels[x]][text.metadata[x]] = [True, 1]
                    else:
                        request.session['metadata'][text.metadata_labels[x]] = {text.metadata[x]: [True, 1]}
    request.session.modified = True
    return request

def remove_text_metadata(request, file_id):
    for file in request.session.get('file_list'):
        if file.file_id == file_id and file.meta_added:
            file.meta_added = False
            for text in file.texts:
                for x in range(len(text.metadata_labels)):
                    if text.metadata_labels[x] in request.session['metadata']:
                        if text.metadata[x] in request.session['metadata'][text.metadata_labels[x]]:
                            request.session['metadata'][text.metadata_labels[x]][text.metadata[x]][1] -= 1
                            if request.session['metadata'][text.metadata_labels[x]][text.metadata[x]][1] == 0:
                                del request.session['metadata'][text.metadata_labels[x]][text.metadata[x]]
                            if not request.session['metadata'][text.metadata_labels[x]]:
                                del request.session['metadata'][text.metadata_labels[x]]
    return request

def handle_uploaded_file(f):
    fname = str(f)
    dest = upload_location + fname
    with open(dest, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def str_to_bool(s):
    return True if s.lower() == "true" else False

# Remove any empty lines in the beginning
def rm_blanks(text_list):
    while True:
        if text_list and text_list[0] == '\n':
            del text_list[0]
        else:
            break
    return text_list

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def checkbox_to_bool(s):
    return True if s == "on" else False

def get_md5(file):
    import hashlib
    try:
        mystr = '<' + ' '.join(file.metadata_labels) + '>\n'

        for text in file.texts:
            mystr += '<' + ' '.join(text.metadata) + '>'
            mystr += '\n'
            for sentence in text.sentences:
                for token in sentence.tokens:
                    mystr += \
                    token.text_id + '\t' +\
                    token.token_id + '\t' +\
                    token.form + '\t' +\
                    token.norm + '\t' +\
                    token.lemma + '\t' +\
                    token.upos + '\t' +\
                    token.xpos + '\t' +\
                    token.feats + '\t' +\
                    token.ufeats + '\t' +\
                    token.head + '\t' +\
                    token.deprel + '\t' +\
                    token.deps + '\t' +\
                    token.misc
                mystr += '\n'

        hash_md5 = hashlib.md5()
        hash_md5.update(mystr)
    except:
        return None
    return hash_md5.hexdigest()

def download_file(request, file_id):
    file_to_dl = [f for f in request.session['file_list']\
    if f.file_id == int(file_id)][0]

    f = NamedTemporaryFile(delete=False)

    def test_signal(sender, **kwargs):
        os.remove(f.name)
    request_finished.connect(test_signal, weak=False)
    request_finished.disconnect(test_signal)

    if file_to_dl.metadata_labels:
        f.write('<' + ' '.join(file_to_dl.metadata_labels) + '>\n')

    if file_to_dl.eligible:
        for text in file_to_dl.texts:
            if text.metadata:
                f.write('<' + ' '.join(text.metadata) + '>')
                f.write('\n')
            for sentence in text.sentences:
                for token in sentence.tokens:
                    if request.session['language'] == 'sv':
                        f.write(
                        token.text_id + '\t' +
                        token.token_id + '\t' +
                        token.form + '\t' +
                        token.norm + '\t' +
                        token.lemma + '\t' +
                        token.upos + '\t' +
                        token.xpos + '\t' +
                        token.feats + '\t' +
                        token.ufeats + '\t' +
                        token.head + '\t' +
                        token.deprel + '\t' +
                        token.deps + '\t' +
                        token.misc.strip() + '\n'
                        )
                    else:
                        f.write(
                        token.text_id + '\t' +
                        token.token_id + '\t' +
                        token.form + '\t' +
                        token.norm + '\t' +
                        token.lemma + '\t' +
                        token.upos + '\t' +
                        token.xpos + '\t' +
                        token.feats + '\t' +
                        token.head + '\t' +
                        token.deprel + '\t' +
                        token.deps + '\t' +
                        token.misc.strip() + '\n'
                        )
                f.write('\n')
    else:
        for line in file_to_dl.raw_contents:
            f.write(line)

    f.close()

    try:
        UploadedFile.objects.create(md5_checksum=get_md5(file_to_dl), normalized=file_to_dl.normalized)
    except:
        pass

    response = HttpResponse(FileWrapper(open(f.name)), content_type='application/force-download')

    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_to_dl.filename)

    return response

def update_sidebar(request):
    if not request.session.get('file_list'):
        return JsonResponse({})
    fl = request.session['file_list']
    tl = request.session['text_list']


    for prop in request.GET:
        if prop == 'rm':
            file_to_remove = int(request.GET[prop])
            request = remove_text_metadata(request, file_to_remove)
            request.session['file_list'] = [f for f in fl if f.file_id != file_to_remove]
            request.session['text_list'] = [t for t in tl if t.file_id != file_to_remove]


        elif prop == 'set_state':
            file_to_change = int(request.GET[prop])
            request.session['file_list'] = [f.toggle_activate() if f.file_id == file_to_change else f for f in fl]
            request.session['text_list'] = [t.toggle_activate() if t.file_id == file_to_change else t for t in tl]

            for f in request.session['file_list']:
                if f.file_id == file_to_change:
                    if f.activated:
                        add_text_metadata(request, file_to_change)
                    else:
                        remove_text_metadata(request, file_to_change)

    eligible_texts = statistics.get_text_list(request)

    context = statistics.basic_stats(eligible_texts, request)


    return JsonResponse(context)
