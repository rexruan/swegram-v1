from django.conf.urls import url

from . import views
from handle_texts.upload_file import upload_annotated_file, annotate_uploaded_file
from handle_texts.helpers import update_sidebar, download_file, set_filename,\
visualise_text, edit_token, set_stats_type, update_metadata, download_stats, download_all
from handle_texts.statistics import get_pos_stats, get_freq_list,\
get_general_stats, get_length, get_readability

app_name = 'swegram'
urlpatterns = [
    url(r'^$', views.start_swedish, name='start_swedish'),
    url(r'^en/$', views.start_english, name='start_english'),
    url(r'^swedish/$', views.swegram_main_swedish, name='swegram_main_swedish'),
    url(r'^english/$', views.swegram_main_english, name='swegram_main_english'),
    url(r'^upload_annotate/$', annotate_uploaded_file, name="annotate_uploaded_file"),
    url(r'^upload/$', upload_annotated_file, name="upload_annotated_file"),
    url(r'^update_sidebar/$', update_sidebar, name='update_sidebar'),

    url(r'^pos_stats/$', get_pos_stats, name='get_pos_stats'),
    url(r'^get_freq_list/$', get_freq_list, name='get_freq_list'),
    url(r'^get_general_stats/$', get_general_stats, name='get_general_stats'),
    url(r'^lengths/$', get_length, name='get_length'),
    url(r'^readability/$', get_readability, name='get_readability'),
    url(r'^visualise/$', visualise_text, name='visualise_text'),
    url(r'^edit_token/$', edit_token, name='edit_token'),
    url(r'^set_stats_type/$', set_stats_type, name='set_stats_type'),
    url(r'^update_metadata/$', update_metadata, name='update_metadata'),

    url(r'^download_all/$', download_all, name='download_all'),

    url(r'^set_filename/$', set_filename, name='set_filename'),
    url(r'^dl/(?P<file_id>.*)/$', download_file, name='download_file'),


    url(r'^get_stats/$', download_stats, name='download_stats'),
]
