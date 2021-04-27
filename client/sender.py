
# Programa para sincronizar diversos streams, creado por Manuel Bazarra.
# NOTA: enviar un float por udp pierde precision devido al "pack", es mejor enviar un string


import socket
import time
from time import gmtime, strftime
import ntplib
import sys, string, os
from os import system, name
import struct
import configparser

def clear():
    # windows
    if name == 'nt':
        _ = system('cls')
    # mac and linux
    else:
        _ = system('clear')

mode='port_game'
if len(sys.argv)>1:
    if sys.argv[1]=='cam':
        mode='port_cam'

  

version="sender 2.0a"

clear()
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


print("VERSION:"+version)

print("\n\nSincronizando con servidor ntp...")
c = ntplib.NTPClient()
response = c.request('europe.pool.ntp.org', version=3)
offset = response.offset #el offset del reloj local con respecto al ntp, que lo tendremos en cuenta para las operaciones con timestamps
print("Sincronizado correctamente con 'europe.pool.ntp.org'")


print("\n Leyendo configuracion...\n\n")



if os.path.isfile("config.cfg"):   #Si existe el archivo de configuracion procedemos, en caso contrario ejecutamos el codigo para crearlo
    print("Configuracion localizada, leyendo datos...")

    config=configparser.ConfigParser() #Objeto config
    config.read('config.cfg')

    if 'local' in config and 'server' in config and 'config' in config:
     
      UDP_IN_IP = config['local']['ip']
      UDP_OUT_IP = config['server']['ip']
      UDP_IN_PORT = int(config['local'][mode])
      UDP_OUT_PORT = int(config['server'][mode])
      pkt_size = int(config['config']['pkt_size'])

      print(UDP_IN_IP)
      print(UDP_OUT_IP)
      print(UDP_IN_PORT)
      print(UDP_OUT_PORT)

      seconds=time.time() + offset  #La fecha actual, en segundos
      sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #socket de entrada
      sock.bind((UDP_IN_IP, UDP_IN_PORT))
      out_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #socket de salida
      print("\nComenzando retransmisión. No cierres esta ventana.\n Cerrar este programa causa el corte del stream ")
      print("\nGG have fun!")

      separator= b'\\xts'
      while True:  #bucle de envio de datos
          data, addr=sock.recvfrom(pkt_size)  #recibimos 1306 bytes

          btime = time.time() + offset
          btime = str(btime)
          packer= struct.Struct('18s')
          packed_time= packer.pack(btime.encode("utf-8"))

          data2 =  packed_time + separator + data

          out_sock.sendto(data2,(UDP_OUT_IP, UDP_OUT_PORT))

          
else:
    print("No se ha encontrado archivo de configuracion")
    input("Presiona [enter] para finalizar... ")
