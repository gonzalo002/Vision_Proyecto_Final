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
pip install -r requirements/requirements.txt
```
#### 5. Mueve los archivos necesarios a las carpetas correspondientes.
```powershell
move .\requirements\Montserrat-Regular.ttf .\proyecto-final-venv\Include\
move .\requirements\user.py .\proyecto-final-venv\Lib\site-packages\ttkbootstrap\themes\  
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
pip install -r requirements/requirements.txt
```
#### 5. Mueve los archivos necesarios a las carpetas correspondientes.
```powershell
move requirements/Montserrat-Regular.ttf proyecto-final-venv/Include
move requirements/user.py proyecto-final-venv/Lib/site-packages/ttkbootstrap/themes  
```
#### 6. Desactiva el entorno virtual.
```bash
deactivate
```
