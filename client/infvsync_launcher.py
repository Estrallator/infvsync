# Programa para sincronizar diversos streams, creado por Manuel Bazarra.
# NOTA: enviar un float por udp pierde precision devido al "pack", es mejor enviar un string


import socket
import time
import sys, string, os
from os import system, name
from time import gmtime, strftime
import struct
import configparser

version="LAUNCHER 1.0 BETA"
author="Manuel BL- alias Estrallator"
option=0
preset=0
begin=0
flag=0
#Defaults y presets

UDP_OUT_IP="0.0.0.0" #IP de destino 
UDP_PORT=['5555', '5556'] #Puertos que se utilizaran en el loopback (video local)
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


clear()
logo()
print("Leyendo 'config.cfg' ... ")
if os.path.isfile("config.cfg"):   #Si existe el archivo de configuracion procedemos, en caso contrario ejecutamos el codigo para crearlo
    print("Configuracion localizada, si lo necesitas puedes editar a mano la configuracion, o borrarla para generar una nueva")
    begin=input("\n\npresiona [enter] para comenzar la transmision...")

    os.startfile("sender.exe")
    os.system("sender.exe cam") 

else: #como no existe config generamos una
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
        local['port_game'] = '5555'
        local['port_cam'] = '5556'
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
  
#seconds=time.time() #La fecha actual, en segundos
#sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #socket de entrada
#sock.bind(('127.0.0.1', UDP_PORT))
#out_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #socket de salida






