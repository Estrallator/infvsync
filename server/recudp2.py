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

#funcion para limpiar consola, cuidado:
#creo bloquea el programa unos ms,porque espera a que el comando finalice y puede provocar perdida de paquetes
#ver si se puede evitar
def clear(): 
    if name=='nt':
        _=system('cls')
    else:
        _=system('clear')

def same(relay,received_data_type):#received_data_type d (data) o tipo t (time) relay 1 data 0 time
    if relay == 0:
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
    i = 0 # reseteamos indice, representa el nº de socket por orden de lista
    for in_s in inputs: #identificamos que socket es
        if s is in_s:
            break
        i += 1
    return i


COMPENSATION_INTERVAL = 2  #Cada cuantos segundos se realiza la compensacion de video
COMPENSATION_PRECISION = 3  # cuantos decimales de precision se usan en la compensacion (segundosme dijist)

LOCAL_IN_IP = "192.168.0.11" #Ip a la que se estan reciviendo todos los streams
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


i = 0 #Indice
for gp in UDP_GAME:  #Reservamos los puertos de entrada (juego)
    game_socket.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
    game_socket[i].bind((LOCAL_IN_IP, gp))
    game_socket[i].setblocking(False)   #establecemos un socket que no bloquee, para no perder paquetes de otros
    i += 1
i = 0  #Reseteamos el indice
for cp in UDP_CAM: #Reservamos los puertos de entrada (camaras)
    cam_socket.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
    cam_socket[i].bind((LOCAL_IN_IP, cp))
    cam_socket[i].setblocking(False)
    i += 1

#socket de salida, ni hace falta reservarlo, ni es necesario crear uno por puerto
out_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
unpacker=struct.Struct('18s') #Desempaqueta un string de 18 bytes de la candena udp, contiene el timestamp 

for gs in game_socket:#añadimos los sockets adecuados a la lista de inputs
    inputs.append(gs)
for cs in cam_socket:
    inputs.append(cs)

#inicializamos las dimensiones de las listas, para no provocar errores
relay = ['d']*len(inputs) # ponemos los reles en d, obligará a que el primer paquete siempre sea data
databuffer = []
stream_t = []
i=0;
for n in inputs:
    databuffer.append([b''])
    stream_t.append([-1.0]) 
    compensation_index.append(1) #iniciamos sin compensacion en ningun video
    stream_lag.append(-1.0) # -1 nos indica que todavia no hay lag disponible
    i += 1 


#bucle de programa
#se usa select para poder comprobar cuándo hay datos disponibles en un socket sin que se bloquee la ejecucion
#asi evitamos perder paquetes en la medida de lo posible
while True:
    readable,writable,exceptional= select.select(inputs,outputs,inputs)
    for s in readable: #iteramos entre todos los socket de entrada que esten listos
        data, addr=s.recvfrom(1316) #recojemos dato
        i= getIndex(s,inputs) #indice del socket actual
        if len(data) == unpacker.size:  #si el tamaño del paquete es 18bytes, es un timestamp
            if(same(relay[i],'t')): #si el paquete anterior no fue un data, ignoramos timestamp
                continue
            relay[i] = 't'
            timestamp=unpacker.unpack(data) #desempaqueta byte
            timestamp=timestamp[0].decode("utf-8") #decodifica
            timestamp=timestamp.replace('\x00','0') #cuando el ultimo caracter es un 0 aparece esta cadena. Tenemos que quitarla
            timestamp=float(timestamp)  #convertimos a float
            stream_lag[i]= time.time()-timestamp
            stream_t[i][-1] = timestamp #insertamos el tiempo en la ultima posicion de la lista
        else:
            databuffer[i].append(data) #almacenamos paquete en buffer
            if(same(relay[i],'d')): #si el paquete anterior fue data, rellenamos con "sin timestamp"
                stream_t[i].append(0)
                continue
            relay[i] = 'd'
            #out_sock.sendto(data,(UDP_IP, UDP_OUT))

        #en este punto deberiamos tener una lista ordenada de buffers y lags, cuya primera dimension en ambos,
        #coincide con el indice de socket y su segunda dimension es el nº de paquete recibido.
        #Dicho de otra manera, tenemos una lista de datos con su correspondiente timestamp en el mismo nº de indice.
    

    elapsed_seconds=time.time()-init_seconds #Segundos transcurridos de programa con precision decimal

    if( elapsed_seconds > COMPENSATION_INTERVAL):
        init_seconds=time.time()
        print("lag values:")
        print(stream_lag)
        #Obtenemos en que punto del buffer tenemos que trabajar para que haya sync de videos
        most_laggy_index = stream_lag.index(max(stream_lag)) #averiguamos que stream es el de mayor lag
        

        #most_laggy_specific_second = round(stream_t[most_laggy_index][-2],COMPENSATION_PRECISION) #Que segundo obtuvimos del video de mas lag
        most_laggy_specific_second = stream_t[most_laggy_index][-2]#Que segundo obtuvimos del video de mas lag
        
        print(stream)
        for stream in stream_t: #debido a udp necesitamos ordenar
            stream=stream.sort()
        print(stream)
        print("most_laggy")
        print(most_laggy_specific_second)
        i = 0 # este indice representa el stream con el que trabajamos (0-7)
        for stream in stream_t:# por cada stream ver en que indice está el segundo más atrasado
            for t in stream:
                if t < 0:
                    continue
                if t <= most_laggy_specific_second:
                    print(t,end='')
                    print("  ")
                    print(most_laggy_specific_second)

                    break
                compensation_index[i] += 1
            i += 1

        print("\ncompensation")     
        print(compensation_index)
        

  
    #realizamos envio de datos
    i = 0
    for stream in databuffer:
        if len(stream) > 500:
            if i <= 3:
                out_socket.sendto(stream[compensation_index[i-1]],('127.0.0.1',UDP_GAME[i]-100))
                stream.pop(0)
            else:
                out_socket.sendto(stream[compensation_index[i-1]],('127.0.0.1',UDP_CAM[i-4]-100))
                stream.pop(0)
        i += 1

    #************************************************
    #{k: v for k, v in sorted(number_list.items(), key=lambda item: item[1], reverse=True)} #ordenar lista


    

    #Version antigua, no vale para nada, solo referencia
    #if len(buffer0)>1 and len(buffer1)>1:
    #    print("ENTRO")
    #    if delay >= delay2:
    #        if elapsed_seconds > delay:
    #            out_sock.sendto(buffer0[0],(UDP_IP, UDP_OUT))
    #            buffer0.pop(0)
    #        out_sock.sendto(buffer1[0],(UDP_IP, UDP_OUT2))
    #        buffer1.pop(0)
    #    else:
    #        if elapsed_seconds > delay2:
    #            out_sock.sendto(buffer1[0],(UDP_IP, UDP_OUT2))
    #            buffer1.pop(0)
    #        out_sock.sendto(buffer0[0],(UDP_IP, UDP_OUT))
    #        buffer0.pop(0)



    #print("delay1:", end='')
    #print(delay)
    #print("delay2:", end='')
    #print(delay2)
    
   

