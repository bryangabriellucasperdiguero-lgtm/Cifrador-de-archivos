import os
import io
import json
import zipfile
import secrets
import hashlib
import tkinter as tk

from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# ==========================================
# CONFIGURACIÓN
# ==========================================

MAGIC = b"CIFRADOR01"
ITERACIONES = 600000


# ==========================================
# DERIVACIÓN DE CLAVE
# ==========================================

def generar_clave(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERACIONES
    )
    return kdf.derive(password.encode("utf-8"))


# ==========================================
# CIFRADO DEL CONTENEDOR
# ==========================================

def cifrar_contenedor(datos, password):
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)

    clave = generar_clave(password, salt)
    aes = AESGCM(clave)

    cifrado = aes.encrypt(nonce, datos, None)

    cabecera = {
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "sha256": hashlib.sha256(datos).hexdigest()
    }

    cabecera_bytes = json.dumps(cabecera).encode("utf-8")

    return (
        MAGIC
        + len(cabecera_bytes).to_bytes(4, "big")
        + cabecera_bytes
        + cifrado
    )


def descifrar_contenedor(datos, password):
    if not datos.startswith(MAGIC):
        raise ValueError("El archivo no es compatible.")

    posicion = len(MAGIC)

    longitud = int.from_bytes(
        datos[posicion:posicion + 4],
        "big"
    )
    posicion += 4

    cabecera = json.loads(
        datos[posicion:posicion + longitud].decode("utf-8")
    )
    posicion += longitud

    salt = bytes.fromhex(cabecera["salt"])
    nonce = bytes.fromhex(cabecera["nonce"])

    clave = generar_clave(password, salt)
    aes = AESGCM(clave)

    original = aes.decrypt(
        nonce,
        datos[posicion:],
        None
    )

    if hashlib.sha256(original).hexdigest() != cabecera["sha256"]:
        raise ValueError("La integridad del archivo no es válida.")

    return original


# ==========================================
# CONTRASEÑA
# ==========================================

def pedir_password():
    password = simpledialog.askstring(
        "Contraseña",
        "Introduce una contraseña:",
        show="*"
    )

    if not password:
        return None

    if len(password) < 8:
        messagebox.showwarning(
            "Contraseña",
            "La contraseña debe tener al menos 8 caracteres."
        )
        return None

    return password


def pedir_confirmacion(password):
    confirmacion = simpledialog.askstring(
        "Confirmar contraseña",
        "Repite la contraseña:",
        show="*"
    )

    if password != confirmacion:
        messagebox.showerror(
            "Error",
            "Las contraseñas no coinciden."
        )
        return False

    return True


# ==========================================
# CREAR ARCHIVO CIFRADO
# ==========================================

def guardar_cifrado(datos, nombre):
    destino = filedialog.asksaveasfilename(
        title="Guardar archivo cifrado",
        defaultextension=".cifrado",
        initialfile=nombre + ".cifrado",
        filetypes=[
            ("Archivos cifrados", "*.cifrado"),
            ("Todos los archivos", "*.*")
        ]
    )

    if not destino:
        return False

    ruta = Path(destino)

    if ruta.exists():
        messagebox.showerror(
            "Error",
            "El archivo de destino ya existe."
        )
        return False

    ruta.write_bytes(datos)
    return True


# ==========================================
# CIFRAR ARCHIVOS SELECCIONADOS
# ==========================================

def cifrar_archivos():
    archivos = filedialog.askopenfilenames(
        title="Seleccionar archivos"
    )

    if not archivos:
        return

    password = pedir_password()

    if password is None:
        return

    if not pedir_confirmacion(password):
        return

    buffer = io.BytesIO()

    try:
        with zipfile.ZipFile(
            buffer,
            "w",
            compression=zipfile.ZIP_DEFLATED
        ) as archivo_zip:

            for ruta in archivos:
                ruta = Path(ruta)

                if ruta.is_file() and not ruta.is_symlink():
                    archivo_zip.write(
                        ruta,
                        arcname=ruta.name
                    )

        datos = cifrar_contenedor(
            buffer.getvalue(),
            password
        )

        if guardar_cifrado(datos, "archivos"):
            messagebox.showinfo(
                "Cifrado completado",
                f"Se han cifrado {len(archivos)} archivos.\n"
                "Los originales permanecen intactos."
            )

    except Exception as error:
        messagebox.showerror(
            "Error",
            str(error)
        )


# ==========================================
# CIFRAR UNA CARPETA COMO ARCHIVO ÚNICO
# ==========================================

def cifrar_carpeta():
    carpeta = filedialog.askdirectory(
        title="Seleccionar carpeta"
    )

    if not carpeta:
        return

    carpeta = Path(carpeta)

    password = pedir_password()

    if password is None:
        return

    if not pedir_confirmacion(password):
        return

    buffer = io.BytesIO()
    contador = 0

    try:
        with zipfile.ZipFile(
            buffer,
            "w",
            compression=zipfile.ZIP_DEFLATED
        ) as archivo_zip:

            for raiz, directorios, archivos in os.walk(carpeta):
                directorios[:] = [
                    d for d in directorios
                    if not (Path(raiz) / d).is_symlink()
                ]

                for nombre in archivos:
                    ruta = Path(raiz) / nombre

                    if ruta.is_symlink() or not ruta.is_file():
                        continue

                    relativo = ruta.relative_to(carpeta)

                    archivo_zip.write(
                        ruta,
                        arcname=str(Path(carpeta.name) / relativo)
                    )

                    contador += 1

        datos = cifrar_contenedor(
            buffer.getvalue(),
            password
        )

        if guardar_cifrado(datos, carpeta.name):
            messagebox.showinfo(
                "Cifrado completado",
                f"Se han incluido {contador} archivos.\n"
                "La carpeta original permanece intacta."
            )

    except Exception as error:
        messagebox.showerror(
            "Error",
            str(error)
        )


# ==========================================
# DESCIFRAR Y EXTRAER ARCHIVO
# ==========================================

def descifrar_archivo():
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo cifrado",
        filetypes=[
            ("Archivos cifrados", "*.cifrado"),
            ("Todos los archivos", "*.*")
        ]
    )

    if not archivo:
        return

    password = simpledialog.askstring(
        "Contraseña",
        "Introduce la contraseña de cifrado:",
        show="*"
    )

    if not password:
        return

    destino = filedialog.askdirectory(
        title="Seleccionar carpeta de recuperación"
    )

    if not destino:
        return

    destino = Path(destino)

    try:
        datos = Path(archivo).read_bytes()
        contenido = descifrar_contenedor(datos, password)

        buffer = io.BytesIO(contenido)

        with zipfile.ZipFile(buffer, "r") as archivo_zip:

            miembros = archivo_zip.infolist()

            for miembro in miembros:
                ruta = Path(miembro.filename)

                if ruta.is_absolute() or ".." in ruta.parts:
                    raise ValueError(
                        "El archivo contiene una ruta no permitida."
                    )

                if miembro.is_dir():
                    continue

                salida = (destino / ruta).resolve()
                raiz = destino.resolve()

                if salida != raiz and raiz not in salida.parents:
                    raise ValueError(
                        "Se ha detectado una ruta no permitida."
                    )

                if salida.exists():
                    raise FileExistsError(
                        f"Ya existe este archivo: {salida}"
                    )

            for miembro in miembros:
                if miembro.is_dir():
                    continue

                salida = destino / miembro.filename
                salida.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                with archivo_zip.open(miembro) as origen:
                    with open(salida, "xb") as resultado:
                        resultado.write(origen.read())

        messagebox.showinfo(
            "Descifrado completado",
            "Los archivos se han recuperado correctamente."
        )

    except Exception as error:
        messagebox.showerror(
            "Error de descifrado",
            f"No se pudo recuperar el contenido:\n{error}"
        )


# ==========================================
# INTERFAZ
# ==========================================

ventana = tk.Tk()
ventana.title("Cifrador de archivos")
ventana.geometry("470x440")
ventana.resizable(False, False)
ventana.configure(bg="#191919")


titulo = tk.Label(
    ventana,
    text="CIFRADOR DE ARCHIVOS",
    font=("Arial", 20, "bold"),
    fg="#4da6ff",
    bg="#191919"
)
titulo.pack(pady=(30, 10))


subtitulo = tk.Label(
    ventana,
    text="Protección de archivos mediante AES-256",
    font=("Arial", 10),
    fg="white",
    bg="#191919"
)
subtitulo.pack(pady=(0, 25))


def crear_boton(texto, funcion, color):
    return tk.Button(
        ventana,
        text=texto,
        command=funcion,
        width=35,
        height=2,
        bg=color,
        fg="white",
        activebackground=color,
        activeforeground="white",
        relief="flat",
        font=("Arial", 10, "bold"),
        cursor="hand2"
    )


crear_boton(
    "Cifrar archivos",
    cifrar_archivos,
    "#27649b"
).pack(pady=8)


crear_boton(
    "Cifrar carpeta entera",
    cifrar_carpeta,
    "#27649b"
).pack(pady=8)


crear_boton(
    "Descifrar archivo",
    descifrar_archivo,
    "#28734b"
).pack(pady=8)


pie = tk.Label(
    ventana,
    text="Los archivos originales nunca se modifican.",
    font=("Arial", 9),
    fg="#aaaaaa",
    bg="#191919"
)
pie.pack(side="bottom", pady=20)


ventana.mainloop()

