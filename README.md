
# Introducción

V-Rep es un programa que permite realizar simulaciones en tiempo real con robots. Estos pueden ser programados usando scripts en lenguaje LUA. Además provee extensiones para trabajar en otros lenguajes como Matlab, C++, Python de forma remota (via sockets)
Para más información sobre V-rep, visitar su página oficial: http://www.coppeliarobotics.com/

pyvrepclient es un wrapper sobre la extensión de V-rep en Python que facilita el manejo remoto de los objetos del simulador V-rep


# Instalación y uso.

- Clonar esta librería
```
git clone https://github.com/Vykstorm/pyvrepclient.git
```
- Ejecutar el script build.sh para compilar las librerías dinámicas necesarias
```
cd pyvrepclient
./build.sh
```

- Descargar el simulador V-rep de la página oficial (la versión EDU es gratuita)
http://www.coppeliarobotics.com/downloads.html

También puedes ejecutar este código(Linux 64-bit)
```
wget http://coppeliarobotics.com/files/V-REP_PRO_EDU_V3_4_0_Linux.tar.gz
tar -xzvf V-REP_PRO_EDU_V3_4_0_Linux.tar.gz
mv V-REP_PRO_EDU_V3_4_0_Linux vrep
```
- Para ejecutar el simulador, abrir el directorio vrep y ejecutar el script vrep.sh
```
cd vrep
./vrep.sh
```

- Ahora para probar la librería, abre una escena de prueba ya preparada con la opción "Open Scene..." del simulador V-rep.
Abre la escena "epuck_example1.ttt" en el directorio "scenes/" de este repositorio.

- Una vez cargada, ejecuta el script Python epuck.py en el directorio "samples/" y observa que es lo que ocurre en el simulador.




