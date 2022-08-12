#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :code.py
# @Time      :2022/6/17 23:07
# @Author    :xxx
from fake_useragent import UserAgent
from urllib.parse import quote
import pandas as pd
import requests

from bs4 import BeautifulSoup

from multiprocessing import Pool

with open('c.txt',encoding='utf8') as f:
    c=f.read().strip()
    
def get_img(f_name):
    #url='https://search.douban.com/movie/subject_search?search_text={}'.format(quote(f_name))
    url='https://www.imdb.com/find?q={}&ref_=nv_sr_sm'.format(quote(f_name))
    print(url)
    #driver.get(url)
    res=requests.get(url)
    soup=BeautifulSoup(res.text,'lxml')
    try:
        d_url='https://www.imdb.com'+soup.find('td',class_='primary_photo').find('a')['href']
        r=requests.get(d_url)
        s=BeautifulSoup(r.text,'lxml')
        img_url=s.find('img',class_='ipc-image')['src']
        #img_url = soup.find('div', class_='item-root').find('img')['src']
    except:
        img_url =''


    return img_url

def is_url(url):
    #url='https://images-na.ssl-images-amazon.com/images/M/MV5BMTkxMTA5OTAzMl5BMl5BanBnXkFtZTgwNjA5MDc3NjE@._V1_UX182_CR0,0,182,268_AL_.jpg'
    res=requests.get(url)
    if res.text=='Not Found':
        return True
    else:
        return False

def main(i):
    #print('\t\t索引：',i)
    #for i in range(len(df['imdbId'].tolist())):
    if str(df['imdbId'].tolist()[i]) not in recode:
        if is_url(df['poster'].tolist()[i]):
            img_url=get_img(df['title'].tolist()[i])
            print('\timg:',img_url)
            ret=[str(df['imdbId'].tolist()[i]), df['title'].tolist()[i], img_url]
        else:
            ret=[str(df['imdbId'].tolist()[i]),df['title'].tolist()[i],df['poster'].tolist()[i]]
        with open('6.txt','a',encoding='utf8') as f:
            f.write('\t'.join(ret)+'\n')
    else:
        print(str(df['imdbId'].tolist()[i]))

if __name__ == '__main__':
    alldata = []
    recode = []
    with open('6.txt', 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip().split('\t')
            if line[0] not in recode:
                recode.append(line[0])
    df = pd.read_csv('MovieGenre5.csv', encoding='gb18030')
    i_l=[i for i in range(len(df['imdbId'].tolist()))]
    #pool = Pool(processes=8)
    #pool.map(main, i_l)
    for i in i_l:
        main(i)

    with open('6.txt', 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip().split('\t')
            if len(line)==3:
                alldata.append(line)

    pd.DataFrame(alldata,columns=['imdbId','title','poster']).to_csv('MovieGenre6.csv',encoding='gb18030',index=None)
