🚀 PROYECTO: Pupusería Las Tuks (Flask + PostgreSQL)
=====================================================

📁 ESTRUCTURA DE CARPETAS
-------------------------
tu_proyecto/
│
├── app.py
├── requirements.txt
├── templates/
│   ├── menu.html
│   ├── login.html
│   └── admin.html
└── static/
    └── tuks-img.png (opcional)

🧩 requirements.txt
--------------------
Flask
psycopg2-binary

💻 SUBIR A GITHUB
-----------------
1. Abre la carpeta del proyecto en VS Code.
2. Abre una terminal y ejecuta:
   git init
   git add .
   git commit -m "Subiendo Las Tuks a GitHub"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/las_tuks.git
   git push -u origin main

🚀 DESPLEGAR EN RENDER
----------------------
1. Entra a https://render.com
2. "New Web Service" → conecta tu repositorio de GitHub
3. En "Start Command" pon:
   gunicorn app:app
4. En "Environment" agrega las variables:

   FLASK_SECRET = clave_super_secreta
   DB_HOST = (host de tu base PostgreSQL)
   DB_NAME = las_tuks2
   DB_USER = postgres
   DB_PASSWORD = (tu contraseña)
   DB_PORT = 5432

📱 ENLACE PÚBLICO
------------------
Tu menú estará disponible en:
https://tu-app.onrender.com/menu

🔗 ADMINISTRADOR
-----------------
https://tu-app.onrender.com/
Usuario: admin
Contraseña: 1234

📸 GENERAR CÓDIGO QR
---------------------
1. Copia el enlace de tu menú (por ejemplo):
   https://tu-app.onrender.com/menu
2. Entra a: https://www.qr-code-generator.com/
3. Pega tu enlace → genera → descarga → imprime o comparte.
