from django import template
import pymysql
from movierecommend.config import HOST, PORT, USER_NAME, PASSWD, DATABASE_NAME


register = template.Library()


@register.filter('hash')
def hash(h, key):
    return h[key]


@register.filter('href')
def href(imdbid):
    return "https://www.imdb.com/title/tt" + str(imdbid).rjust(7, '0')


@register.filter('movie_info')
def movie_info(imdbid):
    info = dict()
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('select * from moviegenre3 where imdbId = %s', imdbid)
        rr = cur.fetchone()
        if rr is not None:
            info['imdbid'] = rr[0]
            if rr[1]:
                info['title'] = rr[1][:-7]
                info['year'] = rr[1][-5:-1]
            else:
                info['title'] = 'not valid'
                info['year'] = 'not valid'
    finally:
        conn.close()
    return info


def get_conn():
    conn = pymysql.connect(host=HOST, port=PORT, user=USER_NAME, passwd=PASSWD, db=DATABASE_NAME, charset='utf8')
    return conn