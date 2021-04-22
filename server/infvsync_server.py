##############################################################################################
# INFV STREAM SYNC - SERVER
#Autor: Manuel Bazarra Lorenzo -  Alias: Estrallator
#
#Sincroniza diversas fuentes de stream, leyendo timestamp, previamente enviado por
#infvSync_client.
#
#Comparamos el timestamp del cliente con el del servidor, de esta manera sabemos el lag
#de la transmision y aplicamos un delay a cada uno de los streams, para que coincida con el de
#mayor latencia
###############################################################################################
 
import socket
import time
import struct
import select
from os import system,name

COMPENSATION_INTERVAL = 2  #Cada cuantos segundos se realiza la compensacion de video
COMPENSATION_PRECISION = 1  # cuantos decimales de precision se usan en la compensacion (segundosme dijist)

LOCAL_IN_IP = "192.168.1.122" #Ip a la que se estan reciviendo todos los streams
UDP_GAME = [6660,6661,6662,6663] # Puertos usados para recibir imagen del juego
UDP_CAM = [6670,6671,6672,6673] #Idem para camaras
relay = [] #Lo usaremos para saber si el anterior paquete fue timestamp o data
stream_t = [] #almacenamos el momento exacto en el que se ha recibido un paquete
stream_lag = [] #almacenamos el lag de cada uno de los streams recibidos
compensation_index = [] #Lo usaremos para aplicar la compensacion
databuffer = [] #buffer donde almacenamos los datos del stream, lo que nos permite sincronizarlos
inputs = [] #lista de sockets de entrada (hace falta para el select)
outputs = []
game_socket = [] #Lista de sockets
cam_socket = []
init_seconds = time.time() #momento inicial del programa, puede que sea util para calculos
init_seconds2 = time.time()


#funcion para limpiar consola, cuidado:
#creo bloquea el programa unos ms,porque espera a que el comando finalice y puede provocar perdida de paquetes
#ver si se puede evitar
def clear(): 
    if name=='nt':
        _=system('cls')
    else:
        _=system('clear')

def same(relay,received_data_type): #nos indica si el anterior paquete fue del mismo tipo
    if relay == 't':
        if received_data_type == 't':
            return True
        else:
            return False
    else:
        if received_data_type == 'd':
            return True
        else:
            return False
    

def getIndex(s,inputs):
    index = 0 # reseteamos indice, representa el nº de socket por orden de lista
    for in_socket in inputs: #identificamos que socket es
        if s is in_socket:
            break
        index += 1
    return index

def setup(): #inicialización de las listas y sockets necesarios
    global unpacker
    global relay
    global out_socket

    index = 0 #Indice
    for gp in UDP_GAME:  #Reservamos los puertos de entrada (juego)
        game_socket.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        game_socket[index].bind((LOCAL_IN_IP, gp))
        game_socket[index].setblocking(False)   #establecemos un socket que no bloquee, para no perder paquetes de otros
        index += 1
    index = 0  #Reseteamos el indice
    for cp in UDP_CAM: #Reservamos los puertos de entrada (camaras)
        cam_socket.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        cam_socket[index].bind((LOCAL_IN_IP, cp))
        cam_socket[index].setblocking(False)
        index += 1
    out_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
    unpacker=struct.Struct('18s') #Desempaqueta un string de 18 bytes de la candena udp, contiene el timestamp 

    for gs in game_socket:#añadimos los sockets adecuados a la lista de inputs
        inputs.append(gs)
    for cs in cam_socket:
        inputs.append(cs)
    #inicializamos las dimensiones de las listas, para no provocar errores
    relay = ['d']*len(inputs) # ponemos los reles en d, obligará a que el primer paquete siempre sea data
    index=0
    for n in inputs:
        databuffer.append([b''])
        stream_t.append([-1.0]) 
        compensation_index.append(-1) #iniciamos sin compensacion en ningun video
        stream_lag.append(-1.0) # -1 nos indica que todavia no hay lag disponible
        index += 1 

def rx_process(): #proceso de recepcion y clasificación de los paquetes
    global relay
    index = 0
    readable,writable,exceptional= select.select(inputs,outputs,inputs)
    for s in readable: #iteramos entre todos los socket de entrada que esten listos
        data, addr=s.recvfrom(1316) #recojemos dato
        index= getIndex(s,inputs) #indice del socket actual
        if len(data) == unpacker.size:  #si el tamaño del paquete es 18bytes, es un timestamp
            if(same(relay[index],'t')): #si el paquete anterior no fue un data, ignoramos timestamp
                continue
            relay[index] = 't'
            timestamp=unpacker.unpack(data) #desempaqueta byte
            timestamp=timestamp[0].decode("utf-8") #decodifica
            timestamp=timestamp.replace('\x00','0') #cuando el ultimo caracter es un 0 aparece esta cadena. Tenemos que quitarla
            timestamp=float(timestamp)  #convertimos a float
            stream_lag[index]= time.time()-timestamp
            stream_t[index][-1] = timestamp #insertamos el tiempo en la ultima posicion de la lista
        else:
            databuffer[index].append(data) #almacenamos paquete en buffer
            if(same(relay[index],'d')): #si el paquete anterior fue data, rellenamos con "sin timestamp"
                index += 1
                stream_t[index].append(0.0)
                continue
            relay[index] = 'd'

def calculate_compensation():
    for stream in stream_t: #debido a udp necesitamos ordenar, por el momento sólo ordenaremos los datos de timestamp
        if stream[-1] != 0.0:
            stream.sort()

def send_stream_without_compensation():
    i = 0
    for stream in databuffer:
        print("tamaño de databuffer: ",end='')
        print(len(stream),end=' timebuffer:')
        print(len(stream_t[i]))
        print("ultimo timestamp-", end='index:')
        print(i, end=' time: ')
        print(stream_t[i])
        if len(stream) > 1:
            if i <= 3:
                out_socket.sendto(stream[0],('127.0.0.1',UDP_GAME[i]-100))
                stream.pop(0)
                if len(stream)< len(stream_t[i]):
                    stream_t[i].pop(0)
            else:
                out_socket.sendto(stream[0],('127.0.0.1',UDP_CAM[i-4]-100))
                stream.pop(0)
                if len(stream)< len(stream_t[i]):
                    stream_t[i].pop(0)
        i += 1




#*****************************INICIO DEL PROGRAMA*********************************

setup()
while True:
    rx_process()
    elapsed_seconds=time.time()-init_seconds #Segundos transcurridos de programa con precision decimal
    if elapsed_seconds > COMPENSATION_INTERVAL: # realizamos el proceso de compensacion 
        init_seconds=time.time()
        calculate_compensation()
        
    send_stream_without_compensation() #Envio sin compensacion de lag(para debug o pruebas)

