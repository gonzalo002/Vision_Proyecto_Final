# Proyecto Final: Visión por Computador - MUCSI Grupo 2
En este repositorio se encuentran los ficheros necesarios para

## Instalación del entorno

### Windows

#### 1. Clona el repositorio.
Clona este repositorio en tu máquina local:
```bash
git clone https://github.com/gonzalo002/Vision_Proyecto_Final.git
```
```bash
./Vision_Proyecto_Final/
```

#### 2. Crea un entorno virtual.
```bash
python -m venv proyecto-final-venv
```
#### 3. Activa el entorno virtual.
```bash
.\proyecto-final-venv\Scripts\activate
```
#### 4. Instala las dependencias.
```bash
python.exe -m pip install --upgrade pip
pip install -r .\requeriments\requirements.txt
```
#### 5. Mueve los archivos necesarios a las carpetas correspondientes.
```bash
copy .\requirements\Montserrat-Regular.ttf .\proyecto-final-venv\Include\
Remove-Item .\proyecto-final-venv\Lib\site-packages\ttkbootstrap\themes\user.py
copy .\requirements\user.py .\proyecto-final-venv\Lib\site-packages\ttkbootstrap\themes\
```
#### 6. Desactiva el entorno virtual.
```bash
deactivate
```
### Ubuntu
#### 1. Clona el repositorio.
Clona este repositorio en tu máquina local:
```bash
git clone https://github.com/gonzalo002/Vision_Proyecto_Final.git
```
```bash
cd Vision_Proyecto_Final
```

#### 2. Crea un entorno virtual.
```bash
python -m venv proyecto-final-venv
```
#### 3. Activa el entorno virtual.
```bash
source proyecto-final-venv/bin/activate
```
#### 4. Instala las dependencias.
```bash
python -m pip install --upgrade pip
pip install -r requirements/requirements_ubuntu.txt
```
#### 5. Mueve los archivos necesarios a las carpetas correspondientes.
Descomprimir y configurar las fuentes del Tkinter.
```bash
unzip requiremets/montserrat.zip -d /usr/share/fonts/truetype/montserrat/
cp /usr/share/fonts/truetype/montserrat/static/Montserrat-Regular.ttf proyecto-final-venv/include/
# Configurar el tema de tkinter
cp requirements/user.py proyecto-final-venv/lib/python3.8/site-packages/ttkbootstrap/themes/
```
Copiar el tema personalizado del Tkinter.
Primero, ten en cuenta que tendrás que poner la versión correcta de Python que tengas instalada en la ruta del directorio.
```bash
python3 --version
```
```bash
cp requirements/user.py proyecto-final-venv/lib/python<version>/site-packages/ttkbootstrap/themes/
```
#### 6. Desactiva el entorno virtual.
```bash
deactivate
```
