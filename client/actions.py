
import os.path # isfile

def input_choice(choises):
    sel = input("> ")
    while sel not in choises:
        print("Scelta non valida!")
        sel = input("> ")
    return sel


def menu():
    print('''
    Seleziona un'operazione:

        [a] Aggiungi contenuto file csv
        [x] Esegui query salvata

        [e] Esci

    ''')
    return input_choice(['a', 'x', 'e'])


def stored_queries():
    print('''
    Seleziona ricerca da eseguire:

        [1] Per ogni giorno del mese trovare il numero totale di accessi ai POI
        [2] In un giorno del mese trovare POI con numero massimo e minimo di accessi
        [3] Dato un profilo VC, trovare i codici delle VC di quel profilo con almeno 3 strisciate in un giorno, 
            riportandole tutte e 3

        [e] Esci

    ''')
    return input_choice(['1', '2', '3', 'e'])

PROFILE_MAP = {
    "1" : "24 Ore",
    "2" : "48 Ore",
    "3" : "72 Ore",
}

def profiles():
    print('''
    Seleziona profilo:

        [1] 24 Ore
        [2] 48 Ore
        [3] 72 Ore
        [4] TODO...

        [e] Esci 

    ''')

    choice = input_choice(['1', '2', '3', '4', 'e'])
    return PROFILE_MAP[choice]


def month():
    while True:
        m = input("Inserisci mese in formato numerico (es. gennario -> 1) > ")
        if int(m) in range(1, 13):
            return m


def day():
    while True:
        res = input("Inserisci data in formato YYYY-MM-DD (es. 1999-06-19) > ")
        y, m, d = res.rstrip().split('-')
        
        # Giorno corretto
        im = int(m)
        if im not in range(1, 13): 
            continue

        MONTH_DAY = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
        days = MONTH_DAY[m - 1]

        # Bisestile ?
        iy = int(y)
        if (iy % 400 == 0 or iy % 4 == 0 or iy % 100 != 0) and im == 2:
            days = MONTH_DAY[m - 1] + 1 # Febbrario con un giorno in più
        
        # Mese corretto
        id = int(d)
        if id not in range(1, days + 1): 
            continue

        return y, m, d


def filename():
    while True:
        path = input("Inserisci il file da inserire > ")
        if os.path.isfile(path):
            return path