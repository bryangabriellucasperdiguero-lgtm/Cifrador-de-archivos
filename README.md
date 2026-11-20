Cifrador de archivos

Cifrador de archivos es una aplicación gratuita desarrollada en Python que permite proteger archivos y carpetas mediante cifrado AES-256-GCM.

Características

- Cifrado de múltiples archivos.
- Cifrado de carpetas completas.
- Contraseña personalizable.
- Recuperación mediante la contraseña original.
- Interfaz gráfica sencilla.
- Código abierto.

Requisitos

- Windows 10 o superior.
- Python 3.
- Biblioteca "cryptography".

Instalación

py -m pip install -r requirements.txt

Ejecución

py cifrador.py

Estado

Versión 0.1.0 — Experimental.

Seguridad

Los archivos originales se conservan. El usuario debe guardar su contraseña: si la pierde, no podrá recuperar los datos cifrados.

Este proyecto se proporciona con fines educativos y de protección de información. No se recomienda utilizar esta versión para proteger datos importantes sin una auditoría y pruebas adicionales.
