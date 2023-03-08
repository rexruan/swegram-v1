#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings

from django.shortcuts import render, HttpResponse

from django.contrib.auth.models import User

def start_swedish(request):
    if request.session.get('language') == 'en':
        if request.session.get('file_list'):
            del request.session['file_list']
        if request.session.get('text_list'):
            del request.session['text_list']
    request.session['language'] = 'sv'
    return render(request, 'swegram_main/start_sv.html')

def start_english(request):
    from django.core.management import call_command
    call_command('createcachetable', database='default')
    if request.session.get('language') == 'sv':
        if request.session.get('file_list'):
            del request.session['file_list']
        if request.session.get('text_list'):
            del request.session['text_list']
    request.session['language'] = 'en'
    request.session.modified = True
    return render(request, 'swegram_main_english/start_en.html')

def swegram_main_swedish(request):
    if request.session.get('language') == 'en':
        if request.session.get('file_list'):
            del request.session['file_list']
        if request.session.get('text_list'):
            del request.session['text_list']
    request.session['language'] = 'sv'
    if request.session.get('file_list') and request.session.get('text_list'):
        request.session['text_list'] = sum([[text for text in file.texts] for file in request.session['file_list'] if file.activated], [])

    context = {}
    if settings.PRODUCTION:
        context['url'] = '/swegram'

    return render(request, "swegram_main/main.html", context)

def swegram_main_english(request):
    if request.session.get('language') == 'sv':
        if request.session.get('file_list'):
            del request.session['file_list']
        if request.session.get('text_list'):
            del request.session['text_list']
    request.session['language'] = 'en'
    if request.session.get('file_list') and request.session.get('text_list'):
        request.session['text_list'] = sum([[text for text in file.texts] for file in request.session['file_list'] if file.activated], [])

    context = {}
    if settings.PRODUCTION:
        context['url'] = '/swegram'

    return render(request, "swegram_main_english/main.html", context)
