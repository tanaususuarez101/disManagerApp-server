# DIS Manager app - server
Este proyecto fue generado con Python version 3.7

## Instalación de flask
Instalación de la versión 10.0 de flask ```pip install flask```

## Especificación de la aplicación de Flask.
Para poder utilizar el shell de flask, es necesario declarar la variable de entorno FLASK_APP con la ruta del script que contiene el código de la aplicación de Flask.
Para el caso de windows
``set FLASK_APP=disnamagerapp.py``

## Arrancar servidor web de flask
``run flask``

## Base de datos en flask
Se estará utilizando SQLite para el almacenamiento
``pip install flask-sqlalchemy``

## Migraciones de base de datos
Para poder realizar cambios en la base de datos  es necesario instalar 
``pip install flask-migrate``
