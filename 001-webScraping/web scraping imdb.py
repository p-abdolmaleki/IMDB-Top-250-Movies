import requests
from bs4 import BeautifulSoup
import pandas as pd



# extrct the movies url
url = 'https://www.imdb.com/chart/top/?ref_=nv_mv_250'
r = requests.get(url, headers = {'user-agent': 'Chrome/58.0.3029.110 accept-language'})
soup = BeautifulSoup(r.content, 'html.parser')
movies_card = soup.select('.sc-1e00898e-0')
movies_link = list()
for movie in movies_card:
    movies_link.append('https://www.imdb.com/' + movie.find('a')['href'])


# extract the movies detail
movies_list = list()
for url in movies_link:
    r = requests.get(url, headers = {'user-agent': 'Chrome/58.0.3029.110 accept-language'})
    soup = BeautifulSoup(r.content, 'html.parser')
    movies_dict = dict()
    movies_dict['id'] = url.split('/')[5].replace('tt','')
    movies_dict['title'] = soup.select('.sc-69e49b85-0')[0].find(class_='hero__primary-text').text
    if len(soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')) == 3:
        movies_dict['year'] = soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[0].text
        movies_dict['parental_guide'] = soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[1].text
        if(len(soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[2].text.split()) == 2):
            movies_dict['runtime'] = int(soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[2].text.replace('h', '').replace('m', '').split()[0]) * 60 + int(soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[2].text.replace('h', '').replace('m', '').split()[1])
        elif 'h' in soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[2].text.split()[0]:
             movies_dict['runtime'] = int(soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[2].text.replace('h', '').replace('m', '').split()[0]) * 60
        else:
            movies_dict['runtime'] = int(soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[2].text.replace('h', '').replace('m', '').split()[0])
    elif len(soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')) == 2:
        movies_dict['year'] = soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[0].text
        movies_dict['parental_guide'] = ''
        if(len(soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[1].text.split()) == 2):
            movies_dict['runtime'] = int(soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[1].text.replace('h', '').replace('m', '').split()[0]) * 60 + int(soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[1].text.replace('h', '').replace('m', '').split()[1])
        elif 'h' in soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[1].text.split()[0]:
             movies_dict['runtime'] = int(soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[1].text.replace('h', '').replace('m', '').split()[0]) * 60
        else:
            movies_dict['runtime'] = int(soup.select('.sc-69e49b85-0')[0].find_all(class_='ipc-inline-list__item')[1].text.replace('h', '').replace('m', '').split()[0])
    genre_list = list()
    genres = soup.select('.sc-69e49b85-4')[0].find_all(class_='ipc-chip')
    for genre in genres:
        genre_list.append(genre.text)
    movies_dict['genre'] = genre_list
    directore = list()
    writer = list()
    star = list()
    for i, person in enumerate(soup.select('.sc-69e49b85-4')[0].find_all(class_='ipc-metadata-list__item')):
        for j, role in enumerate(person.find_all('a')):
            if i == 0:
                if role.text != 'Directores' and role.text != '':
                    directore.append((role['href'].split('/')[2].replace('nm', ''), role.text))
            elif i == 1:
                if role.text != 'Writers' and role.text != 'Writer' and role.text != '':
                    writer.append((role['href'].split('/')[2].replace('nm', ''), role.text))
            elif i == 2:
                if role.text != 'Stars' and role.text != '':
                    star.append((role['href'].split('/')[2].replace('nm', ''), role.text))
    movies_dict['directore'] = directore
    movies_dict['writer'] = writer
    movies_dict['star'] = star
    gross_us_canada_check = True
    for i, l in enumerate(list(soup.select('span'))):
        if 'Gross US &amp; Canada' in str(l):
            index = i +1
            movies_dict['gross_us_canada'] = soup.select('span')[index].text.replace('$','').replace(',','')
            gross_us_canada_check = False
            break
    if gross_us_canada_check:
        movies_dict['gross_us_canada'] = ''
    movies_list.append(movies_dict)
    print('movie with ', url, 'finished')

# store data in csv file
data = pd.DataFrame(movies_list)
data.to_csv(
    'imdb-250.csv',
    index=False
)