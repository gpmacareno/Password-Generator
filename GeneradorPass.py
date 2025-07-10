import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import json
import string
import secrets
from cryptography.fernet import Fernet
import os

# ========================
# CONFIGURACIÓN DEL CIFRADO
# ========================

import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Carpeta segura
VAULT_DIR = os.path.join(BASE_DIR, 'vault')
os.makedirs(VAULT_DIR, exist_ok=True)

KEY_FILE = os.path.join(VAULT_DIR, 'clave.key')
MASTER_KEY_FILE = os.path.join(VAULT_DIR, "master.key")
DATA_FILE = os.path.join(VAULT_DIR, 'datos_seguros.json')

def generar_clave():
    clave = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as archivo:
        archivo.write(clave)

def cargar_clave():
    if not os.path.exists(KEY_FILE):
        generar_clave()
    with open(KEY_FILE, 'rb') as archivo:
        return archivo.read()

clave = cargar_clave()
fernet = Fernet(clave)

# ========================
# FUNCIONES PRINCIPALES
# ========================

def crear_contraseña_maestra():
    def guardar_contraseña():
        pwd = entry1.get()
        confirm = entry2.get()
        if not pwd or not confirm:
            messagebox.showwarning("Error", "No puede estar vacío.")
            return
        if pwd != confirm:
            messagebox.showwarning("Error", "Las contraseñas no coinciden.")
            return

        contraseña_cifrada = fernet.encrypt(pwd.encode())
        with open(MASTER_KEY_FILE, "wb") as f:
            f.write(contraseña_cifrada)

        popup.destroy()
        messagebox.showinfo("Listo", "Contraseña maestra creada correctamente.")

    popup = tb.Toplevel()
    popup.title("Crear contraseña maestra")
    centrar_ventana(popup, 300, 200)

    tb.Label(popup, text="Crea tu contraseña maestra:").pack(pady=5)
    entry1 = tb.Entry(popup, show="*", width=30)
    entry1.pack(pady=5)
    tb.Label(popup, text="Confirma la contraseña:").pack(pady=5)
    entry2 = tb.Entry(popup, show="*", width=30)
    entry2.pack(pady=5)
    tb.Button(popup, text="Guardar", bootstyle="success", command=guardar_contraseña).pack(pady=10)

def generar_contraseña():
    caracteres = string.ascii_letters + string.digits + string.punctuation
    contraseña = ''.join(secrets.choice(caracteres) for _ in range(16))
    entrada_contraseña.delete(0, 'end')
    entrada_contraseña.insert(0, contraseña)

def guardar():
    sitio = entrada_sitio.get()
    usuario = entrada_usuario.get()
    contraseña = entrada_contraseña.get()

    if not sitio or not usuario or not contraseña:
        messagebox.showwarning("Campos vacíos", "Por favor, rellena todos los campos.")
        return

    datos = {'usuario': usuario, 'contraseña': contraseña}
    datos_json = json.dumps(datos).encode()
    datos_cifrados = fernet.encrypt(datos_json)

    try:
        with open(DATA_FILE, 'ab') as archivo:
            archivo.write(sitio.encode() + b'||' + datos_cifrados + b'\n')
        messagebox.showinfo("Éxito", f"Contraseña guardada para {sitio}")
        entrada_sitio.delete(0, 'end')
        entrada_usuario.delete(0, 'end')
        entrada_contraseña.delete(0, 'end')
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

def ver_contraseñas():
    if not os.path.exists(MASTER_KEY_FILE):
        crear_contraseña_maestra()
        return

    def verificar():
        ingreso = entrada_maestra.get()
        with open(MASTER_KEY_FILE, "rb") as f:
            cifrada = f.read()
        try:
            original = fernet.decrypt(cifrada).decode()
            if ingreso == original:
                popup.destroy()
                mostrar_contraseñas()
            else:
                messagebox.showerror("Error", "Contraseña incorrecta.")
        except:
            messagebox.showerror("Error", "No se pudo verificar la contraseña.")

    popup = tb.Toplevel()
    popup.title("Verificación")
    centrar_ventana(popup, 300, 150)

    tb.Label(popup, text="Introduce la contraseña maestra:").pack(pady=10)
    entrada_maestra = tb.Entry(popup, show="*", width=30)
    entrada_maestra.pack(padx=10)
    tb.Button(popup, text="Verificar", bootstyle="primary", command=verificar).pack(pady=10)
    entrada_maestra.focus()

def mostrar_contraseñas():
    if not os.path.exists(DATA_FILE):
        messagebox.showinfo("Sin datos", "Aún no hay contraseñas guardadas.")
        return

    ventana_resultados = tb.Toplevel()
    ventana_resultados.title("Contraseñas Guardadas")
    centrar_ventana(ventana_resultados, 500, 400)

    with open(DATA_FILE, 'rb') as archivo:
        filas = archivo.readlines()

    for fila in filas:
        try:
            sitio, datos_cifrados = fila.split(b'||')
            datos_descifrados = fernet.decrypt(datos_cifrados).decode()
            datos_json = json.loads(datos_descifrados)
            usuario = datos_json['usuario']
            contraseña = datos_json['contraseña']

            texto = f"Sitio: {sitio.decode()}\nUsuario: {usuario}\nContraseña: {contraseña}\n{'-'*40}\n"
            etiqueta = tb.Label(ventana_resultados, text=texto, justify="left", anchor="w", font=("Courier", 10))
            etiqueta.pack(anchor="w")
        except Exception as e:
            print("Error al leer una línea:", e)

def centrar_ventana(ventana, ancho, alto):
    ventana.update_idletasks()
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    pos_x = (ancho_pantalla - ancho) // 2
    pos_y = (alto_pantalla - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")

# ========================
# INTERFAZ 
# ========================

ventana = tb.Window(themename="superhero")
ventana.title("Gestor de Contraseñas")
ventana.resizable(False, False)

centrar_ventana(ventana, 450, 250)

frame = tb.Frame(ventana, padding=20)
frame.pack(fill="both", expand=True)

tb.Label(frame, text="Sitio / Servicio:").grid(row=0, column=0, sticky="w", pady=5)
entrada_sitio = tb.Entry(frame, width=35)
entrada_sitio.grid(row=0, column=1, pady=5)

tb.Label(frame, text="Usuario / Correo:").grid(row=1, column=0, sticky="w", pady=5)
entrada_usuario = tb.Entry(frame, width=35)
entrada_usuario.grid(row=1, column=1, pady=5)

tb.Label(frame, text="Contraseña:").grid(row=2, column=0, sticky="w", pady=5)
entrada_contraseña = tb.Entry(frame, width=35)
entrada_contraseña.grid(row=2, column=1, pady=5)

btn_generar = tb.Button(frame, text="Generar", bootstyle="info", command=generar_contraseña)
btn_generar.grid(row=2, column=2, padx=5)

btn_guardar = tb.Button(frame, text="Guardar", bootstyle="success", command=guardar)
btn_guardar.grid(row=3, column=1, pady=10)

btn_ver = tb.Button(frame, text="Ver Contraseñas", bootstyle="warning", command=ver_contraseñas)
btn_ver.grid(row=4, column=1, pady=5)

ventana.mainloop()
