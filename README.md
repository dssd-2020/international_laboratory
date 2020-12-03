# International laboratory
Se desea modelar el proceso de aprobación de medicamentos en un laboratorio internacional.

Proyecto realizado en *Django3.1*.

La base de datos está administrada por el gestor Postgresql y hosteada en Heroku, no se necesita una base local.

La aplicación Cloud se encuentra en la carpeta remote-laboratory-2020 y deployada en el servidor Heroku en: 
- `http://remote-laboratory-2020.herokuapp.com/`.

El código de todo el proyecto se encuentra almacenado en el siguiente repositorio de GitHub:
- `https://github.com/dssd-2020/international_laboratory`

## [Guía del Proyecto]

+ Importar en Bonita Soft el archivo international_laboratory/AprobacionDeMedicamentos-1.0.bos
+ Desplegar la organización Grupo02

## Deploy del proyecto internacional_laboratory

- Crear virtualenv de python3 y activarla
- Instalar dependencias del proyecto
  - `cd international_laboratory`
  - `pip install -r requirements.txt`
- Correr servidor de python
  - `python manage.py runserver`
- Logearse en `/`


### Features

+ `/admin` con gestión integral de todo el sistema
+ ABM de Actividades y Protocolos, los cuales son reulizables
+ `/monitoreo`para las consultas gerenciales
