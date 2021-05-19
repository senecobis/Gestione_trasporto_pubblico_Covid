import pandas as pd
import numpy as np
import mip

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

Tratte = pd.read_excel("file_di_dati.xlsx", sheet_name="porzioni di viaggio")
tempi_vuoto = pd.read_excel("file_di_dati.xlsx", sheet_name="tempi di percorrenza a vuoto")

# i tempi a vuoto sono una matrice triangolare inferiore in cui gli elementi [0][j] sono i nomi delle partenze e
# gli elementi [i][0] le destinazioni. Quindi gli elementi [i][j] rappresentano il tempo per andare a vuoto dalla origine
# j alla destinazione i

# conversione files

Tratte = Tratte.to_numpy()
tempi_vuoto = tempi_vuoto.to_numpy()

# testings

timedelay = Tratte[1][5] - Tratte[1][4]

n_di_tratte = Tratte.shape

print(Tratte[1][4])
print(timedelay)
print(n_di_tratte[0])
print(f"Da {tempi_vuoto[2][0]} a {tempi_vuoto[0][4]} il tempo di percorrenza è {tempi_vuoto[4][2]} minuti ")

# <<<<<<<<<<<<< Modello mip >>>>>>>>>>>>>

modello = mip.Model()

xij = modello.add_var(var_type=mip.BINARY)
zj = modello.add_var(var_type=mip.INTEGER)

for j in range(0,K_AUTOBUS)
for i in range(1,n_di_tratte[0]):
    modello.add_constr(xij*(Tratte[i][INITIAL_STOP]))


#m.objective = mip.maximize(110*x1 + 130*x2)

#m.add_constr(  x1 + 2*x2 <= 10)
#m.add_constr(2*x1 + 2*x2 <= 18)
#m.add_constr(  x1 + 3*x2 <= 12)
#m.add_constr(2*x1 + 3*x2 <= 21)
#m.add_constr(  x1        <=  9)
#m.add_constr(  x1        <= 10)





