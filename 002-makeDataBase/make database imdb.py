import mysql.connector
import pandas as pd
import numpy as np

db = mysql.connector.connect(
    host = '127.0.0.1',
    user = 'root',
    password = '',
)
cursor = db.cursor()

# create imdb_250 database
cursor.execute("create database if not exists imdb_250")

# connect to imdb_250 database
db = mysql.connector.connect(
    host = '127.0.0.1',
    user = 'root',
    password = 'VW1eQF7LR5#',
    database = 'imdb_250'
)
cursor = db.cursor()

# create movie table
cursor.execute(
    '''create table movie (
            id varchar(8) primary key not null,
            Title varchar(128) not null,
            Year int not null,
            Runtime int not null,
            Parental_Guide varchar(8) not null,
            Gross_US_Canada int
        );'''
)

# create genre_movie table
cursor.execute(
    '''create table genre_movie (
            id int primary key not null auto_increment,
            Movie_id varchar(8) not null,
            Genre varchar(16) not null,
            foreign key (Movie_id) references movie(id)
        );'''
)
cursor.execute('alter table genre_movie auto_increment=1;')

# create person table
cursor.execute(
    '''create table person (
            id varchar(8) primary key not null ,
            Name varchar(32) not null
        );'''
)

# create cast table
cursor.execute(
    '''create table cast (
            id int primary key not null auto_increment,
            Movie_id varchar(8) not null,
            Person_id varchar(8) not null,
            foreign key (Movie_id) references movie(id),
            foreign key (Person_id) references person(id)
        );'''
)
cursor.execute('alter table cast auto_increment=1;')

# create crew table
cursor.execute(
    '''create table crew (
            id int primary key not null auto_increment,
            Movie_id varchar(8) not null,
            Person_id varchar(8) not null,
            Role varchar(8) not null,
            foreign key (Movie_id) references movie(id),
            foreign key (Person_id) references person(id)
        );'''
)
cursor.execute('alter table crew auto_increment=1;')

# load data
data = pd.read_csv('../001-webScraping/imdb-250.csv')

# fil na
data.loc[(data['parental_guide'].isna()) | (data['parental_guide'] == 'Not Rated'), 'parental_guide'] = 'Unrated'
data = data.replace({np.nan:None})

# concat movei_id witth user and genre
id = data['id'].values
directore_primary = data[['directore']].values
directore_primary = directore_primary.reshape(250)
directore_secondary = list()
for row in directore_primary:
    directore_secondary.append(eval(row))
directore_finaly = list()
for i, _ in enumerate(id):
    directore_finaly.append([id[i], directore_secondary[i]])
directore_with_id = list()
for id, directores in directore_finaly:
    for directore in directores:
        directore_with_id.append((id,) + directore + ('Director',))

id = data['id'].values 
writer_primary = data[['writer']].values
writer_primary = writer_primary.reshape(250)
writer_secondary = list()
for row in writer_primary:
    writer_secondary.append(eval(row))
writer_finaly = list()
for i, _ in enumerate(id):
    writer_finaly.append([id[i], writer_secondary[i]])
writer_with_id = list()
for id, writers in writer_finaly:
    for writer in writers:
        writer_with_id.append((id,) + writer + ('Writer',))

id = data['id'].values
star_primary = data[['star']].values
star_primary = star_primary.reshape(250)
star_secondary = list()
for row in star_primary:
    star_secondary.append(eval(row))
star_finaly = list()
for i, _ in enumerate(id):
    star_finaly.append([id[i], star_secondary[i]])
star_with_id = list()
for id, stars in star_finaly:
    for star in stars:
        star_with_id.append((id,) + star + ('Star',))

id = data['id'].values
genre_primary = data[['genre']].values
genre_primary = genre_primary.reshape(250)
genre_secondary = list()
for row in genre_primary:
    genre_secondary.append(eval(row))
genre_finaly = list()
for i, _ in enumerate(id):
    genre_finaly.append([id[i], genre_secondary[i]])
genre_with_id = list()
for id, genres in genre_finaly:
    for genre in genres:
        genre_with_id.append((id,) + (genre,))

# insert movie details
sql_insert_movei_data = 'insert into movie (id, Title, Year, Runtime, Parental_Guide, Gross_US_Canada) values (%s, %s, %s, %s, %s, %s)'
val_insert_movei_data = [tuple(row) for row in data[['id', 'title', 'year', 'runtime', 'parental_guide', 'gross_us_canada']].values]
cursor.executemany(sql_insert_movei_data, val_insert_movei_data)
db.commit()

# insert genre details
sql_insert_genre_movie_data = 'insert into genre_movie (Movie_id, Genre) values (%s, %s)'
val_insert_genre_movie_data = [(int(row[0]), row[1])for row in genre_with_id]
cursor.executemany(sql_insert_genre_movie_data, val_insert_genre_movie_data)
db.commit()

# insert person details
sql_insert_person_data = 'insert into person (id, Name) values (%s, %s)'
val_insert_person_data = list(set([(int(row[1]), row[2]) for row in directore_with_id] + [(int(row[1]), row[2]) for row in writer_with_id] + [(int(row[1]), row[2]) for row in writer_with_id]))
cursor.executemany(sql_insert_person_data, val_insert_person_data)
db.commit()

# insert cast details
sql_insert_cast_data = 'insert into cast (Movie_id, Person_id) values (%s, %s)'
val_insert_cast_data = list(set([(int(row[0]), int(row[1])) for row in directore_with_id] + [(int(row[0]), int(row[1])) for row in writer_with_id] + [(int(row[0]), int(row[1])) for row in writer_with_id]))
cursor.executemany(sql_insert_cast_data, val_insert_cast_data)
db.commit()

# insert crew details
sql_insert_crew_data = 'insert into crew (Movie_id, Person_id, Role) values (%s, %s, %s)'
val_insert_crew_data = [(int(row[0]), int(row[1]), row[3])for row in directore_with_id] + [(int(row[0]), int(row[1]), row[3])for row in writer_with_id]
cursor.executemany(sql_insert_crew_data, val_insert_crew_data)
db.commit()

db.close()