## Modules

import lyricsgenius
import os
import eyed3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from io import StringIO
import sys
import zipfile

## Fonctions


chrome_options = Options()

chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)


def string(lst): # convertir une liste en chaine
    str = ''
    for n in range(len(lst)):
        str += lst[n]
    return str

def accents(str): # retirer des accents d'une chaine
    texte = list(str.upper()+'  ')

    for n in range(len(texte)-2):
        k = ord(texte[n])
        if k in [200,201,202,203]:
            texte[n] = 'E'
        elif k in [192,193,194,195,196,197]:
            texte[n] = 'A'
        elif k in [204,205,206,207]:
            texte[n] = 'I'
        elif k == 199:
            texte[n] = 'C'
        elif k in [210,211,212,213,214]:
            texte[n] = 'O'
        elif k == 338:
            texte[n] = 'O'
            texte.insert(n+1,'E')
        k = ord(texte[n])
    return string(texte)

def miseenforme(str): # enlever les majuscules, accents, caractères spéciaux...
    str = str.replace('\n', ' ').replace('\r', '')
    texte = list(accents(str))
    n,i=0,0
    while n < len(texte)-2:
        k = ord(texte[n]) - 64
        k1 = ord(texte[n+1]) -64

        if (k<1 or k>26) and k != -32 and (not (k>-16 and k<-7)):
            texte[n] = ' '
            n-=1

        if k==-32 and (k1<1 or k1>26) and (not (k>-16 and k<-7)):
            del texte[n]
            n-=1

        if n-i >= 10000:
            print(i)
            i=n

        n += 1

    return string(texte[:-2]).lower()


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout



## Programme

def paroliser(tmpDir, folderName):


    # Emplacement des fichiers
    prevDir = os.getcwd()
    os.chdir(tmpDir)

    listefichiers = os.listdir()
    lst = []

    for n in listefichiers:
        if '.mp3' in n:
            lst.append(n)

    lst2 = []
    lst3 = []
    lst4 = []
    lst5 = []
    lst6 = []



    token = 'uMWtxOGdLmCY94uXn82yRvdbA7HFzTj2cR-v3A0byNZKPwZdcmJmQ-zB1-SPfr1J'
    LG = lyricsgenius.Genius(token)


    for k in lst:
        audio = eyed3.load(k)

        if audio.tag.title != '' and audio.tag.artist != '' and audio.tag.artist != None and audio.tag.title != None:

            titre = miseenforme(audio.tag.title)
            auteur = miseenforme(audio.tag.artist)

            with Capturing() as output:
                song = LG.search_song(title = titre, artist = auteur)

            for n in output:
                print(n)


            if 'No results found' in output[1]:
                print('Non trouvée')
                lst2.append(k)
            elif 'does not contain lyrics' in output[1]:
                print('Instrumental')
                lst4.append(k)
                audio.tag.lyrics.set('Instrumental')
                audio.tag.save()

            elif song != None:

                if miseenforme(song.artist) == miseenforme(auteur):

                    paroles = song.lyrics

                    a = paroles.find('Lyrics')
                    paroles = paroles[a+6:].replace('Embed','')

                    while ord(paroles[-1]) in range(48,58):
                        paroles = paroles[:len(paroles)-1]

                    while '[' in paroles:
                        a = paroles.find('[')
                        if ']' in paroles:
                            b = paroles.find(']')
                            if a == 0:
                                paroles=paroles[b+1:]
                            else:
                                paroles1 = paroles[:a]
                                paroles2 = paroles[b+1:]
                                paroles = paroles1+paroles2
                        else:
                            paroles = paroles[:a]

                    if paroles != '':

                        while paroles[0]=='\n':
                            paroles = paroles[1:]

                        while '\n\n\n' in paroles:
                            paroles = paroles.replace('\n\n\n','\n\n')


                        paroles = paroles.replace('œ', 'oe').replace('\u2005',' ').encode('latin-1','ignore').decode('latin-1').replace('\n ','\n')

                        #print(paroles)
                        lst3.append(k)
                        audio.tag.lyrics.set(paroles)
                        audio.tag.save()
                    else:
                        print('Instrumental')
                        audio.tag.lyrics.set('Intrumental')
                        audio.tag.save()
                        lst4.append(k)
                else:
                    print('Non trouvée')
                    lst2.append(k)
            else:
                print('Non trouvée')
                lst2.append(k)

        else:
            print('Pas de données pour trouver le morceau')
            lst6.append(k)


    for k in lst2:
        audio = eyed3.load(k)

        if audio.tag.title != '' and audio.tag.artist != '' and audio.tag.artist != None and audio.tag.title != None:

            titre = miseenforme(audio.tag.title)
            auteur = miseenforme(audio.tag.artist)

            print(titre)

            # Récupération des paroles
            driver = webdriver.Chrome(options=chrome_options)

            url = 'https://www.google.com/search?q=' + titre.replace(' ', '+') + '+' + auteur.replace(' ','+') + '+lyrics'

            driver.get(url)

            # Bouton accepter les cookies de leurs morts
            try:
                button = driver.find_element(by=By.XPATH, value='''//*[@id="L2AGLb"]/div''')
                button.click()
            except:
                l=1

            data = driver.find_elements(by=By.XPATH, value='''//div[@jsname='U8S5sf']''')


            paroles = ''

            for i in range(len(data)):
                paroles += data[i].text + '\n\n'*(i!=len(data)-1)


            paroles = paroles.replace('œ', 'oe').replace('\u2005',' ').encode('latin-1','ignore').decode('latin-1').replace('\n ','\n')



            if '' != paroles:
                while paroles[0]==' ':
                    paroles = paroles[1:]
                #print(paroles)
                lst3.append(k)
                audio.tag.lyrics.set(paroles)
                audio.tag.save()
            else:
                lst5.append(k)

            driver.close()


    print(' ')
    print(' ')

    print('Total: ', len(lst), ' chansons.')

    print(' ')

    print('Réussies: ', len(lst3))
    for k in lst3:
        print(k)

    print(' ')
    print('Ratées: ', len(lst5)+len(lst6))
    for k in lst5+lst6:
        print(k)

    print(' ')
    print('Instrumental: ', len(lst4))
    for k in lst4:
        print(k)



    with zipfile.ZipFile('../results/' + folderName + '.zip', mode="w") as archive:
        for k in lst:
            archive.write(k)
    
    os.chdir(prevDir)

    return folderName + '.zip'