# CinePlus

Aplicación Flask para consultar el catálogo de películas guardado en MongoDB.

## Configuración

1. Crear y activar un entorno virtual de Python.
2. Instalar dependencias con `pip install -r requirements.txt`.
3. Definir `MONGODB_URI` con la cadena de conexión del proyecto y, opcionalmente, `MONGODB_DATABASE` (por defecto `cineplus`). `.env.example` muestra los nombres de configuración; no contiene credenciales.
4. Ejecutar `python app.py` y abrir `http://127.0.0.1:5000/movies`.

La colección se llama `movies`. HU-05 espera documentos con `title`, `genre`, `year` y `poster_url`, junto con los campos de película definidos para el registro.

## HU-05 · Catálogo

La página `/movies` muestra tarjetas con título, género, año y póster, enlaces visibles de acciones y un estado vacío cuando la colección no tiene registros. Las rutas de crear, consultar, editar y eliminar corresponden a las demás historias CRUD y deben integrarse con este catálogo.
