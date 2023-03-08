#!/usr/bin/env python
# -*- coding: utf-8 -*-

import statistics

import tempfile
import codecs

from datetime import datetime

import shutil

import os

import subprocess

from django.conf import settings

from ..models import UploadedFile

from pipeline import pipeline, pipeline_en

from get_optparse import get_optparse
from helpers import handle_uploaded_file, checkbox_to_bool, add_text_metadata, str_to_bool, get_md5
from .. import config
from import_text import import_textfile
import os
from django.http import JsonResponse

import time

pipe_path       = config.PIPE_PATH
upload_location = config.UPLOAD_LOCATION

def set_session(request, t):

    if not request.session.get('file_list'):
        request.session['file_list'] = [t]
    else:
        request.session['file_list'].append(t)

    if not request.session.get('text_list'):
        request.session['text_list'] = []
        for file in request.session['file_list']:
            for text in file.texts:
                request.session['text_list'].append(text)
    else:
        request.session['text_list'] += [text for text in t.texts]

    add_text_metadata(request, t.file_id)
    request.session.modified = True
    return request

def upload_annotated_file(request):
    handle_uploaded_file(request.FILES['file_to_analyze'])
    filename = str(request.FILES['file_to_analyze'])

    normalized = True # Implement a way to actually check this at some point

    try:
        # File that are already annotated are assumed to be eligible
        t = import_textfile(upload_location + filename, True, normalized)
        if type(t) == str:
            return JsonResponse({'success': 0, 'error_meta': t})
        md5 = get_md5(t)
        try:
            existing = UploadedFile.objects.get(pk=md5)
            t.normalized = existing.normalized
        except:
            pass
    finally:
        os.remove(upload_location + filename)

    if not t:
        return JsonResponse({'success': 0})

    request = set_session(request, t)

    return JsonResponse({'success': 1})

def annotate_uploaded_file(request):
    tmp_dir = tempfile.mkdtemp() + "/" # Used for the pipeline

    normalized = False
    use_paste = False
    pasted_text = None

    for key in request.POST:
        if key == 'use_paste':
            if checkbox_to_bool(request.POST[key]):
                use_paste = True
        elif key == 'pasted_text':
            pasted_text = request.POST[key]
        elif key == 'checkNormalization':
            normalized = checkbox_to_bool(request.POST[key])

    if use_paste:
        tf = tempfile.NamedTemporaryFile(delete=False)
        with codecs.open(tf.name, 'wb', encoding='utf-8') as f:
            f.write(pasted_text)
        file_path = tf.name
        filename = 'paste ' + datetime.now().strftime("%H:%M:%S") + '.txt'
        shutil.move(tf.name, upload_location + filename)
        options = get_optparse(request, upload_location + filename, tmp_dir, custom_filename=filename)

    else:
        handle_uploaded_file(request.FILES['file_to_annotate'])
        filename = str(request.FILES['file_to_annotate'])
        original_filename = filename
        if settings.PRODUCTION and os.path.splitext(filename)[1] != ".txt":
            try:
                subprocess.call(['unoconv', '--format=txt', upload_location + filename])
                stdout_file = open(upload_location + os.path.splitext(filename)[0] + ".txt2", "w")
                subprocess.call(['iconv', '-f', 'iso-8859-1', '-t', 'utf-8', upload_location + os.path.splitext(filename)[0] + ".txt"], stdout=stdout_file)
                shutil.move(upload_location + os.path.splitext(filename)[0] + ".txt2", upload_location + os.path.splitext(filename)[0] + ".txt")
                filename = os.path.splitext(filename)[0] + ".txt"
            finally:
                os.remove(upload_location + original_filename)
        options = get_optparse(request, upload_location + filename, tmp_dir)

    # If the user has removed some column, the text can't be used for analysis

    try:
        if request.session['language'] == 'en':
            annotated_file_path, text_eligible = pipeline_en.run(options)
        else:
            annotated_file_path, text_eligible = pipeline.run(options)
    finally:
        shutil.rmtree(tmp_dir)

    def import_t(request, annotated_file_path, text_eligible, normalized):
        return import_textfile(request, annotated_file_path, text_eligible, normalized)
    # The second arg here is whether to use metadata or not
    try:
        t = import_t(request, annotated_file_path, text_eligible, normalized)
    finally:
        try:
            os.remove(annotated_file_path)
        except:
            pass

    if not t:
        return JsonResponse({'success': 0})

    if type(t) == str:
        return JsonResponse({'success': 0, 'error_meta': t})

    request = set_session(request, t)

    return JsonResponse({'success': 1})
