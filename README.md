# International laboratory
Se desea modelar el proceso de aprobación de medicamentos en un laboratorio internacional.

Proyecto realizado en *Django3.1*.

La base de datos está administrada por el gestor Postgresql y hosteada en Heroku, no se necesita una base local.

## [Guía del Proyecto]

+ Importar en Bonita Soft el archivo international_laboratory/AprobacionDeMedicamentos-1.0.bos

## Deploy del proyecto internacional_laboratory

- Crear virtualenv de python3 y activarla
- Instalar dependencias del proyecto
  - `cd international_laboratory`
  - `pip install -r requirements.txt`
- Correr servidor de python
  - `python manage.py runserver`
- Logearse en `/`


### Features

+ `/admin` con gestión integral de todo el proyecto
+ ABM de Actividades y Protocolos, los cuales son reulizables
+ `/monitoreo` 
