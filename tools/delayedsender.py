
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



mode='port_game'
if len(sys.argv)>1:
    if sys.argv[1]=='cam':
        mode='port_cam'

init_time = time.time()
buffer_data = []
buffer_time = []
DELAY_TIME = 5.0

version="DelayedSend release 1.0"
 

def clear():
    # windows
    if name == 'nt':
        _ = system('cls')
    # mac and linux
    else:
        _ = system('clear')

def initscreen():
  clear()
  print("DELAYED SEND  TESTING TOOL\n\n\n")
  print("VERSION:"+version)

def ntpsync():
  c = ntplib.NTPClient()
  response = c.request('europe.pool.ntp.org', version=3)
  
  return response.offset #el offset del reloj local con respecto al ntp, que lo tendremos en cuenta para las operaciones con timestamps

def setup():
  global UDP_IN_IP
  global UDP_OUT_IP
  global UDP_IN_PORT
  global UDP_OUT_PORT1
  global UDP_OUT_PORT2
  global pkt_size
  global sock
  global out_sock
  global seconds

  UDP_IN_IP = "127.0.0.1"
  UDP_OUT_IP = "192.168.1.122"
  UDP_IN_PORT = 5555
  UDP_OUT_PORT1 = 6660
  UDP_OUT_PORT2 = 6661
  pkt_size = 1316
  sock =socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #socket de entrada
  sock.bind((UDP_IN_IP, UDP_IN_PORT))
  out_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #socket de salida
  seconds=time.time() + offset  #La fecha actual, en segundos
  #Print config
  print(UDP_IN_IP)
  print(UDP_IN_PORT)
  print("\nSe retransmitirá por duplicado a:")
  print(UDP_OUT_IP)
  print("\nsin delay: ", end='')
  print(UDP_OUT_PORT1, end='  Con delay: ')
  print(UDP_OUT_PORT2)
      


#**************************INICIO DEL PROGRAMA************************************
initscreen()
print("\n\nSincronizando con servidor ntp...")
offset = ntpsync()
print("Sincronizado correctamente con 'europe.pool.ntp.org'")
print("\n Leyendo configuracion...\n\n")
setup()
print("\nComenzando retransmisión. No cierres esta ventana.\n Cerrar este programa causa el corte del stream ")
print("\nGG have fun!")

while True:  #bucle de envio de datos
  data, addr=sock.recvfrom(pkt_size)  #recibimos bytes
  btime = time.time() + offset
  btime = str(btime)
  packer= struct.Struct('18s')
  
  buffer_data.append(data)  #buffer data (para el delay)
  buffer_time.append(packer.pack(btime.encode("utf-8"))) #buffer time(para el delay)

  out_sock.sendto(data,(UDP_OUT_IP, UDP_OUT_PORT1))   #enviamos paquete de datos al instante
  out_sock.sendto(packer.pack(btime.encode("utf-8")),(UDP_OUT_IP, UDP_OUT_PORT1)) # paquete de tiempo

  if time.time() - init_time >= DELAY_TIME: #envio con delay
     out_sock.sendto(buffer_data[0],(UDP_OUT_IP, UDP_OUT_PORT2))   #enviamos una cadena
     buffer_data.pop(0)
     out_sock.sendto(buffer_time[0],(UDP_OUT_IP, UDP_OUT_PORT2))# enviamos timestamp
     buffer_time.pop(0)
          

 

