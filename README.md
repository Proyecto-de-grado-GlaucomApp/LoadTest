# LoadTest

[English](#english) | [Español](#español)

### README - Español

## Descripción
Este proyecto realiza pruebas de carga en una API para procesar imágenes y evaluar el rendimiento de respuestas concurrentes. Utiliza autenticación mediante un token JWT y se configura a través de variables de entorno.

## Estructura
- `Config`: Administra la configuración de la API a través de variables de entorno.
- `AuthenticationHandler`: Realiza la autenticación para obtener el token JWT.
- `RequestHandler`: Envía solicitudes a la API y recopila métricas de respuesta.
- `LoadTester`: Ejecuta las pruebas de carga, guarda y muestra los resultados.

## Instalación
1. Asegúrate de tener Python instalado.
2. Instala las dependencias necesarias usando:
    ```bash
    pip install -r requirements.txt
    ```

3. Configura las variables de entorno en un archivo `.env`, siguiendo el formato en `LoadTestExample.env`.

## Uso
Ejecuta el script con:
```bash
python nombre_del_script.py
```
Este iniciará pruebas de carga en la API, variando el nivel de concurrencia para analizar el rendimiento.

## Configuración del .env
```plaintext
API_HOST= [Dirección IP o dominio del host de la API]
API_PORT= [Número de puerto de la API]
API_USERNAME= [Usuario para autenticación]
API_PASSWORD= [Contraseña para autenticación]
TEST_IMAGE_PATH= [Ruta de la imagen de prueba]
REQUEST_TIMEOUT= [Tiempo de espera para solicitudes en segundos]
```

---

### README - English

## Description
This project conducts load testing on an API for image processing, assessing performance with concurrent requests. It uses JWT token-based authentication and is configured via environment variables.

## Structure
- `Config`: Manages API settings through environment variables.
- `AuthenticationHandler`: Authenticates and retrieves the JWT token.
- `RequestHandler`: Sends requests to the API and collects response metrics.
- `LoadTester`: Runs load tests, saves, and displays results.

## Installation
1. Make sure Python is installed.
2. Install the required dependencies by running:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables in a `.env` file, following the format in `LoadTestExample.env`.

## Usage
Run the script with:
```bash
python script_name.py
```
This will initiate load testing on the API, varying concurrency levels to analyze performance.

## .env Configuration
```plaintext
API_HOST= [API host IP or domain]
API_PORT= [API port number]
API_USERNAME= [API authentication username]
API_PASSWORD= [API authentication password]
TEST_IMAGE_PATH= [Path to the test image]
REQUEST_TIMEOUT= [Request timeout duration in seconds]
```
