# infvsync
_Sincronizacion de video en streaming para proyecto infv_tv_
 
 ## Descripcion 📋
 _Este software sincroniza diversos streams enviados por UDP a un servidor que se encarga de sincronizarlos a todos en el tiempo. El programa cliente, por cada paquete de video, añade un paquete con el timestamp, lo que permite al servidor sincronizarlos en el tiempo.
 
 ## Requisitos
 _Testeado sólo bajo win10 y debian. Cualquier sistema basado en POSIX time (UNIX time) deberia funcionar, no obstante, correrlo en otros sistemas dará un resultado inesperado, ya que este programa se basa en un epoch Unix (UTC del 1 de enero de 1970). Ejecutarlo en otro SO con diferente epoch requiere de una adaptación.

Existen ejecutables ya compilados para win10, no es necesario ningun otro requisito especial._

## Configuración y detalles sobre uso con OBS
_No es necesario configurar ningun puerto en el router, no obstante, se utilizan 4 puertos en total (2 de entrada y 2 de salida), los cuales se pueden configurar a necesidad. Para los puertos de entrada se recomienda usar el loopback(127.0.0.1). Los puertos de salida estarán determinados por el servidor.

El programa dispone de presets de configuracion para los usuarios de infv_tv, no obstante la configuración se puede modificar a mano en el archivo config.cfg, que se genera la primera vez que se ejecuta el programa_

## Autores ✒️

* **Manuel Bazarra Lorenzo** - *Desarrollo completo del software y lógica de programa* 

## Version 1.1 Alpha
_Se añade sincronización con servidor NTP para correjir posibles desfases entre relojes de los clientes._
