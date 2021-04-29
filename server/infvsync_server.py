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
import threading

version = "Server 2.2 ALPHA"

COMPENSATION_INTERVAL = 5  #Cada cuantos segundos se realiza la compensacion de video
COMPENSATION_PRECISION = 2  # cuantos decimales de precision se usan en la compensacion (segundosme dijist)
LOCAL_IN_IP = "192.168.0.11" #Ip a la que se estan reciviendo todos los streams
BUFFERING_TIME= 0 #Segundos de carga del buffer (no se emite en este intervalo)

UDP_GAME = [6660,6661,6662,6663] # Puertos usados para recibir imagen del juego
UDP_CAM = [6670,6671,6672,6673] #Idem para camaras



timebuffer = [] #almacenamos el momento exacto en el que se ha recibido un paquete
stream_lag = [] #almacenamos el lag de cada uno de los streams recibidos
rx_thread = [] #lista de hilos
compensation_index = [] #Lo usaremos para aplicar la compensacion
databuffer = [] #buffer donde almacenamos los datos del stream, lo que nos permite sincronizarlos
buffer_min_size=[] #Tamaño minimo que debe tener el buffer (autocalculado)
inputs = [] #lista de sockets de entrada (hace falta para el select)
outputs = []
game_socket = [] #Lista de sockets
cam_socket = []
compensation_timer = time.time() 
buffering_timer = time.time()


#funcion para limpiar consola, cuidado:
#creo bloquea el programa unos ms,porque espera a que el comando finalice y puede provocar perdida de paquetes
#ver si se puede evitar
def clear(): 
    if name=='nt':
        _=system('cls')
    else:
        _=system('clear')


def getIndex(s,inputs):
    index = 0 # reseteamos indice, representa el nº de socket por orden de lista
    for in_socket in inputs: #identificamos que socket es
        if s is in_socket:
            break
        index += 1
    return index

def setup(): #inicialización de las listas y sockets necesarios
    global unpacker
    global out_socket
    global inputs   
    global rx_thread

    index = 0 #Indice
    for gp in UDP_GAME:  #Reservamos los puertos de entrada (juego)
        game_socket.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        game_socket[index].bind((LOCAL_IN_IP, gp))
        #game_socket[index].setblocking(False)   #establecemos un socket que no bloquee, para no perder paquetes de otros
        index += 1
    index = 0  #Reseteamos el indice
    for cp in UDP_CAM: #Reservamos los puertos de entrada (camaras)
        cam_socket.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        cam_socket[index].bind((LOCAL_IN_IP, cp))
        #cam_socket[index].setblocking(False)
        index += 1
    out_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
    unpacker=struct.Struct('18s') #Desempaqueta un string de 18 bytes de la candena udp, contiene el timestamp 

    for gs in game_socket:#añadimos los sockets adecuados a la lista de inputs
        inputs.append(gs)
    for cs in cam_socket:
        inputs.append(cs)
    #inicializamos las dimensiones de las listas, para no provocar errores
    index=0
    for n in inputs:
        rx_thread.append(threading.Thread(target=rx_process,args=(n,), daemon=True))
        databuffer.append([b''])
        timebuffer.append([-1.0]) 
        compensation_index.append(-1) #iniciamos sin compensacion en ningun video
        stream_lag.append(-1.0) # -1 nos indica que todavia no hay lag disponible
        buffer_min_size.append(0)
        index += 1 

def rx_process(sk): #proceso de recepcion y clasificación de los paquetes
    
    global timebuffer
    global databuffer
    global inputs

    while True:
        data, addr=sk.recvfrom(1338) #recojemos dato
        index= getIndex(sk,inputs) #indice del socket actual
        #print(index)
        #print(len(data))
        #ATENCION del paquete recibido,[0:22] contiene timestamp+separador
        #el resto  [22:] es datos
        #lock.acquire()
        if len(data) > 1000:
            databuffer[index].append(data)
            #lock.release()

            


########################################################################################################################################
#                                                       CALCULO DE LA COMPENSACION                                                     #
# Primero debemos tener unos segundos de grabacion almacenados en el buffer                                                            #
# De los streams activos, localizamos el que EMPIECE por un timestamp más alto. Con este dato, comparamos en el resto de streams       #
# en que índice del buffer se encuetra este mismo tiempo, lo que nos dará un offset a partir del cual debemos emitir para compensar    #
# los delays                                                                                                                           #
########################################################################################################################################
def calculate_compensation(): 
    global databuffer
    #for stream in databuffer:
    #    for packet in stream:
    #        print(packet[0:22])
    #print(timebuffer[7])
    #max_time = [0,0,0,0,0,0,0,0]
    #active_streams = []
    
    #i = 0
    #for stream in timebuffer: #debido a udp necesitamos ordenar, por el momento sólo ordenaremos los datos de timestamp
    #    if stream[-1] != 0.0:
    #        stream.sort()
    #        if stream[0] != -1.0:  #sólo nos interesan streams que tengan timestamp asignados
    #            max_time[i] = stream[0]
    #            active_streams.append(i)            
    #    i += 1
    #reference_time = max(max_time)    #El valor más alto es eĺ que nos interesa
    #reference_time = round(reference_time, COMPENSATION_PRECISION) #Trabajamos con la precision decimal configurada 
    
    #print("Listado de tiempos: ", end='')
    #print(max_time)
    #print('Tiempo seleccionado de referencia: ', end='')
    #print(reference_time)
    #print('Streams detectados como activos: ', end='')
    #print(active_streams)
    #print("Tamaño de los timebuffer: ")
    #for index in active_streams:
    #    print("Stream index: ", end='')
    #    print(index, end=' Tamaño: ')
    #    print(len(timebuffer[index]))

    #Calculamos el indice de compensación, pero sólo procesamos los stream que tengan timestamps
    #for index in active_streams:
    #    compensation_index[index] = 0
    #    for t in timebuffer[index]:
    #        if t >= reference_time: 
    #            print("localizado timestamp coincidente: ", end='')
    #            print(t, end=' para stream con índice: ')
    #            print(index)
    #            break
    #        if index == len(timebuffer[index])-1:
    #            print("* Se ha llegado al final de la lista sin timestamp coincidente para el stream con indice: ", end='')
    #            print(index)
    #            break
    #        compensation_index[index] += 1

    #print(compensation_index)



def send_stream_without_compensation(buffer_time, lock):
    global out_socket
    global databuffer
    elapsed = time.time() - buffering_timer
    while True:
        if elapsed >= buffer_time:

            i = 0
            for stream in databuffer:
                if len(stream) > 1:
                    if i <= 3:
                        #lock.acquire()
                        out_socket.sendto(stream[0][22:],('127.0.0.1',UDP_GAME[i]-100))
                        stream.pop(0)
                        #lock.release()
                    else:
                        #lock.acquire()
                        out_socket.sendto(stream[0],('127.0.0.1',UDP_CAM[i-4]-100))
                        stream.pop(0)
                        #lock.release()
                i += 1
        
    


#*****************************INICIO DEL PROGRAMA*********************************

setup()

lock = threading.Lock()

for rxt in rx_thread:
    rxt.start()

tx_thread = threading.Thread(target=send_stream_without_compensation,args=(0,lock,), daemon=True)
tx_thread.start()

print("emitiendo")
while True:
    #elapsed_seconds=time.time()-compensation_timer  #Segundos transcurridos de programa con precision decimal
    #if elapsed_seconds > COMPENSATION_INTERVAL: # realizamos el proceso de compensacion 
        #compensation_timer=time.time()
        #calculate_compensation()
    #send_stream_without_compensation(0) #Envio sin compensacion de lag(para debug o pruebas) con un tiempo de almacenado en buffer
    #send_stream_with_compensation(10.0)
    time.sleep(1)
