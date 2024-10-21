### DVM

#### Compilación del proyecto

1. **Requisitos previos:**
   - Python 3.9+
   - Controlador **canbus** instalado y funcional en el sistema.
   - Las siguientes dependencias se pueden instalar mediante `pip`:
     ```bash
     pip install -r requirements.txt
     ```

2. **Compilar el proyecto:**
   Este proyecto es un script de Python y no requiere un proceso de compilación en sí. Sin embargo, asegúrate de que todas las dependencias estén instaladas y que el hardware (controlador CAN Bus) esté correctamente configurado.

3. **Configuración de CAN Bus:**
   Para inicializar la interfaz **can0** en Linux, ejecuta los siguientes comandos:
   ```bash
   sudo ip link set can0 up type can bitrate 500000
   sudo ifconfig can0 up
   ```

#### Levantar un ambiente de desarrollo

1. **Requisitos del sistema:**
   - Controlador **CAN Bus**: Asegúrate de tener un controlador CAN Bus compatible instalado y configurado en tu sistema.
   - Hardware compatible con CAN Bus para la comunicación.

2. **Configuración del entorno:**
   - Clona el repositorio:
     ```bash
     git clone https://github.com/usuario/proyecto_canbus.git
     cd proyecto_canbus
     ```

   - Instala las dependencias:
     ```bash
     pip install -r requirements.txt
     ```

3. **Configuración de la interfaz CAN Bus:**
   - Para activar la interfaz **can0** en tu máquina, asegúrate de que el controlador y el hardware estén correctamente configurados y ejecuta los comandos para levantar la interfaz, como se describe en la sección de compilación.

4. **Ejecutar el proyecto en desarrollo:**
   Ejecuta el script principal:
   ```bash
   python main.py
   ```