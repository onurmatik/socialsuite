#encoding:utf-8
from gexf import Gexf
from django.views.decorators.cache import cache_page
from genelizleyici.tweets.models import Tweet, Hashtag
from genelizleyici.vekiller.models import Stats
from django.http import JsonResponse


@cache_page(60 * 60 * 24, key_prefix="graph:trends")
def trends(request):
    params = {k: v for k, v in request.GET.iteritems()}
    return JsonResponse(
        list(Stats.objects.trends(**params)),
        safe=False,
    )


@cache_page(60 * 60 * 1, key_prefix="graph:network")
def mp_tag(request):
    """
    Sigma network graph of the tag - mp relations
    """
    params = {k: v for k, v in request.GET.iteritems()}

    graph = {
        'nodes': [],
        'edges': [],
    }
    ids = []  # to avoid duplicates

    qs = Tweet.objects.get_tags(**params)
    if not (params.has_key('mv') or params.has_key('konu')):
        qs = qs.filter(total__gt=1)
    qs = qs[:params.get('limit') or 6]
    for item in qs:
        tag_id = 't%s' % item['tag__id']
        if not tag_id in ids:
            ids.append(tag_id)
            graph['nodes'].append({
                'id': tag_id,
                'label': item['tag__name'],
            })
        # mps
        mps = Tweet.objects.filter(hashtags__id=item['tag__id']).values('vekil__id', 'vekil__isim', 'vekil__parti').distinct()
        for mp in mps:
            mp_id = 'm%s' % mp['vekil__id']
            if not mp_id in ids:
                ids.append(mp_id)
                graph['nodes'].append({
                    'id': mp_id,
                    'label': mp['vekil__isim'],
                    'parti': mp['vekil__parti'],
                })

            edge_id = '%s-%s' % (tag_id, mp_id)
            if not edge_id in ids:
                ids.append(edge_id)
                graph['edges'].append({
                    'id': edge_id,
                    'source': mp_id,
                    'target': tag_id,
                })
        # related tags
        """
        related_tags = Hashtag.objects.get(id=item['tag__id']).related_tags[:params.get('limit') or 3]
        for tag in related_tags:
            related_tag_id = 't%s' % tag['tag__id']
            if not related_tag_id in ids:
                ids.append(related_tag_id)
                graph['nodes'].append({
                    'id': related_tag_id,
                    'label': tag['tag__name'],
                })
            # tag - related_tag edges
            edge_id = '%s-%s' % (tag_id, related_tag_id)
            if not edge_id in ids:
                ids.append(edge_id)
                graph['edges'].append({
                    'id': edge_id,
                    'source': tag_id,
                    'target': related_tag_id,
                })
        """
    return JsonResponse(graph, safe=False)


def mp_tag_export(request, format='gexf'):
    if format == 'gexf':
        gexf = Gexf("Genelizleyici.com", "Milletvekilleri - Konular")
        graph = gexf.addGraph("undirected", "static", "mp - hashtags")

        for node in nodes:
            n = graph.addNode(
                node['id'],
                node['label'],
            )

        for edge in edges:
            e = graph.addEdge(
                '%s|%s' % (edge['tag__slug'], edge['vekil__slug']),
                edge['vekil__slug'],
                edge['tag__slug'],
            )

        f = open('test.gexf', 'w')
        gexf.write(f)
        f.close()

