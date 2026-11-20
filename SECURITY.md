Política de seguridad

Estado del proyecto

Cifrador de archivos es un proyecto experimental en desarrollo. Aunque utiliza AES-256-GCM para proteger los datos, todavía no ha sido sometido a una auditoría de seguridad independiente.

No se recomienda utilizarlo para proteger información crítica o irremplazable.

Medidas de seguridad

- Utiliza cifrado AES-256-GCM.
- Deriva las claves mediante PBKDF2-HMAC-SHA256.
- Genera una sal aleatoria para cada operación de cifrado.
- Comprueba la autenticidad de los datos durante el descifrado.
- Conserva los archivos originales sin modificarlos.

Limitaciones conocidas

- El procesamiento se realiza en memoria RAM, por lo que los archivos grandes pueden provocar problemas.
- Todavía existen limitaciones en el tratamiento de archivos con nombres duplicados.
- El programa puede presentar errores durante la extracción de archivos.

Comunicación de vulnerabilidades

Si encuentras un fallo de seguridad, informa al propietario del repositorio mediante un aviso privado o un canal de contacto disponible.

No publiques detalles de una vulnerabilidad que pueda comprometer a otros usuarios antes de que exista una solución.

Recomendación

Mantén siempre copias de seguridad independientes de los archivos originales y no dependas exclusivamente de esta aplicación para proteger información importante.
