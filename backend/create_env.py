from cryptography.fernet import Fernet

key = Fernet.generate_key().decode()
with open(".env", "w") as f:
    f.write(f"SECRET_ENCRYPT_KEY={key}\n")
    f.write("PTERODACTYL_URL=https://panel.fenixcloud.xyz/api/client\n")
    f.write("JWT_SECRET=super-secret-pterodev-companion-key\n")
    f.write("DB_PATH=companion.db\n")
print("Archivo .env creado con éxito.")
