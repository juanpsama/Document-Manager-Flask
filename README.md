## Document Manager Flask

### Descripción
Una aplicación simple en Flask para gestionar documentos, usuarios, roles y etiquetas.

### Requisitos
- Python 3.8 o superior
- pip
- Virtualenv

### Instalación y Configuración
1. Clona el repositorio:
   ```bash
   git clone https://github.com/juanpsama/Document-Manager-Flask.git
   cd Document-Manager-Flask
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   # En Windows
   .\venv\Scripts\activate
   # En MacOS/Linux
   source venv/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura la base de datos:
   ```bash
   flask db upgrade
   ```

5. Ejecuta la aplicación:
   ```bash
   flask run --host=0.0.0.0  --debug
   ```

### Uso
Accede a la aplicación en tu navegador en `http://127.0.0.1:5000`.