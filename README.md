# infvsync
_Sincronizacion de video en streaming para proyecto infv_tv_
 
 ## Descripcion 📋
 _Este software sincroniza diversos streams enviados por UDP a un servidor que se encarga de sincronizarlos a todos en el tiempo. El programa cliente, por cada paquete de video, añade un paquete con el timestamp, lo que permite al servidor sincronizarlos en el tiempo.
 
 ## Requisitos
 _Testeado sólo bajo win10 y debian. Cualquier sistema basado en POSIX time (UNIX time) deberia funcionar, no obstante, correrlo en otros sistemas dará un resultado inesperado, ya que este programa se basa en un epoch Unix (UTC del 1 de enero de 1970). Ejecutarlo en otro SO con diferente epoch requiere de una adaptación.

Existen ejecutables ya compilados para win10, no es necesario ningun otro requisito especial._

## Configuración y detalles sobre uso con OBS
_No es necesario configurar ningun puerto en el router, no obstante, se utilizan 4 puertos en total (2 de entrada y 2 de salida), los cuales se pueden configurar a necesidad. Para los puertos de entrada se recomienda usar el loopback(127.0.0.1). Los puertos de salida estarán determinados por el servidor.

El programa dispone de presets de configuracion para los usuarios de infv_tv, no obstante la configuración se puede modificar a mano en el archivo config.cfg, que se genera la primera vez que se ejecuta el programa.
En obs se deben configurar 2 instancias individuales, en una se enviará la pantalla principal (la de juego). Debe configurarse para el envio a través de UDP al loopback y puerto seleccionados en la entrada del infvsync_client. En la segunda instancia se enviará la cámara. Importante establecer un tamaño del paquete de 1316
Estas son las configuraciónes recomendadas:_

*Parametros para la salida de video: udp://x.x.x.x:pppp?pkt_size=1316
*Formato del contenedor:mpegts
*tasa: 2000kbps
*reescalado: Para cámara max. 1280*720, para juego 1920*1080

## Autores ✒️

* **Manuel Bazarra Lorenzo** - *Desarrollo completo del software y lógica de programa* 

## Version 1.1 Alpha
_Se añade sincronización con servidor NTP para correjir posibles desfases entre relojes de los clientes._
