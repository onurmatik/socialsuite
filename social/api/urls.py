from django.conf.urls import url
from django.views.generic import TemplateView
from genelizleyici.api.timeline import tweets, replies, tags, tag_detail, mp_list, mp_detail, reply, fav, rt
from genelizleyici.api.graphs import trends, mp_tag, mp_tag_export
from genelizleyici.api.common import update_profile


urlpatterns = [
    # doc
    url(r'^$', TemplateView.as_view(template_name='api.html'), name='api_doc'),

    # timeline
    url(r'^tweets/$', tweets, name='tweets'),
    url(r'^replies/$', replies, name='replies'),

    url(r'^tags/$', tags, name='tags'),
    url(r'^tag/$', tag_detail, name='tag_detail'),

    url(r'^mps/$', mp_list, name='mp_list'),
    url(r'^mp/$', mp_detail, name='mp_detail'),


    # graphs
    url(r'^graph/$', trends, name='graph'),

    url(r'^graph/mp_tag.json$', mp_tag, name='mp_tag_json'),
    url(r'^graph/export/gexf/$', mp_tag_export, {'output': 'gexf'}, name='mp_tag_gexf'),


    # POSTs
    url(r'^reply/$', reply, name='reply'),
    url(r'^fav/$', fav, name='fav'),
    url(r'^rt/$', rt, name='rt'),

    # update profile
    url(r'^update/$', update_profile, name='update_profile'),

]
