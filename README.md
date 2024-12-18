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
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\proyecto-final-venv\Scripts\activate
```
#### 4. Instala las dependencias.
```bash
python.exe -m pip install --upgrade pip
pip install -r .\requirements\requirements.txt
```
#### 5. Mueve los archivos necesarios a las carpetas correspondientes.
Para estos dos pasos se necesita abrir el Power Shell en la carpeta correspondiente con permisos de administrador, ya que la carpeta de fuentes está protegida.
```bash
Expand-Archive -Path "requirements\montserrat.zip" -DestinationPath "C:\Windows\Fonts\"
```
```bash
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
pip install -r requirements/requirements.txt
```
#### 5. Mueve los archivos necesarios a las carpetas correspondientes.
Descomprimir y configurar las fuentes del Tkinter.
```bash
unzip requirements/montserrat.zip -d /usr/share/fonts/truetype/montserrat/
```
```bash
cp /usr/share/fonts/truetype/montserrat/static/Montserrat-Regular.ttf proyecto-final-venv/include/
```
Copiar el tema personalizado del Tkinter.
```bash
cp requirements/user.py proyecto-final-venv/lib/python$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)/site-packages/ttkbootstrap/themes/
```
#### 6. Desactiva el entorno virtual.
```bash
deactivate
```
