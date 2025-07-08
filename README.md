
# Documentación de Instalación DVM

## Requisitos Previos
Antes de comenzar con la instalación, asegúrate de contar con lo siguiente:

- Tablet con sistema operativo basado en Linux.
- Acceso como administrador (root) en la tablet.
- Conexión a Internet en la tablet, ya sea por Wi-Fi o mediante un cable Ethernet.

## Pasos para la Instalación

### 1. Conectar la Tablet a Internet
- Si utilizas Wi-Fi, abre la configuración de red en la tablet y selecciona tu red Wi-Fi.
- Si prefieres Ethernet, simplemente conecta el cable a la tablet.

### 2. Descargar los Archivos Necesarios
Tienes dos opciones para obtener los archivos del sistema:

**Opción 1: Usar Git**  
Si tienes acceso a Internet, abre una terminal y escribe el siguiente comando para descargar los archivos necesarios:
```bash
git clone https://github.com/darkflowsrl/DVM-Scripts.git /root/DVM-Scripts
```
Si no tienes Git instalado, puedes instalarlo ejecutando este comando:
```bash
apt-get install -y git
```

**Opción 2: Usar un Pendrive**  
Si prefieres no usar Internet, conecta un pendrive con los archivos `DVM-Scripts` y copia la carpeta al directorio `/root` de la tablet utilizando el explorador de archivos de la tablet.

### 3. Dar Permisos a los Archivos
Ahora, es necesario asegurarse de que los archivos se puedan ejecutar correctamente. Para esto, ejecuta el siguiente comando en la terminal:
```bash
chmod +x -R /root/DVM-Scripts
```

### 4. Ejecutar el Instalador
Una vez que los archivos estén listos, sigue estos pasos para comenzar la instalación:

- Abre una terminal.
- Escribe estos comandos para ejecutar el instalador:
  ```bash
  cd /root/DVM-Scripts
  ./setup.sh
  ```
Este paso instalará todos los componentes del software, tanto el sistema interno (backend) como el externo (frontend), además de otras herramientas necesarias.

### 5. Reiniciar la Tablet
Después de la instalación, reinicia la tablet escribiendo en la terminal:
```bash
reboot
```
Al reiniciar, el sistema de control de aspersores estará listo para funcionar.

## Información Adicional
- **Inicio automático (Autologin):** El sistema está configurado para que la tablet inicie sesión automáticamente como administrador (root).
- **Configuración del sistema:** El instalador descarga la última versión del sistema desde GitHub y ajusta todos los componentes necesarios.
- **Herramientas adicionales:** Durante la instalación se agregarán programas como `htop`, `nodm`, `curl`, y `jq` para mejorar el rendimiento de la tablet.
- **Personalización del arranque:** Se ajusta la configuración del sistema para ocultar mensajes técnicos durante el encendido y se añade una imagen personalizada.

---

# DVM - Compilación del Proyecto

## Requisitos Previos
Antes de comenzar, asegúrate de contar con lo siguiente:

- Python 3.9 o superior instalado en tu sistema.
- Controlador CAN Bus instalado y funcionando correctamente en el sistema.
- Dependencias necesarias que se instalan ejecutando este comando en la terminal:
  ```bash
  pip install -r requirements.txt
  ```

## Compilación del Proyecto
Este proyecto es un script de Python, por lo que no requiere un proceso de compilación tradicional. Sin embargo, asegúrate de que:

- Todas las dependencias estén instaladas correctamente.
- El hardware CAN Bus y su controlador estén configurados y funcionando.

### Configuración de CAN Bus
Para activar la interfaz CAN Bus en Linux, ejecuta los siguientes comandos en la terminal:
```bash
sudo ip link set can0 up type can bitrate 500000
sudo ifconfig can0 up
```
Estos comandos configurarán la interfaz `can0` con la tasa de bits adecuada.

---

# Levantar un Ambiente de Desarrollo

## Requisitos del Sistema
- **Controlador CAN Bus:** Asegúrate de tener un controlador CAN Bus compatible instalado en tu sistema.
- **Hardware compatible con CAN Bus** para realizar la comunicación.

## Configuración del Entorno

1. **Clonar el repositorio del proyecto:**  
   Abre una terminal y ejecuta:
   ```bash
   git clone https://github.com/usuario/proyecto_canbus.git
   cd proyecto_canbus
   ```

2. **Instalar las dependencias:**  
   Una vez dentro del directorio del proyecto, instala las dependencias con:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar la interfaz CAN Bus:**  
   Para activar la interfaz `can0`, asegúrate de que el controlador y el hardware estén listos y luego ejecuta los mismos comandos que en la sección de "Configuración de CAN Bus".

## Ejecutar el Proyecto en Desarrollo
Para iniciar el proyecto en el entorno de desarrollo, ejecuta el script principal con el siguiente comando:
```bash
python main.py
```

# Documentación de la API

## POST /testing

Envía un comando de prueba a los nodos especificados.

- **URL**: `/testing`  
- **Método**: `POST`  
- **Content-Type**: `application/json`  
- **Cuerpo de la petición**:
    ```json
    {
      "nodos": [1030, 1230, 1150]
    }
    ```

- **Respuesta exitosa (200)**:
    ```json
    {
      "status": "ok"
    }
    ```

---

## POST /normal

Envía valores de RPM para operación normal a los nodos.

- **URL**: `/normal`  
- **Método**: `POST`  
- **Content-Type**: `application/json`  
- **Cuerpo de la petición**:
    ```json
    {
      "nodos": [
        { "nodo": 1030, "rpm1": 2000, "rpm2": 0, "rpm3": 1500, "rpm4": 0 },
        { "nodo": 1230, "rpm1": 0,    "rpm2": 0, "rpm3": 0,    "rpm4": 0 }
      ]
    }
    ```

- **Respuesta exitosa (200)**:
    ```json
    {
      "status": "ok"
    }
    ```

---

## POST /setConfiguracion

Envía parámetros de configuración a los nodos.

- **URL**: `/setConfiguracion`  
- **Método**: `POST`  
- **Content-Type**: `application/json`  
- **Cuerpo de la petición**:
    ```json
    {
      "configuraciones": [
        {
          "nodo": 1030,
          "variacionRPM": 50,
          "subcorriente": 1.5,
          "sobrecorriente": 2.0,
          "cortocicuito": 0.5,
          "sensor": 1,
          "electrovalvula": 0
        }
      ]
    }
    ```

- **Respuesta exitosa (200)**:
    ```json
    {
      "status": "ok"
    }
    ```

---

## GET /scan

Escanea el bus CAN para detectar placas conectadas.

- **URL**: `/scan`  
- **Método**: `GET`  
- **Parámetros**: ninguno  

- **Respuesta exitosa (200)**:
    ```json
    {
      "nodos": [1030, 1230, 1150]
    }
    ```

---

## POST /renombrar

Renombra un nodo asignándole un nuevo ID.

- **URL**: `/renombrar`  
- **Método**: `POST`  
- **Content-Type**: `application/json`  
- **Cuerpo de la petición**:
    ```json
    {
      "nodo": 1030,
      "nodoNombreNuevo": 2030
    }
    ```

- **Respuestas**:
  - **200 OK**  
      ```json
      { "status": "ok" }
      ```
  - **400 Bad Request** (falta algún campo):  
      ```json
      { "error": "Falta 'nodo' o 'nodoNombreNuevo'" }
      ```

---

## POST /restablecerFabrica

Restablece un nodo a su configuración de fábrica.

- **URL**: `/restablecerFabrica`  
- **Método**: `POST`  
- **Content-Type**: `application/json`  
- **Cuerpo de la petición**:
    ```json
    {
      "nodo": 1030
    }
    ```

- **Respuestas**:
  - **200 OK**  
      ```json
      { "status": "ok" }
      ```
  - **400 Bad Request** (falta `nodo`):  
      ```json
      { "error": "Falta 'nodo'" }
      ```

---

## GET /version

Obtiene la versión de la API y la versión de las placas.

- **URL**: `/version`  
- **Método**: `GET`  
- **Parámetros**: ninguno  

- **Respuesta exitosa (200)**:
    ```json
    {
      "version": "1.2.0",
      "boardVersion": "2.1"
    }
    ```

---

## GET /datosMeteorologicos

Devuelve los datos meteorológicos actuales (sin el campo `command`).

- **URL**: `/datosMeteorologicos`  
- **Método**: `GET`  
- **Parámetros**: ninguno  

- **Respuesta exitosa (200)**:
    ```json
    {
      "humedad": 45.2,
      "velViento": 3.1,
      "dirViento": 180.0,
      "temperatura": 22.5,
      "puntoDeRocio": 10.3,
      "presionAtmosferica": 1013.2,
      "version": 1,
      "gpsInfo": {
        "nroSatelites": 5,
        "velocicidad": 0.0,
        "latitud": 0.0,
        "longitud": 0.0,
        "altura": 0.0
      },
      "caudalInfo": {
        "boards": [
          { "board_id": 1030, "caudalEngine0": 0.0, "caudalEngine1": 0.0, "caudalEngine2": 0.0, "caudalEngine3": 0.0 }
        ]
      }
    }
    ```

---

## GET /estadoGeneralNodos

Devuelve el estado general de todos los nodos (sin el campo `command`).

- **URL**: `/estadoGeneralNodos`  
- **Método**: `GET`  
- **Parámetros**: ninguno  

- **Respuesta exitosa (200)**:
    ```json
    {
      "nodos": [
        {
          "nodo": 1030,
          "state1": 3.1,
          "state2": 3.2,
          "state3": 3.3,
          "state4": 6.2,
          "corr1": 2000,
          "corr2": 2500,
          "corr3": 2000,
          "corr4": 500,
          "rpm1": 2000,
          "rpm2": 2500,
          "rpm3": 1000,
          "rpm4": 0,
          "voltaje": 12.8
        }
      ]
    }
    ```
