
# Programa para sincronizar diversos streams, creado por Manuel Bazarra.
# NOTA: enviar un float por udp pierde precision devido al "pack", es mejor enviar un string


import socket
import time
from time import gmtime, strftime
import struct

version="1.0 BETA"

UDP_IP="127.0.0.1"
UDP_PORT=5005
UDP_OUT=6666

print("InfV Streaming Sync \n Creado por Manuel BL, alias 'Estrallator'\n para uso exclusivo del grupo InfV")
print("VERSION:"+version)
print("\nConfigurando...\n\n")
UDP_IP=input("Introduce la IP de destino: ")
UDP_PORT=input("Introuce puerto de ENTRADA: ")
UDP_OUT=input("Introduce puerto de SALIDA: ")
print("\n La ip introducida es: "+ UDP_IP +"\n El stream se redirigirá del puerto "+UDP_PORT+" hacia el " + UDP_OUT )
print("Comenzando retransmisión. No cierres esta ventana.\n Cerrar este programa causa el corte del stream ")
print("GG have fun!")

UDP_PORT=int(UDP_PORT)
UDP_OUT=int(UDP_OUT)

seconds=time.time() #La fecha actual, en segundos
sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #socket de entrada
sock.bind(('127.0.0.1', UDP_PORT))
out_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #socket de salida



print("\n\nPuertos configurados...Iniciando...")

while True:
    data, addr=sock.recvfrom(1306)  #recibimos 1306 bytes
    local_time=strftime("%H:%M:%S.%f", gmtime())[:-3]  

    out_sock.sendto(data,(UDP_IP, UDP_OUT))   #enviamos una cadena

    btime = seconds#test, pasamos un tiempo cualquiera a bytes
    btime = str(btime)
    packer= struct.Struct('18s')
    out_sock.sendto(packer.pack(btime.encode("utf-8")),(UDP_IP, UDP_OUT))# enviamos la hora a la que fue enviado el stream para realizar sync
    
    
