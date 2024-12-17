#!/usr/bin/python3

import os
# Configurar la variable de entorno para que no aparezcan mensajes de error de index de camara
os.environ["OPENCV_LOG_LEVEL"] = "FATAL"

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.font import Font
from tkinter import filedialog
from PIL import Image, ImageTk, Image, ImageDraw, ImageFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL.ImageTk import PhotoImage
import cv2, sys, platform

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)
from codigo.image_processor_top import ImageProcessor_Top
from codigo.image_processor_front import ImageProcessor_Front
from codigo.cube_tracker import CubeTracker
from codigo.camera_controller import CameraController
from codigo.generacion_figura import FigureGenerator
from geometry2D import Geometry2D
from copy import deepcopy

class VisionTab:
    def __init__(self,) -> None:
        # --- ROOT ---
        self.root = ttk.Window(title="", themename="custom-vision")
        self.root.resizable(True, True)  # Permitir redimensionar la ventana
        self.system = platform.system()

        if self.system == "Linux":
            # Para Linux, se usa -zoomed para maximizar
            self.root.attributes('-zoomed', True)
        elif self.system == "Windows":
            # Para Windows, se usa state('zoomed') para maximizar
            self.root.state('zoomed')

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        #Definicion imagenes y varibles
        self.img_front = None
        self.img_plant = None
        self.img_mesa_trabajo = None
        self.file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', "/")
        
        # Definición de clases
        self.ImageProcessorFrontal = ImageProcessor_Front()
        self.ImageProcessorPlanta = ImageProcessor_Top()
        self.CubeLocalizator = CubeTracker(f"{self.file_path}/data/camera_data/ost.yaml")
        self.Geometry3D = FigureGenerator()
        self.Geometry2D = Geometry2D()
        self.camera_controller = CameraController(10)
        
        # Definición de Objetos ttk
        self.camera_entry1 = None
        self.camera_entry2 = None
        
        self.F_inputs = []
        self.F_images = []
        self.imgs = [None, None, None]
        self.CB_entries = []
        self.label_text = ["ALZADO", "PERFIL", "PLANTA"] 
        self.L_imgs = []
        self.F_input_1 = None
        self.F_input_2 = None
        self.camera_feed_job_3 = None

        #Definicion geometria
        self.cube_data = []
        
        #Definicion estados del boton
        self.state_procesar = True
        self.state_procesar_xy = True
        
        
        self.estilo()
        self.vision_tab()
        self.root.mainloop()
    
    
    def vision_tab(self):
        self.frame_vision = ttk.Frame(self.root)
        self.frame_vision.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        self.frame_vision.grid_rowconfigure(0, weight=1)
        self.frame_vision.grid_rowconfigure(1, minsize=self.screen_height*0.82)
        self.frame_vision.grid_columnconfigure(0, weight=1)
        self.frame_vision.grid_columnconfigure(1, minsize=self.screen_width*0.5)

        self._fila_0_col_0()
        self._fila_0_col_1()
        self._fila_1_col_0()
        self._fila_1_col_1()

        self.toggle_3d_mode()
        self.toggle_ws_mode()


    def _fila_0_col_0(self):

        # --- FRAME: Primera fila ---
        self.F_primera_fila = ttk.Frame(self.frame_vision)
        self.F_primera_fila.grid(row=0, column=0, sticky="nsew",padx=10, pady=5)
        self.F_primera_fila.grid_rowconfigure(0, weight=1)
        self.F_primera_fila.grid_columnconfigure(0, weight=1)

        self.LF_primera_col = ttk.LabelFrame(self.F_primera_fila, text="  Modo Funcionamiento  ")
        self.LF_primera_col.grid(row=0, column=0, sticky="nsew", padx=[0,0], pady=0)
        self.LF_primera_col.grid_rowconfigure(0, weight=1)
        self.LF_primera_col.grid_columnconfigure(0, weight=1)


        self.F_primera_col = ttk.Frame(self.LF_primera_col)
        self.F_primera_col.grid(row=0, column=0, sticky="nsew",padx=10, pady=10)
        self.F_primera_col.grid_rowconfigure(0, weight=1)
        self.F_primera_col.grid_columnconfigure(0, weight=2)
        self.F_primera_col.grid_columnconfigure(1, weight=1)
        self.F_primera_col.grid_columnconfigure(2, weight=2)

        # --- ELEMENTS ---
        # Text MANUAL
        self.L_camOFF = ttk.Label(self.F_primera_col, text="CAMARA OFF" )
        self.L_camOFF.grid(row=0, column=0, sticky="e", padx=[0, 10])

            # Checkbutton
        self.V_modo_3d_cam = ttk.IntVar()  # Variable para el estado del Checkbutton
        self.CB_modo = ttk.Checkbutton(
            self.F_primera_col,
            variable=self.V_modo_3d_cam,
            command=self.toggle_3d_mode,
            bootstyle="primary-round-toggle")
        self.CB_modo.grid(row=0, column=1)

        # Text MANUAL
        self.L_camON = ttk.Label(self.F_primera_col, text="CAMARA ON" )
        self.L_camON.grid(row=0, column=2, sticky="w", padx=[10, 0])

    
    def _fila_0_col_1(self):

        # --- FRAME: Primera fila ---
        self.F_primera_fila = ttk.Frame(self.frame_vision)
        self.F_primera_fila.grid(row=0, column=1, sticky="nsew",padx=10, pady=5)
        self.F_primera_fila.grid_rowconfigure(0, weight=1)
        self.F_primera_fila.grid_columnconfigure(0, weight=1)

        # --- SEGUNDA COLUMNA ---
        self.LF_segunda_col = ttk.LabelFrame(self.F_primera_fila, text="  Control de las Cámaras  ")
        self.LF_segunda_col.grid(row=0, column=0, sticky="nsew", padx=[0,0], pady=0)
        self.LF_segunda_col.grid_rowconfigure(0, weight=1)
        self.LF_segunda_col.grid_columnconfigure(0, weight=1)


        self.F_segunda_col= ttk.Frame(self.LF_segunda_col)
        self.F_segunda_col.grid(row=0, column=0, sticky="nsew",padx=0, pady=0)
        self.F_segunda_col.grid_rowconfigure(0, weight=1)
        self.F_segunda_col.grid_columnconfigure(0, weight=1)
        
        self.B_ActualizarCam = ttk.Button(self.F_segunda_col, 
                                 text="ACTUALIZAR CAMARAS",
                                 bootstyle="warning",
                                 command=self.update_cameras)
        self.B_ActualizarCam.grid(row=0, column=0, sticky="nsew",padx=10, pady=10)
         

    def _fila_1_col_0(self):
        # --- FRAME ---
        # Label Frame
        self.LF_segunda_fila = ttk.LabelFrame(self.frame_vision, text="  Generación de la Figura  ")
        self.LF_segunda_fila.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.LF_segunda_fila.grid_rowconfigure(0, weight=1)
        self.LF_segunda_fila.grid_rowconfigure(1, minsize=self.frame_vision.winfo_height()*0.20)
        self.LF_segunda_fila.grid_columnconfigure(0, weight=1)

        # --- INNER FRAME: Fila 1 ---
        self.F_10_0 = ttk.Frame(self.LF_segunda_fila)
        self.F_10_0.grid(row=0, column=0, sticky="nsew",padx=10, pady=10)
        self.F_10_0.grid_rowconfigure(0, weight=1)
        self.F_10_0.grid_rowconfigure(1, weight=1)
        self.F_10_0.grid_columnconfigure(0, weight=1)
        self.F_10_0.grid_columnconfigure(1, weight=1)

        # --- ELEMENTS ---
        # Image Frame 1

        for i in range(3):
            row = 0 if i < 2 else 1
            col = i if i < 2 else 0
            
            self.F_images.append(ttk.Frame(self.F_10_0))
            self.F_images[i].grid_rowconfigure(0, weight=1)
            self.F_images[i].grid_rowconfigure(1, weight=1)
            self.F_images[i].grid_rowconfigure(2, weight=1)
            self.F_images[i].grid_columnconfigure(0, weight=1)
            self.F_images[i].grid(row=row, column=col, pady=10, padx=10, sticky="nsew")

            ttk.Label(self.F_images[i],
                      text=self.label_text[i], 
                      font=("Montserrat SemiBold", 10), 
                      foreground="#000000").grid(row=0, column=0, pady=[0,5],sticky="N")
        
            self.L_imgs.append(ttk.Label(self.F_images[i]))
            self.L_imgs[i].grid(row=1, column=0, sticky="N")
            
            self.F_inputs.append(ttk.Frame(self.F_images[i], width=self.F_10_0.winfo_width()*0.5))
            self.F_inputs[i].grid(row=2, column=0)
        
        
        # Figure Frame
        self.F_figure_3D = ttk.Frame(self.F_10_0)
        self.F_figure_3D.grid_rowconfigure(0, weight=1)
        self.F_figure_3D.grid_rowconfigure(1, weight=1)
        self.F_figure_3D.grid_columnconfigure(0, weight=1)
        self.F_figure_3D.grid(row=1, column=1, pady=10, padx=10, sticky="nsew")
        
        ttk.Label(self.F_figure_3D,text="FIGURA 3D", 
                  font=("Montserrat SemiBold", 10),
                  foreground="#000000").grid(row=0, column=0, pady=[0,5],sticky="N")
        

        fig_3d = self.Geometry3D.generate_figure_from_matrix(np.full((5,5),-1), 
                                                             np.full((5,5),-1), 
                                                             paint=True,
                                                             tkinter=True)
        self.canvas_3d = FigureCanvasTkAgg(fig_3d, self.F_figure_3D)
        self.canvas_3d.get_tk_widget().grid(row=1, column=0, pady=20, padx=10, sticky="nsew")
        
        # --- INNER FRAME: Fila 2 ---
        self.F_10_1 = ttk.Frame(self.LF_segunda_fila)
        self.F_10_1.grid(row=1, column=0, sticky="nsew",padx=10, pady=10)
        self.F_10_1.grid_rowconfigure(0, weight=1)
        self.F_10_1.grid_columnconfigure(0, weight=1)
        self.F_10_1.grid_columnconfigure(1, weight=1)
        self.process_button = ttk.Button(
            self.F_10_1,
            text="PROCESAR",
            command=self.process_images,  # Función para procesar las imágenes
            bootstyle="secondary",  # Estilo del botón
        )
        self.process_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.clear_button = ttk.Button(
            self.F_10_1,
            text="BORRAR",
            state = ttk.DISABLED,
            command=self.clear_3D_images,  # Función para procesar las imágenes
            bootstyle="danger-outline",  # Estilo del botón
        )
        self.clear_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def _fila_1_col_1(self):
        # --- GLOBAL FRAME ---
        self.F_11 = ttk.Frame(self.frame_vision)
        self.F_11.grid(row=1, column=1, sticky="nsew", padx=0, pady=5)
        self.F_11.grid_columnconfigure(0, weight=1)
        self.F_11.grid_rowconfigure(0, minsize=self.frame_vision.winfo_height()*0.60)
        self.F_11.grid_rowconfigure(1, weight=1)
        
        # Label Frame
        self.LF_11 = ttk.LabelFrame(self.F_11, text="  Mesa de Trabajo  ")
        self.LF_11.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.LF_11.grid_columnconfigure(0, weight=1)
        self.LF_11.grid_rowconfigure(0, weight=1)
        
        # Inner Frame
        self.F_11_1 = ttk.Frame(self.LF_11)
        self.F_11_1.grid_rowconfigure(0, minsize=self.LF_11.winfo_height()*0.40)
        self.F_11_1.grid_rowconfigure(1, weight=1)
        self.F_11_1.grid_rowconfigure(2, minsize=self.LF_11.winfo_height()*0.20)
        self.F_11_1.grid_columnconfigure(0, weight=1)
        self.F_11_1.grid(row=0, column=0, sticky="nsew",padx=10, pady=10)


        # --- INNER FRAME: Fila 1 ---
        self.V_modo_ws = ttk.IntVar(value=1)  # Variable para el estado del Checkbutton
        self.CB_modo_ws = ttk.Checkbutton(
            self.F_11_1,
            text="CAMARA ACTIVADA",
            variable=self.V_modo_ws,
            command=self.toggle_ws_mode,
            bootstyle="success-outline-toolbutton")
        self.CB_modo_ws.grid(row=0, column=0, sticky="nsew", padx=10)
        
        # --- INNER FRAME: Fila 2 ---
        self.F_11_1_1 = ttk.Frame(self.F_11_1)
        self.F_11_1_1.grid(row=1, column=0, pady=20, sticky="nsew")
        self.F_11_1_1.grid_rowconfigure(0, weight=1)
        self.F_11_1_1.grid_columnconfigure(0, weight=1)
        self.F_11_1_1.grid_columnconfigure(1, weight=1)
        
        # Imagen WS
        self.F_img_ws = ttk.Frame(self.F_11_1_1)
        self.F_img_ws.grid(row=0, column=0, sticky="nsew")
        self.F_img_ws.grid_rowconfigure(0, weight=1)
        self.F_img_ws.grid_rowconfigure(1, weight=1)
        self.F_img_ws.grid_rowconfigure(2, weight=1)
        self.F_img_ws.grid_columnconfigure(0, weight=1)
        
        ttk.Label(self.F_img_ws,
                  text="CÁMARA SUPERIOR", 
                  font=("Montserrat SemiBold", 10), 
                  foreground="#000000").grid(row=0, column=0, pady=[0,5],sticky="ns")
        
        self.L_img_ws = ttk.Label(self.F_img_ws)
        self.L_img_ws.grid(row=1, column=0)
        
        self.F_input_ws = ttk.Frame(self.F_img_ws)
        self.F_input_ws.grid(row=2, column=0, sticky="nsew")
        
        # --- FRAME ---
        self.F_figure_ws = ttk.Frame(self.F_11_1_1)
        self.F_figure_ws.grid(row=0, column=1, sticky="nsew")
        self.F_figure_ws.grid_rowconfigure(0, weight=1)
        self.F_figure_ws.grid_rowconfigure(1, weight=1)
        self.F_figure_ws.grid_rowconfigure(2, weight=1)
        self.F_figure_ws.grid_columnconfigure(0, weight=1)
        
        ttk.Label(self.F_figure_ws,
                  text="REPRESENTACIÓN 2D", 
                  font=("Montserrat SemiBold", 10), 
                  foreground="#000000").grid(row=0, column=0, pady=[0,5],sticky="ns")
        

        # --- ELEMENTS ---
        fig_2d = self.Geometry2D.draw_2d_space([], True, (4, 3.5))
        self.canvas_2d = FigureCanvasTkAgg(fig_2d, self.F_figure_ws)
        self.canvas_2d.get_tk_widget().grid(row=0, column=0, pady=20, padx=10, sticky="nsew")
        
        
        # --- INNER FRAME: Fila 3 ---
        self.F_ws_col_12 = ttk.Frame(self.LF_11)
        self.F_ws_col_12.grid(row=1, column=0, sticky="nsew",padx=10, pady=10)
        self.F_ws_col_12.grid_rowconfigure(0, weight=1)
        self.F_ws_col_12.grid_columnconfigure(0, weight=1)
        self.F_ws_col_12.grid_columnconfigure(1, weight=1)
        self.process_button = ttk.Button(
            self.F_ws_col_12,
            text="PROCESAR",
            command=self.xy_process_images,  # Función para procesar las imágenes
            bootstyle="secondary",  # Estilo del botón
        )
        self.process_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.clear_button = ttk.Button(
            self.F_ws_col_12,
            text="BORRAR",
            state = ttk.DISABLED,
            command=self.xy_clear_images,  # Función para procesar las imágenes
            bootstyle="danger-outline",  # Estilo del botón
        )
        self.clear_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.LF_terminal = ttk.LabelFrame(self.F_11, text="  Terminal  ")
        self.LF_terminal.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.LF_terminal.grid_rowconfigure(0, weight=1)
        self.LF_terminal.grid_columnconfigure(0, weight=1)



        self.F_terminal = ttk.Frame(self.LF_terminal)
        self.F_terminal.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        self.F_terminal.grid_rowconfigure(0, weight=1)
        self.F_terminal.grid_columnconfigure(0, weight=1)

        self.terminal = ttk.ScrolledText(self.F_terminal, 
                                    wrap=ttk.WORD, 
                                    font=("Courier", 12),
                                    height=1,
                                    state=ttk.NORMAL)
        self.terminal.configure(
            bg="#1e1e1e",  # Fondo negro
            fg="white",  # Texto blanco
            insertbackground="white",  # Cursor blanco
        )
        self.terminal.vbar.pack_forget() 
        #self.terminal.config(yscrollcommand=self.terminal_scroll.set)
        self.terminal.grid(row=0, column=0, sticky="nsew")
        self.terminal.tag_configure("ERROR", foreground="red")  # Estilo para errores
        self.terminal.tag_configure("WARN", foreground="yellow")  # Estilo para advertencias
        self.terminal.tag_configure("INFO", foreground="green")
        self.terminal.insert(ttk.END, f"Mensaje 1\n", "ERROR")
        self.terminal.insert(ttk.END, f"Mensaje 1\n")
        self.terminal.insert(ttk.END, f"Mensaje 1\n")
        self.terminal.insert(ttk.END, f"Mensaje 1\n")
        self.terminal.insert(ttk.END, f"Mensaje 1\n")
        self.terminal.insert(ttk.END, f"Mensaje 1\n")
        self.terminal.insert(ttk.END, f"Mensaje 1\n")


    def toggle_3d_mode(self):
        """Maneja el cambio de estado del Checkbutton"""
        # Limpia filas específicas para evitar superposiciones
        for i in range(3):
            if self.F_inputs[i] is not None:
                self.F_inputs[i].destroy()
        self.F_inputs = []

        if self.V_modo_3d_cam.get() == 1:
            self.L_camOFF.config(font=("Montserrat", 10), foreground="#474B4E")
            self.L_camON.config(font=("Montserrat", 10, "bold"), foreground="#5eaae8")
            self.camera_3D_inputs()

        else:
            self.L_camOFF.config(font=("Montserrat", 10, "bold"), foreground="#5eaae8")
            self.L_camON.config(font=("Montserrat", 10), foreground="#474B4E")
            self.file_3D_inputs()
    
    def toggle_ws_mode(self):
        """Maneja el cambio de estado del Checkbutton del Frame 2D"""
        # Destruir el frame y vover a crearlo
        if self.F_input_ws is not None:
            self.F_input_ws.destroy()
            self.F_input_ws = ttk.Frame(self.F_img_ws)
            self.F_input_ws.grid(row=2, column=0, sticky="nsew")
            
        if self.V_modo_ws.get() == 1:
            self.CB_modo_ws.config(text="CAMARA ACTIVA")
            self.CB_modo_ws.config(bootstyle="success-outline-toolbutton")
            self.camera_ws_inputs()

        else:
            self.CB_modo_ws.config(text="CAMARA DESACTIVADA")
            self.CB_modo_ws.config(bootstyle="danger-outline-toolbutton")
            self.file_ws_inputs()
            

    def camera_ws_inputs(self):
        """Elimina los campos de entrada y botones para cargar imágenes"""
            
        # Configurar el frame
        self.F_input_ws.grid_rowconfigure(0, weight=1)
        self.F_input_ws.grid_columnconfigure(0, weight=1)
        
        self.CB_cam_ws = ttk.Combobox(self.F_input_ws, 
                                        values=self.camera_controller.camera_names,
                                        font=("Montserrat", 10))
        self.CB_cam_ws.grid(row=0, column=0, sticky="nsew", padx=10, pady=[10,0])
        
        if len(self.camera_controller.cameras) > 0:
            self.CB_cam_ws.set(self.camera_controller.camera_names[0])
            
        self.update_camera_ws()
            
    def file_ws_inputs(self):
        """Elimina los campos de entrada y botones para cargar imágenes"""
        
        # Configurar el frame
        self.F_input_ws.grid_rowconfigure(0, weight=1)
        self.F_input_ws.grid_columnconfigure(0, weight=1)
        self.F_input_ws.grid_columnconfigure(1, weight=1)  
          

        self.E_input_3 = ttk.Entry(self.F_input_ws, width=25, font=("Montserrat", 10), bootstyle="dark")
        self.E_input_3.grid(row=0, column=0, padx=10, pady=[10,0], sticky="nsew")
        self.E_input_3.delete(0, END)
        self.E_input_3.configure(foreground="#5a5a5a")
        self.E_input_3.state([ttk.DISABLED])

        self.B_browse_3 = ttk.Button(
            self.F_input_ws,
            text="Buscar...",
            command=lambda: self.load_save_frame("img_ws", self.E_input_3, self.L_img_ws, 0.65))
        self.B_browse_3.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self._update_2D_file_images()
    
    def camera_3D_inputs(self):
        """Elimina los campos de entrada y botones para cargar imágenes"""
        self.CB_entries = []
        for i in range(3):
            self.F_inputs.append(ttk.Frame(self.F_images[i], width=self.F_10_0.winfo_width()*0.5))
            self.F_inputs[i].grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
            self.F_inputs[i].grid_columnconfigure(0, weight=1)
            self.F_inputs[i].grid_rowconfigure(0, weight=1)
            
            self.CB_entries.append(ttk.Combobox(self.F_inputs[i],
                                              values=self.camera_controller.camera_names,
                                              font=("Montserrat", 10),
                                              width=33))
            self.CB_entries[i].grid(row=0, column=0, padx=0, pady=0,sticky="nsew")
            if len(self.camera_controller.cameras) > i:
                self.camera_entry1.set(self.camera_controller.camera_names[i])
        
        self.update_camera_3D()
        
    def file_3D_inputs(self):
        """Crea los campos de entrada y botones para cargar imágenes"""
        self.E_inputs = []
        self.B_browsers = []
        for i in range(3):
            self.F_inputs.append(ttk.Frame(self.F_images[i], width=self.F_10_0.winfo_width()*0.5))
            self.F_inputs[i].grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
            self.F_inputs[i].grid_columnconfigure(0, weight=1)
            self.F_inputs[i].grid_columnconfigure(1, weight=1)
            self.F_inputs[i].grid_rowconfigure(0, weight=1)
            
            self.E_inputs.append(ttk.Entry(self.F_inputs[i], width=25, font=("Montserrat", 10), bootstyle="dark"))
            self.E_inputs[i].grid(row=0, column=0, padx=[0,10], sticky="nsew")
            self.E_inputs[i].delete(0, END)
            self.E_inputs[i].configure(foreground="#5a5a5a")
            self.E_inputs[i].state([ttk.DISABLED])
            
            self.B_browsers.append(ttk.Button(self.F_inputs[i],
                                              text="Buscar...",
                                              command=lambda: self.load_save_frame(i, self.E_inputs[i], self.L_imgs[i])))
            self.B_browsers[i].grid(row=0, column=1, sticky="nsew")

        self._update_3D_file_images()
        

    def _update_camera(self, camera_index, aspect_ratio:float=0.6):
        frame = self.camera_controller.get_frame(camera_index)

        if frame is not None:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img = self._resize_image(img, aspect_ratio)
            imgtk = ImageTk.PhotoImage(image=img)
        else:
            imgtk = self._create_image_with_text("Cámara NO encontrada", aspect_ratio)
        
        return imgtk, frame
    
    def update_camera_3D(self):
        if self.V_modo_3d_cam.get() == 1:
            if self.state_procesar:
                for i in range(3):
                    if self.CB_entries[i].get() != '':
                        index = self.camera_controller.camera_names.index(self.CB_entries[i].get())
                        imgtk, frame = self._update_camera(index)
                    else:
                        imgtk = self._create_image_with_text("Cámara NO encontrada")
                        frame = None

                    self.imgs[i] = deepcopy(frame)
                    self.L_imgs[i].config(image=imgtk)
                    self.L_imgs[i].image = imgtk

                for i in range(3):
                    self.L_imgs[i].update()

                # Actualizar el hilo
                self.root.after(10, self.update_camera_3D)
    

    def update_camera_ws(self):
        """Actualiza el feed de la cámara y lo muestra en el Label."""
        if self.V_modo_ws.get() == 1:
            if self.state_procesar_xy:
                if self.CB_cam_ws.get() != '':
                    index = self.camera_controller.camera_names.index(self.CB_cam_ws.get())
                    imgtk, frame = self._update_camera(index, 0.65)

                else:
                    imgtk = self._create_image_with_text("Cámara NO encontrada", 0.65)
                    frame = None

                self.img_ws = frame
                self.L_img_ws.config(image=imgtk)
                self.L_img_ws.image = imgtk
                self.L_img_ws.update()
                
                self.camera_feed_job_3 = self.root.after(12, self.update_camera_ws)
            else:
                if self.camera_feed_job_3 is not None:
                    self.root.after_cancel(self.camera_feed_job_3)
                    self.camera_feed_job_3 = None
        else:
            if self.camera_feed_job_3 is not None:
                self.root.after_cancel(self.camera_feed_job_3)
                self.camera_feed_job_3 = None
            
    def load_save_frame(self, img_index, entry:ttk.Entry, label:ttk.Label, aspect_ratio:float=0.6):
        loaded_image = self._load_file(entry, label, aspect_ratio)
        self.imgs[img_index] = deepcopy(loaded_image)

    def _load_file(self, entry:ttk.Entry, label:ttk.Label, aspect_ratio:float=0.6):
        """Permite seleccionar un archivo y actualizar la imagen correspondiente"""
        file_path = filedialog.askopenfilename(
            initialdir=f"{self.file_path}/data",
            filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.bmp *.gif"),
                       ("Todos los archivos", "*.*")])
        if file_path:
            try:
                directorio_padre = os.path.dirname(file_path)
                nombre_archivo = os.path.basename(file_path)
                ultimo_directorio = os.path.basename(directorio_padre)

                entry.state(["!disabled"])
                entry.delete(0, END)
                entry.insert(0, f".../{ultimo_directorio}/{nombre_archivo}")
                entry.state([ttk.DISABLED])

                # Actualizar la imagen
                frame = cv2.imread(file_path)
                image = self._resize_image(Image.open(file_path), aspect_ratio)

                # Crear objeto PhotoImage y actualizar la etiqueta con la nueva imagen
                photo = ImageTk.PhotoImage(image)
                label.config(image=photo)
                label.image = photo

            except Exception as e:
                print(f"Error al cargar la imagen: {e}")
        
            return frame
        
        return self._create_image_with_text("CARGAR IMAGEN", aspect_ratio)

    def xy_process_images(self):
        if self.img_ws is not None:
            self.xy_process_button.state([ttk.DISABLED])
            self.xy_clear_button.state(["!disabled"])
            self.state_procesar_xy = False
            self.update_camera_ws()
            

            img_ws_processed, coordenadas = self.CubeLocalizator.process_image(self.img_ws, area_size=1000)

            #Resize
            img_ws_processed = Image.fromarray(cv2.cvtColor(img_ws_processed, cv2.COLOR_BGR2RGB))
            photo1 = self._resize_image(img_ws_processed, 0.65)

            photo1 = ImageTk.PhotoImage(photo1)
            self.L_img_ws.config(image=photo1)
            self.L_img_ws.image = photo1

            # Actualizar canvas_3d
            if hasattr(self, "canvas_2d"):
                self.canvas_2d.get_tk_widget().destroy()

            fig_2d = self.Geometry2D.draw_2d_space(coordenadas, True, (10, 3.5))
            self.canvas_2d = FigureCanvasTkAgg(fig_2d, self.LF_2d_fila)
            self.canvas_2d.get_tk_widget().grid(row=0, column=0, pady=20, padx=10, sticky="nsew")
    
    def _expand_corners(self, corners, factor=1.2):
        """
        Expande las esquinas del marcador ArUco aumentando su tamaño.
        :param corners: Esquinas de los marcadores detectados (forma de (1, 4, 2)).
        :param factor: Factor de escala para aumentar o reducir el tamaño del marcador.
        :return: Nuevas coordenadas de las esquinas ajustadas.
        """
        expanded_corners = []

        for corner in corners:
            # corner es un array de 4 puntos del marcador, por ejemplo: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            
            # Calcular el centro del marcador como el promedio de las 4 esquinas
            centro = np.mean(corner, axis=0)  # El centro es el promedio de los puntos

            # Crear una lista para las nuevas coordenadas ajustadas
            new_corners = []

            # Ajustar las esquinas en función del factor
            for point in corner:
                # Calcular el vector desde el centro hacia la esquina
                vector = point - centro
                # Ajustar el tamaño del vector con el factor
                new_point = centro + vector * factor  # Escalar el vector para aumentar el tamaño
                # Añadir el nuevo punto a la lista de esquinas ajustadas
                new_corners.append(new_point)

            # Convertir a tipo entero (por si acaso) y agregar el marcador ajustado a la lista final
            expanded_corners.append(np.array(new_corners, dtype=np.int32))

        return expanded_corners
    
    def process_images(self):
        """Procesa las imágenes y las muestra en los labels"""
        # Verifica que ambas imágenes estén cargadas
        if (self.imgs[0] is not None) and (self.imgs[1] is not None) and (self.imgs[2] is not None):
            self.state_procesar = False
            self.update_camera_3D()
            self.process_button.state([ttk.DISABLED])
            self.clear_button.state(["!disabled"])
            
            if self.V_modo_3d_cam != 1:
                for i in range(3):
                    self.B_browsers[i].state(["!disabled"])
            
            img_resultado = [None, None, None]        
            alzado_matrix, img_resultado[0] = self.ImageProcessorFrontal.process_image(self.imgs[0])          
            perfil_matrix, img_resultado[1] = self.ImageProcessorFrontal.process_image(self.imgs[1])
            planta_matrix, img_resultado[2] = self.ImageProcessorPlanta.process_image(self.imgs[2])

            #Resize
            for i in range(3):
                img = Image.fromarray(cv2.cvtColor(img_resultado[i], cv2.COLOR_BGR2RGB))
                photo1 = self._resize_image(img)
                photo1 = ImageTk.PhotoImage(photo1)
                self.L_imgs[i].config(image=photo1)
                self.L_imgs[i].image = photo1

            if hasattr(self, "canvas_3d"):
                self.canvas_3d.get_tk_widget().destroy()

            fig_3d = self.Geometry3D.generate_figure_from_matrix(plant_matrix, front_matrix, paint=True, tkinter=True)
            self.canvas_3d = FigureCanvasTkAgg(fig_3d, self.F_figure_3D)
            self.canvas_3d.get_tk_widget().grid(row=0, column=0, pady=20, padx=10, sticky="nsew")

    def _resize_image(self, img:Image.Image, aspect_ratio:float=0.6):
        img_size = (int(img.width * aspect_ratio), int(img.height * aspect_ratio))
        return img.resize(img_size)    
    
    def clear_3D_images(self):
        self.clear_button.state([ttk.DISABLED])
        self.img_front = deepcopy(None)
        self.img_plant = deepcopy(None)

        # --- VACIAR MATRIZ ---
        if hasattr(self, "canvas_3d"):
            self.canvas_3d.get_tk_widget().destroy()

        fig_3d = self.Geometry3D.generate_figure_from_matrix(np.full((5,5),-1), 
                                                             np.full((5,5),-1),
                                                             paint=True, 
                                                             tkinter=True)
        self.canvas_3d = FigureCanvasTkAgg(fig_3d, self.LF_3d_fila)
        self.canvas_3d.get_tk_widget().grid(row=0, column=0, pady=20, padx=10, sticky="nsew")
            
        self.process_button.state(["!disabled"])
        if self.V_modo_3d_cam == 1:
            self.B_browse_1.state(["!disabled"])
            self.B_browse_2.state(["!disabled"])
        self.state_procesar = True
        self.toggle_3d_mode()
    
    def xy_clear_images(self):
        self.xy_clear_button.state([ttk.DISABLED])
        self.xy_process_button.state(["!disabled"])
        self.state_procesar_xy = True

        # --- VACIAR MATRIZ ---
        if hasattr(self, "canvas_2d") and self.canvas_2d is not None:
            self.canvas_2d.get_tk_widget().destroy()

        fig_2d = self.Geometry2D.draw_2d_space([], True, (10, 3.5))

        self.canvas_2d = FigureCanvasTkAgg(fig_2d, self.LF_2d_fila)
        self.canvas_2d.get_tk_widget().pack(padx=0, pady=0)
        
        self.update_camera_ws()

    def update_cameras(self):
        self.camera_controller.stop()
        self.camera_controller.start(10)
        if self.camera_controller.camera_names != []:
            self.camera_entry1['values'] = self.camera_controller.camera_names
            self.camera_entry2['values'] = self.camera_controller.camera_names
            self.CB_cam_ws['values'] = self.camera_controller.camera_names
        self.update_camera_3D()
        self.update_camera_ws()
        
        
# Función para actualizar las imágenes en la interfaz
    def _update_3D_file_images(self):
        img = self._create_image_with_text("CARGAR IMAGEN")
        for i in range(3):
            self.L_imgs[i].config(image=img)
            self.L_imgs[i].image = img
    
    def _update_2D_file_images(self):
        img3 = self._create_image_with_text("CARGAR IMAGEN", 0.65)
        
        # Actualizar las etiquetas en la interfaz
        self.L_img_ws.config(image=img3)
        self.L_img_ws.image = img3



    def _create_image_with_text(self, text, aspect_ratio:float=0.6):

        img_size = (int(640 * aspect_ratio), int(480 * aspect_ratio))

        image = Image.new('RGB', img_size, color='black')
        
        # Crear un objeto para dibujar en la imagen
        draw = ImageDraw.Draw(image)
        
        # Establecer el texto y su color
        text_color = (255, 255, 255)  # Blanco
        
        # Intentar cargar una fuente del sistema o usar una por defecto
        if self.system == "Linux":
            path = f"{self.file_path}/proyecto-final-venv/include/Montserrat-Regular.ttf"
        elif self.system == "Windows":
            path  = f"{self.file_path}/proyecto-final-venv/Include/Montserrat-Regular.ttf"
        try:
            font = ImageFont.truetype(path, 20)  # Usa una fuente si está disponible
        except IOError:
            font = ImageFont.load_default()  # Si no se encuentra, usa la fuente predeterminada
        
        # Calcular el tamaño del texto y su posición para centrarlo
        text_bbox = draw.textbbox((0, 0), text, font=font)  # Obtiene las dimensiones del texto
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        position = ((img_size[0] - text_width) // 2, (img_size[1] - text_height) // 2)
        
        # Dibujar el texto en la imagen
        draw.text(position, text, font=font, fill=text_color)
        
        # Convertir la imagen a un formato compatible con tkinter
        tk_image = PhotoImage(image, master=self.root)
        
        return tk_image
    
    def estilo(self):
        style = ttk.Style()
        style.configure("Custom.TNotebook.Tab",
            font= ("Montserrat Medium", 12), 
            background= "white",
            )

        style.configure("Custom.TNotebook",
            background= "white",
            )

        style.configure("Custom.TFrame",
            font= ("Montserrat Medium", 12), 
            background= "white",
            borderwidth=0,  # Grosor del borde
            )

        style.map(
            "Custom.TNotebook.Tab",
            background=[("selected", "#8C85F7"), ("active", "#8C85F7"), ("!selected", "white")],     # Background color when hovered
            foreground=[("selected", "black"), ("active", "black"), ("!selected", "black")],   # Text color when hovered
        )

        style.configure("Vision.TNotebook.Tab",
            font= ("Montserrat Medium", 10), 
            background= "white",
            borderwidth=0,  # Grosor del borde
            )

        style.configure("Vision.TNotebook",
            background= "white",
            borderwidth=0
            )

        style.configure("Custom.TFrame",
            font= ("Montserrat Medium", 12), 
            background= "white",
            borderwidth=0,  # Grosor del borde
            )

        style.map(
            "Vision.TNotebook.Tab",
            background=[("selected", "#C5C1F7"), ("active", "#C5C1F7"), ("!selected", "white")],     # Background color when hovered
            foreground=[("selected", "black"), ("active", "black"), ("!selected", "black")],   # Text color when hovered
        )

        style.configure(
        "TCheckbutton",  # Nombre del estilo
        font=("Montserrat", 10),  # Fuente personalizada
        )

        style.configure(
        "TButton",  # Nombre del estilo
        font=("Montserrat", 10),  # Fuente personalizada
        )

        style.configure(
        "TLabelframe.Label",  # Nombre del estilo
            font=("Montserrat", 10),
        )
    
    def _on_closing(self):
        """Esta función se ejecuta cuando la ventana se cierra."""
        self.camera_controller.stop()
        
        # Cerrar la ventana de Tkinter
        self.root.destroy()
        exit()
            
if __name__ == "__main__":
    VisionTab()
