# Programa para sincronizar diversos streams, creado por Manuel Bazarra.
# NOTA: enviar un float por udp pierde precision devido al "pack", es mejor enviar un string


import socket
import time
import sys, string, os
from os import system, name
from time import gmtime, strftime
import struct
import configparser
import ntplib
import threading

version="LAUNCHER 2.0 BETA"
author="Manuel BL- alias Estrallator"
option=0
preset=0
begin=0
flag=0
#Defaults y presets
UDP_OUT_IP="0.0.0.0" #IP de destino 
UDP_IN=['5555', '5556'] #Puertos que se utilizaran en el loopback (video local)
UDP_OUT=['1234','1234'] #Puertos de la IP de destino
PRESET =['6663','6673'],['6660','6670'],['6661','6671'],['6662','6672'],['6664','6674'] #Presets
PKT_SIZE='1316' #tamaño por defecto del paquete udp
config=configparser.ConfigParser() #Objeto config

def clear():
    # windows
    if name == 'nt':
        _ = system('cls')
    # mac and linux
    else:
        _ = system('clear')

def logo():
    print("""\n$$$$$$\\ $$\\   $$\\ $$$$$$$$\\ $$\\    $$\\     
\\_$$  _|$$$\\  $$ |$$  _____|$$ |   $$ |      
  $$ |  $$$$\\ $$ |$$ |      $$ |   $$ |     
  $$ |  $$ $$\\$$ |$$$$$\\    \\$$\\  $$  |      
  $$ |  $$ \\$$$$ |$$  __|    \\$$\\$$  /     
  $$ |  $$ |\\$$$ |$$ |        \\$$$  /       
$$$$$$\\ $$ | \\$$ |$$ |         \\$  /         
\\______|\\__|  \\__|\\__|          \\_/    \n """)

    print(""" $$$$$$\\ $$$$$$$$\\ $$$$$$$\\  $$$$$$$$\\  $$$$$$\\  $$\\      $$\\        $$$$$$\\ $$\\     $$\\ $$\\   $$\\  $$$$$$\\  
$$  __$$\\\\__$$  __|$$  __$$\\ $$  _____|$$  __$$\\ $$$\\    $$$ |      $$  __$$\\\\$$\\   $$  |$$$\\  $$ |$$  __$$\\ 
$$ /  \\__|  $$ |   $$ |  $$ |$$ |      $$ /  $$ |$$$$\\  $$$$ |      $$ /  \\__|\\$$\\ $$  / $$$$\\ $$ |$$ /  \\__|
\\$$$$$$\\    $$ |   $$$$$$$  |$$$$$\\    $$$$$$$$ |$$\\$$\\$$ $$ |      \\$$$$$$\\   \\$$$$  /  $$ $$\\$$ |$$ |    
 \\____$$\\   $$ |   $$  __$$< $$  __|   $$  __$$ |$$ \\$$$  $$ |       \\____$$\\   \\$$  /   $$ \\$$$$ |$$ | 
$$\\   $$ |  $$ |   $$ |  $$ |$$ |      $$ |  $$ |$$ |\\$  /$$ |      $$\\   $$ |   $$ |    $$ |\\$$$ |$$ |  $$\\     
\\$$$$$$  |  $$ |   $$ |  $$ |$$$$$$$$\\ $$ |  $$ |$$ | \\_/ $$ |      \\$$$$$$  |   $$ |    $$ | \\$$ |\\$$$$$$  |   
 \\______/   \\__|   \\__|  \\__|\\________|\\__|  \\__|\\__|     \\__|       \\______/    \\__|    \\__|  \\__| \\______/\n\n""")

    print("Autor: " +author)
    print("VERSION:"+version+"\n\n")

def menu():
    print("\n\nMENU:")
    print("1 - Escojer un preset InfV\n2 - Generar config manual\n3 - Sobre 'Infv Stream Sync' y OBS ")

def info():
    clear()
    logo()
    print("Info")
    input("presiona [enter] para continuar...")


def generate_config():   ##Funcion para generar una nueva configuracion en caso de que no exista
    global flag
    global option
    global preset
    global begin

    print("No existe archivo de configuracion, se procederá a generar una nueva configuracion.")
    input("presiona [enter] para continuar...")
    config['local']={}
    config['server']={}
    config['config'] = {}
    config['config']['pkt_size']= PKT_SIZE
    local = config['local']
    server = config['server']
    while flag==0: #Bucle del menú
        clear()
        logo()
        menu()
        option=input("Introduce opcion:")
        if option=='1':
            clear()
            logo()
            print("Escoje un preset\n")
            print("1-Estrallator\n2-Emmet\n3-ManiaK\n4-TipToe\n5-Strabe\nCualquier otra para volver\n\n")
            preset=input("Introduce opcion: ")
            if preset == '1' or preset == '2' or preset == '3' or preset == '4' or preset == '5':
                flag=1
                preset = int(preset)
        elif option=='2':
            print("opcion2")
        elif option=='3':
            info()
    clear()
    logo()
    UDP_OUT_IP=input("Introduce la IP del SERVER: ")
    if preset:
        preset -= 1
        local['ip'] = '127.0.0.1'
        local['port_game'] = UDP_IN[0]
        local['port_cam'] = UDP_IN[1]
        server['ip'] = UDP_OUT_IP
        server['port_game'] = PRESET[preset][0]
        server['port_cam'] = PRESET[preset][1]
        with open('config.cfg', 'w') as configfile:
            config.write(configfile)
        print("\n\nSe ha generado un archivo de configuracion, puedes revisar los datos en config.cfg .")
        print("Vuelve a ejecutar este programa para iniciar la transmisión")
        input("presiona [enter] para finalizar...")
              
    else:
        local['ip'] = input("IP transmision local(por lo general 127.0.0.1) : ")
        local['port_game'] = input("Puerto local game: ")
        local['port_cam'] = input("Puerto local cam: ")
        server['ip'] = UDP_OUT_IP
        server['port_game'] = input("Puerto SERVER para juego: ")
        server['port_cam'] = input("Puerto SERVER para cam: ")
        with open('config.cfg', 'w') as configfile:
            config.write(configfile)
        print("\n\nSe ha generado un archivo de configuracion, puedes revisar los datos en config.cfg .")
        print("Vuelve a ejecutar este programa para iniciar la transmisión")
        input("presiona [enter] para finalizar...")


def show_config():          #Mostramos la configuracion antes de iniciar el programa
    print("\n\n******Mostrando parametros******")
    print("Recibiendo streams en: ",end='\033[2;32;40m')
    print(UDP_IN_IP, end=' \033[1;37;40m')
    print("GAME: ", end='\033[1;32;40m')
    print(UDP_GAME_IN_PORT,end=' \033[1;37;40mCAM: \033[1;32;40m')
    print(UDP_CAM_IN_PORT)
    print("\033[1;37;40mEnviando streams a: ", end='\033[1;32;40m')
    print(UDP_OUT_IP, end=' ')
    print("\033[1;37;40mGAME: ", end='\033[1;32;40m')
    print(UDP_GAME_OUT_PORT,end='\033[1;37;40m CAM: \033[1;32;40m')
    print(UDP_CAM_OUT_PORT, end='\033[1;37;40m')


def parse_config():   # Parseamos el archivo de config y asignamos la variables necesarias
    print("Verificando configuracion...")
    global UDP_IN_IP
    global UDP_OUT_IP
    global UDP_GAME_IN_PORT
    global UDP_GAME_OUT_PORT
    global UDP_CAM_IN_PORT
    global UDP_CAM_OUT_PORT
    global PKT_SIZE
    config=configparser.ConfigParser() #Objeto config
    config.read('config.cfg')
    if 'local' in config and 'server' in config and 'config' in config:
      UDP_IN_IP = config['local']['ip']
      UDP_OUT_IP = config['server']['ip']
      UDP_GAME_IN_PORT = int(config['local']['port_game'])
      UDP_GAME_OUT_PORT = int(config['server']['port_game'])
      UDP_CAM_IN_PORT = int(config['local']['port_cam'])
      UDP_CAM_OUT_PORT = int(config['server']['port_cam'])
      PKT_SIZE = int(config['config']['pkt_size'])
      show_config()
    else:
        print("ERROR, la configuracion tiene un formato incorrecto o faltan parámetros. Borra config.cfg y genera uno nuevo.")
        input("Finaliza este programa antes de continuar...")
def game_stream_process(offset,lock):

    game_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #socket de entrada
    game_sock.bind((UDP_IN_IP, UDP_GAME_IN_PORT))
    game_out_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #socket de salida
    separator= b'\\xts'
    while True:  #bucle de envio de datos

      game_data, addr=game_sock.recvfrom(PKT_SIZE)  #recibimos 1316 bytes
      game_time = time.time() + offset
      game_time = str(game_time)
      packer= struct.Struct('18s')
      packed_time= packer.pack(game_time.encode("utf-8"))
      cooked_game_data =  packed_time + separator + game_data
      game_out_sock.sendto(cooked_game_data,(UDP_OUT_IP, UDP_GAME_OUT_PORT))
      #game_out_sock.sendto(game_data,(UDP_OUT_IP, UDP_GAME_OUT_PORT))

      #print("sent: ", end='')
      #print(len(cooked_game_data), end=' bytes\n')
  

def cam_stream_process(offset, lock):
    cam_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #socket de entrada
    cam_sock.bind((UDP_IN_IP, UDP_CAM_IN_PORT))
    cam_out_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #socket de salida
    separator= b'\\xts'
    while True:  #bucle de envio de datos

      cam_data, addr=cam_sock.recvfrom(PKT_SIZE)  #recibimos 1316 bytes
      cam_time = time.time() + offset
      cam_time = str(cam_time)
      packer= struct.Struct('18s')
      packed_time= packer.pack(cam_time.encode("utf-8"))
      cooked_cam_data =  packed_time + separator + cam_data
      cam_out_sock.sendto(cooked_cam_data,(UDP_OUT_IP, UDP_CAM_OUT_PORT))




################################### MAIN PROGRAM ##############################################
clear()
logo()
print("Leyendo 'config.cfg' ... ")

if os.path.isfile("config.cfg"):   #Si existe el archivo de configuracion procedemos, en caso contrario ejecutamos el codigo para crearlo
    print("Configuracion localizada, si lo necesitas puedes editar a mano la configuracion, o borrarla para generar una nueva")

    parse_config()

    print("\n\nSincronizando con servidor ntp...")

    c = ntplib.NTPClient()
    response = c.request('europe.pool.ntp.org', version=3)
    offset = response.offset    #el offset del reloj local con respecto al ntp, que lo tendremos en cuenta para las operaciones con timestamps

    print("Sincronizado correctamente con 'europe.pool.ntp.org'")
    begin=input("\n\npresiona [enter] para comenzar la transmision...")
    print("----->EMITIENDO<-------")

    lock = threading.Lock()
    game_thread=threading.Thread(target=game_stream_process,args=(offset,lock, ) , daemon=True)
    cam_thread=threading.Thread(target=cam_stream_process,args=(offset,lock, ) , daemon=True)
    

    game_thread.start()
    cam_thread.start()

    while True:   # bucle principal, lo necesitamos, de lo contrario los hilos morirían
        time.sleep(1) # evitamos que los hilos colapsen añadiendo un tiempo entre iteraciones

else: #como no existe config generamos una
    generate_config()
    





