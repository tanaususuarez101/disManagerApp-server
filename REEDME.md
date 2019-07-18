# DIS Manager app - server
Este proyecto fue generado con Python version 3.7

## Instalación de flask
Instalación de la versión 10.0 de flask ```pip install flask```

## Especificación de la aplicación de Flask.
Para poder utilizar el shell de flask, es necesario declarar la variable de entorno FLASK_APP con la ruta del script que contiene el código de la aplicación de Flask.
Para el caso de windows
``set FLASK_APP=disnamagerapp.py``

## Arrancar servidor
Para iniciar el servidor con flask será necesario ejecutar el siguiente comando:
``run flask``

## Base de datos en flask
Para el almacenamiento en el backend se estará empleado SQLite. Para ello es necesario realizar la instalación  de flask sqlalchemy que facilitará ésta tarea
``pip install flask-sqlalchemy``

## Migraciones de base de datos
Para poder realizar cambios en la base de datos  es necesario instalar 
``pip install flask-migrate``

## Primera migracion DDBB

Para generar las tablas de las bases de datos una vez declarados en el modelo habrá que introduccir el siguiente comando:
+ Primero hay que crear unr epositorio de migración
 ``flask db init``
+ Realizar la migración 
``flask db migrate ``
+ Aplicar los cambios realizados en la migración
``flask db upgrade``

# Archivo xls
PAra manipular los archivos xls y ser guardados en la base de datos se utiliza la libería ``pip install openpyxl``

## Http basic authentification
``
pip install flask-httpauth
``

## Libería JWT
``
pip install Flask-JWT
``