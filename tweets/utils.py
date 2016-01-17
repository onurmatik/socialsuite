import re
from unidecode import unidecode
from datetime import datetime
from django.template.defaultfilters import slugify as slgfy


def slugify(s, max_length=50, max_words=None):
    if s == '':
        return s
    slug = slgfy(unidecode(s))
    while len(slug) > max_length:
        # try to shorten word by word
        temp = slug[:slug.rfind('-')]
        if len(temp) > 0:
            slug = temp
        else:
            # we have nothing left, do not apply the last crop, apply the cut-off directly
            slug = slug[:max_length]
            break
    if max_words:
        words = slug.split('-')[:max_words]
        slug = '-'.join(words)
    return slug


def hashify(s):
    # FIXME: (abbreviations) ASAP => Asap
    hash = re.sub(r'((-|^)[a-z])', lambda pat: pat.group(1).upper(), slugify(s)).replace('-', '')
    return hash


def timestamp_to_datetime(ts):
    try:
        return datetime.fromtimestamp(int(ts)/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
    except:
        return None
