
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
