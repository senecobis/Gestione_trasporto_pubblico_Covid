
import pandas as pd
import numpy as np
import mip
import xlrd
import datetime
from string import*

# <<<<<<<<<<<<<  header  >>>>>>>>>>>>>>>

# definizioni costanti fittizzie

COUNTED_PASSENGERS = 0
EXTRA_PASSENGERS = 1
INITIAL_STOP = 2
FINAL_STOP = 3
INITIAL_TIME = 4
FINAL_TIME = 5
K_AUTOBUS = 10

# lettura files

Tratte = pd.read_excel('file_di_dati.xlsx', sheet_name="porzioni di viaggio")
tempi_vuoto = pd.read_excel('file_di_dati.xlsx', sheet_name="tempi di percorrenza a vuoto")

# i tempi a vuoto sono una matrice triangolare inferiore in cui gli elementi [0][j] sono i nomi delle partenze e
# gli elementi [i][0] le destinazioni. Quindi gli elementi [i][j] rappresentano il tempo per andare a vuoto dalla origine
# j alla destinazione i

# conversione files

Tratte = Tratte.to_numpy()
tempi_vuoto = tempi_vuoto.to_numpy()

# ulteriori "costanti"

n_di_tratte = Tratte.shape[0]
n_di_luoghi = tempi_vuoto.shape[0]

# uniformo i nomi tra tempi di percorrenza e tempi a vuoto

for i in range(1, tempi_vuoto.shape[0]):
    tempi_vuoto[0][i].strip()
    tempi_vuoto[i][0].strip()


    if tempi_vuoto[0][i] == 'stazione fs':
        tempi_vuoto[0][i] = 'stazione'

    if tempi_vuoto[0][i] == 'p. medaglie d’oro':
        tempi_vuoto[0][i] = 'medaglie d’oro'

    if tempi_vuoto[0][i] == 'piazzale medaglie d’oro':
        tempi_vuoto[0][i] = 'medaglie d’oro'

    if tempi_vuoto[0][i] == 'piazzale dante':
        tempi_vuoto[0][i] = 'p. dante'

    if tempi_vuoto[i][0] == 'stazione fs':
        tempi_vuoto[i][0] = 'stazione'

    if tempi_vuoto[i][0] == 'p. medaglie d’oro':
        tempi_vuoto[i][0] = 'medaglie d’oro'

    if tempi_vuoto[i][0] == 'piazzale medaglie d’oro':
        tempi_vuoto[i][0] = 'medaglie d’oro'

    if tempi_vuoto[i][0] == 'piazzale dante':
        tempi_vuoto[i][0] = 'p. dante'

for i in range(1,n_di_tratte):
    Tratte[i][INITIAL_STOP] = Tratte[i][INITIAL_STOP].strip()
    Tratte[i][FINAL_STOP] = Tratte[i][FINAL_STOP].strip()

# funzione per convertie i tempi

epoch = datetime.datetime.utcfromtimestamp(0)


def unix_time_sec(dt):
    return (dt - epoch).total_seconds()


tempo_diff = -unix_time_sec(Tratte[1][INITIAL_TIME]) + unix_time_sec(Tratte[1][FINAL_TIME])
print(tempo_diff)

#converto i tempi in tabella rispetto al tempo assoluto
#converto i tempi a vuoto in secondi

for i in range(1,n_di_tratte):
    Tratte[i][INITIAL_TIME] = unix_time_sec(Tratte[i][INITIAL_TIME])
    Tratte[i][FINAL_TIME] = unix_time_sec(Tratte[i][FINAL_TIME])

for i in range(1,n_di_luoghi):
    for j in range(1,n_di_luoghi):
        if tempi_vuoto[i][j]!= 'NaN':
            tempi_vuoto[i][j] = tempi_vuoto[i][j]*60




# creazione indice dei luoghi visitabili

# luoghi = [dict() for k in range(0,n_di_luoghi)]
luoghi = dict()
for k in range(0, n_di_luoghi):
    luoghi[tempi_vuoto[0][k]] = k

# <<<<<<<<<<<<< Modello mip >>>>>>>>>>>>>

modello = mip.Model()

# per ogni autobus abbiamo 157 variabili che rappresentano le tratte a cui possono sono assegnati

#x = np.array([modello.add_var(var_type=mip.BINARY) for i in range(0, n_di_tratte * K_AUTOBUS)])

x = []
for k in range(n_di_tratte):
    x.append([modello.add_var(var_type=mip.BINARY) for i in range(K_AUTOBUS)])

# x è un array di array python che ha come primo campo le tratte e come secondo gli autobus

#dimensionex = x
#print(f"la dimensione della x è {dimensionex}")

# vincoli
# k è un indice che va da 0 a K_AUTOBUS*157 per assecondare come sono definite le varibili

k = 0
indice_luogo_stop = 1
indice_luogo_desiderato = 2
t_di_stop = Tratte[1][FINAL_TIME]

for j in range(0, K_AUTOBUS):
    t_di_stop = 0
    for i in range(1, 157):
        #print(f"numero {i} iterazione")

        luogo_desiderato = Tratte[i][INITIAL_STOP]
        indice_luogo_desiderato = luoghi[luogo_desiderato]
        t_di_start = Tratte[i][INITIAL_TIME]

        # da file excel deve essere più grande il primo indice che il secondo per i tempi a vuoto

        if indice_luogo_desiderato > indice_luogo_stop:
            tempo_per_arrivarci = tempi_vuoto[indice_luogo_desiderato][indice_luogo_stop]
        if indice_luogo_desiderato < indice_luogo_stop:
            tempo_per_arrivarci = tempi_vuoto[indice_luogo_stop][indice_luogo_desiderato]
        if indice_luogo_desiderato == indice_luogo_stop:
            tempo_per_arrivarci = 0

        #print(f"la key è {luogo_desiderato}")

        modello.add_constr(x[i][j] * t_di_start >= x[i][j] * (t_di_stop + tempo_per_arrivarci))

        if x[i][j] == 1:
            # tempi e luoghi di stop relativi all'ultima iterazione in cui la variabile era 1
            luogo_di_stop = Tratte[i][FINAL_STOP]
            indice_luogo_stop = luoghi[luogo_di_stop]
            t_di_stop = Tratte[i][FINAL_TIME]

        k += 1

# vincolo 2
for i in range(n_di_tratte):
    modello.add_constr( mip.xsum(x[i][j] for j in range(K_AUTOBUS)) == 1 )



# funzione obiettivo
for i in range(1,n_di_tratte):
    modello.objective = mip.maximize(mip.xsum(x[i][j]*Tratte[i][EXTRA_PASSENGERS] for j in range(0,K_AUTOBUS) ))

