# 1 Environment Set Up
## 1.1 Conda Invironment
```bash
conda create --name proj python=3.6
conda install django=1.11
conda install numpy=1.19.5
conda install pandas=1.1.5
pip install uwsgi
pip install beautifulsoup4
```

## 1.2 MySQL
```bash
wget http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
rpm -ivh mysql-community-release-el7-5.noarch.rpm
yum update
yum install mysql-server
chown -R mysql:mysql /var/lib/mysql/
mysqld --initialize
systemctl start mysqld
systemctl status mysqld # Check the MySQL running status
```

## 1.3 nginx
```bash
cd ~
wget http://nginx.org/download/nginx-1.5.6.tar.gz
tar xf nginx-1.5.6.tar.gz
cd nginx-1.5.6
./configure --prefix=/usr/local/nginx-1.5.6 --with-http_stub_status_module --with-http_gzip_static_module
make && make install
```

# 2 Web Crawler

python crawler.py

Download the poster data: https://connecthkuhk-my.sharepoint.com/:f:/g/personal/u3590624_connect_hku_hk/EkvMRqnQ9XdEsgVW4ovNHzYBlteqR5jOkrZ5vZ6ii-HJNA?e=E7JeCP

Put the poster dir into movierecommend/users/static/img

# 3 Database Set Up

```sql
create table MovieData;
CREATE TABLE moviegenre3(imdbId INT NOT NULL PRIMARY KEY,title varchar(300),poster varchar(600)); 
CREATE TABLE users_resulttable(userId INT NOT NULL,imdbId INT,rating DECIMAL(3,1)); 
alter table users_resulttable add column id int auto_increment PRIMARY KEY; 
```

```bash
load data infile "E:/MovieRecommend/data/users_resulttable.csv" into table users_resulttable fields terminated by ',' lines terminated by '\n' (userId,imdbId,rating);
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

# 4 Run the Service
## 4.1 Run Easily
Start the project by running the manage.py file:

`nohup python manage.py runserver 0.0.0.0:8000 > users/static/log  2>&1 &`

## 4.2 Deploy in an Optimized Way
To Run the Project using uWSGI:

`uwsgi --chdir=/tmp/proj/movie_recommender_proj_hku/movierecommend  --module=django_auth_example.wsgi:application --env DJANGO_SETTINGS_MODULE=django_auth_example.settings --master --pidfile=uwsgi.pid --http=127.0.0.1:8000 --processes=2 --uid=1000 --gid=2000 --harakiri=20 --max-requests=5000 --vacuum --home=/root/anaconda3/envs/proj --daemonize=log --pythonpath=/root/anaconda3/envs/proj/lib/python3.6/site-packages`

## 4.3 Deploy in the Cloud Server
You could visit our website on the cloud server with url: https://hz-t3.matpool.com:26853/

# 5 Introduction to Project Structure

- [**django_auth_example**](django_auth_example)
    - [**settings.py**](settings.py): Setup/configuration for this Django project.
    - [**urls.py**](urls.py): The Django project's URL declaration; A Django-powered "directory" of Web sites.
    - [**wsgi.py**](wsgi.py): Entry to a WSGI-compatible Web server to run our project.
- [**templates**](templates) Template Files.
    - [**registration**](templates/registration): Login Page.
    - [**users**](templates/users): Most pages, including fuzzy search page, movie recommendation page, etc.
- [**users**](users)
    - [**migrations**](users/migrations)
    - [**static**](users/static): Static files, including pictures, css files, js files, etc.
        - [**css**](users/static/css)
        - [**img**](users/static/img)
        - [**js**](users/static/js)
    - [**templatetags**](users/templatetags)
    - [**view.py**](view.py): Template files.
- [**manage.py**](manage.py): A useful command-line tool that lets us interact with this Django project in a variety of ways.

# reference
- https://github.com/liangliangyy/DjangoBlog
- https://github.com/hwwang55/RippleNet
- https://github.com/JaniceWuo/MovieRecommend
- https://github.com/XuefengHuang/RecommendationSystem