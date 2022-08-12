import logging
from collections import defaultdict

from django.shortcuts import render, redirect,HttpResponseRedirect
from .forms import RegisterForm
from users.models import Resulttable,Insertposter
from django.db import models
from movierecommend.config import MAX_CHAR_NUM
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', context={'form': form})


def index(request):
    max_char_num = MAX_CHAR_NUM
    if request.user.id is not None:
        userId = int(request.user.id) + 1000
        movieId2rating = load_rating_history(userId)
    return render(request, 'users/..//index.html', locals())


def load_rating_history(userId):
    movieId2rating = dict()
    data = Resulttable.objects.filter(userId=userId)
    for row in data:
        movieId2rating[int(row.imdbId)] = int(row.rating)
    return movieId2rating


def check(request):
    return render((request, 'users/..//index.html'))


def showmessage(request):
    if request.user.id is None:
        return redirect('/')
    usermovieid = []
    id2title = dict()
    USERID = int(request.user.id) + 1000
    movieId2rating = load_rating_history(USERID)
    data=Resulttable.objects.filter(userId=USERID)
    for row in data:
        usermovieid.insert(0, row.imdbId)
    try:
        conn = get_conn()
        cur = conn.cursor()
        for i in range(len(usermovieid)):
            cur.execute('select * from moviegenre3 where imdbId = %s', usermovieid[i])
            rr = cur.fetchone()
            if rr is not None:
                title = rr[1]
                id2title[usermovieid[i]] = title
    finally:
        conn.close()
    max_char_num = MAX_CHAR_NUM
    return render(request, 'users/message.html', locals())


def fuzzy_search(request):
    if request.user.id is None:
        return redirect('/')
    userId = int(request.user.id) + 1000
    movieId2rating = load_rating_history(userId)
    keyword = str(request.GET["keyword"])
    max_char_num = MAX_CHAR_NUM
    if keyword == '':
        return redirect('/')
    data = []
    sql = "SELECT * FROM moviegenre3 where (title LIKE '%{}%' or imdbid = '{}')".format(keyword, keyword)
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        rr = cur.fetchall()
        if rr is None:
            print('no item found')
        else:
            for r in rr:
                data.append({'imdbId': r[0], 'title': r[1]})
    finally:
        conn.close()
    return render(request, 'users/fuzzySearch.html', locals())


def recommend2(request):
    if request.user.id is None:
        return redirect('/')
    USERID = int(request.user.id) + 1000
    if (updated[USERID]) or (not Insertposter.objects.filter(userId=USERID).exists()):

        Insertposter.objects.filter(userId=USERID).delete()
        read_mysql_to_csv2('users/static/users_resulttable.csv', USERID)
        ratingfile2 = os.path.join('users/static', 'users_resulttable.csv')
        itemcf = ItemBasedCF()
        userid = str(USERID)
        print(userid)
        itemcf.generate_dataset(ratingfile2)
        itemcf.calc_movie_sim()
        itemcf.recommend(userid)

        try:
            conn = get_conn()
            cur = conn.cursor()
            for i in matrix2:
                cur.execute('select * from moviegenre3 where imdbId = %s',i)
                rr = cur.fetchall()
                for imdbId,title,poster in rr:
                    if(Insertposter.objects.filter(userId=USERID, title=title)):
                        continue
                    else:
                        if title: # title有null的，暂时鸵鸟
                            Insertposter.objects.create(userId=USERID, title=title, poster=imdbId) # 因为海报名就是imdbid.jpg，直接拿imdbid当poster了
                        else:
                            Insertposter.objects.create(userId=USERID, title='not valid', poster=imdbId)

        finally:
            conn.close()

    results = Insertposter.objects.filter(userId=USERID)
    max_char_num = MAX_CHAR_NUM

    # 推荐后，updated[USERID]更新为False
    updated[USERID] = False
    return render(request,'users/movieRecommend2.html', locals())


def insert(request):
    global USERID
    USERID = int(request.GET["userId"])+1000
    RATING = float(request.GET["rating"])
    IMDBID = int(request.GET["imdbId"])
    Resulttable.objects.update_or_create(
        userId=USERID, imdbId=IMDBID,
        defaults={'rating': RATING}
    )
    updated[USERID] = True
    return render(request, ['index.html', 'users/fuzzySearch.html'], {'userId':USERID,'imdbId':IMDBID, 'max_char_num': MAX_CHAR_NUM})


def delete(request):
    global USERID
    USERID = int(request.GET["userId"])+1000
    IMDBID = int(request.GET["imdbId"])

    Resulttable.objects.filter(userId=USERID, imdbId=IMDBID).delete()
    updated[USERID] = True

    return render(request, ['index.html', 'users/fuzzySearch.html'], {'userId':USERID,'imdbId':IMDBID, 'max_char_num': MAX_CHAR_NUM})


import sys
import random
import os,math
from operator import itemgetter
import pymysql
import csv
from django.http import HttpResponse
import codecs
from movierecommend.config import HOST, PORT, USER_NAME, PASSWD, DATABASE_NAME


def get_conn():
    conn = pymysql.connect(host=HOST, port=PORT, user=USER_NAME, passwd=PASSWD, db=DATABASE_NAME, charset='utf8')
    return conn


def query_all(cur, sql, args):
    cur.execute(sql, args)
    return cur.fetchall()


def read_mysql_to_csv(filename, user):
    with codecs.open(filename=filename, mode='w', encoding='utf-8') as f:
        write = csv.writer(f, dialect='excel')
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('select * from users_resulttable')
        rr = cur.fetchall()
        for result in rr:
            write.writerow(result[:-1])


def read_mysql_to_csv2(filename, user):
    with codecs.open(filename=filename, mode='w', encoding='utf-8') as f:
        write = csv.writer(f, dialect='excel')
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('select * from users_resulttable')
        rr = cur.fetchall()
        for result in rr:
            write.writerow(result[:-1])


import sys
import random
import math
import os
from operator import itemgetter

random.seed(0)
user_sim_mat = {}
matrix = []  #全局变量
matrix2 = []
updated = defaultdict(lambda: True)  # 用户是否更新数据


class ItemBasedCF(object):
    ''' TopN recommendation - Item Based Collaborative Filtering '''

    def __init__(self):
        self.trainset = {}
        self.testset = {}

        self.n_sim_movie = 20
        self.n_rec_movie = 10

        self.movie_sim_mat = {}
        self.movie_popular = {}
        self.movie_count = 0

    @staticmethod
    def loadfile(filename):
        ''' load a file, return a generator. '''
        fp = open(filename, 'r', encoding='UTF-8')
        for i, line in enumerate(fp):
            yield line.strip('\r\n')
        fp.close()
        print('load %s succ' % filename, file=sys.stderr)

    def generate_dataset(self, filename, pivot=1.0):
        ''' load rating data and split it to training set and test set '''
        trainset_len = 0
        testset_len = 0

        for line in self.loadfile(filename):
            user, movie, rating = line.split(',')
            rating = float(rating)
            # split the data by pivot
            if random.random() < pivot:
                self.trainset.setdefault(user, {})

                self.trainset[user][movie] = float(rating)
                trainset_len += 1
            else:
                self.testset.setdefault(user, {})

                self.testset[user][movie] = float(rating)
                testset_len += 1

        print('train set = %s' % trainset_len, file=sys.stderr)
        print('test set = %s' % testset_len, file=sys.stderr)

    def calc_movie_sim(self):
        ''' calculate movie similarity matrix '''
        print('counting movies number and popularity...', file=sys.stderr)

        for user, movies in self.trainset.items():
            for movie in movies:
                # count item popularity
                if movie not in self.movie_popular:
                    self.movie_popular[movie] = 0
                self.movie_popular[movie] += 1

        # print('count movies number and popularity succ', file=sys.stderr)

        # save the total number of movies
        self.movie_count = len(self.movie_popular)
        print('total movie number = %d' % self.movie_count, file=sys.stderr)

        # count co-rated users between items
        itemsim_mat = self.movie_sim_mat
        # print('building co-rated users matrix...', file=sys.stderr)

        for user, movies in self.trainset.items():
            for m1 in movies:
                for m2 in movies:
                    if m1 == m2:
                        continue
                    itemsim_mat.setdefault(m1, {})
                    itemsim_mat[m1].setdefault(m2, 0)
                    itemsim_mat[m1][m2] += 1 / math.log(1 + len(movies) * 1.0)

        simfactor_count = 0
        PRINT_STEP = 2000000

        for m1, related_movies in itemsim_mat.items():
            for m2, count in related_movies.items():
                itemsim_mat[m1][m2] = count / math.sqrt(
                    self.movie_popular[m1] * self.movie_popular[m2])
                simfactor_count += 1
                if simfactor_count % PRINT_STEP == 0:
                    print('calculating movie similarity factor(%d)' %
                          simfactor_count, file=sys.stderr)


    def recommend(self, user):
        ''' Find K similar movies and recommend N movies. '''
        K = self.n_sim_movie
        N = self.n_rec_movie
        matrix2.clear()
        rank = {}
        watched_movies = self.trainset[user]

        data = pd.read_csv("users/static/users_resulttable.csv",header=None)
        movie_score_incount={}
        movie_score_recount={}

        for movie, rating in watched_movies.items():
            for related_movie, similarity_factor in sorted(self.movie_sim_mat[movie].items(),
                                                           key=itemgetter(1), reverse=True)[:K]:
                x = data[data[1] == int(related_movie)]
                score = np.mean(x[2].values)
                if related_movie in watched_movies :
                    continue
                rank.setdefault(related_movie, 0)
                movie_score_incount.setdefault(related_movie, 0)
                movie_score_recount.setdefault(related_movie, 0)

                if score >= 3:movie_score_incount[related_movie] += 1
                else: movie_score_recount[related_movie] += 1
                rank[related_movie] += similarity_factor * rating
        for movie, count in movie_score_incount.items():
            rank[movie]+=np.log(max(1,count))
            rank[movie]-=np.log(max(1,movie_score_recount[movie]))
        # return the N best movies
        rank_ = sorted(rank.items(), key=itemgetter(1), reverse=True)[:N]
        rank_plot = []
        for key,value in rank_:
            matrix2.append(key)    #matrix为存储推荐的imdbId号的数组
            #print(key)     #得到了推荐的电影的imdbid号
            rank_plot.append(value)
        # print(rank_plot[0:10])
        # plt.figure(2)
        # plt.hist(rank_plot, bins = 20)
        # #plt.show()
        # plt.savefig('./2.png')
        print(matrix2)
        return matrix2

if __name__ == '__main__':
    ratingfile2 = os.path.join('static', 'users_resulttable.csv')  # 一共671个用户

    usercf = UserBasedCF()
    userId = '1'
    # usercf.initial_dataset(ratingfile1)
    usercf.generate_dataset(ratingfile2)
    usercf.calc_user_sim()
    # usercf.evaluate()
    usercf.recommend(userId)
    # 给用户推荐10部电影  输出的是‘movieId’,兴趣度





