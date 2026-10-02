# Taller 04 — Dockerización y Despliegue en AWS

Este taller NO escribe código nuevo: empaqueta la "Tienda API" (Tutorial 03) en
Docker y la despliega en AWS EC2.

## ✅ Lo que ya quedó preparado en el proyecto

| Archivo | Estado |
|---|---|
| `Tienda/settings.py` — BD lee variables de entorno (`os.environ.get`) | ✅ listo (Paso 1.1) |
| `Tienda/settings.py` — `ALLOWED_HOSTS` lee de env (por defecto `*`) | ✅ listo (necesario para la IP de EC2) |
| `requirements.txt` — Django, DRF y `psycopg2-binary` | ✅ creado (Paso 1.2) |
| `Dockerfile` — en la raíz, junto a `manage.py` | ✅ creado (Paso 2) |
| `docker-compose.yml` — Django + PostgreSQL | ✅ listo (Paso 3) |
| Comando `seed` — carga libros con inventario | ✅ creado (para que la API tenga datos) |

El `command` del servicio `web` en el compose ejecuta automáticamente:
`migrate → seed → runserver 0.0.0.0:8000`, así la API responde sin pasos manuales.

Verificado localmente: la imagen Docker construye y Django arranca dentro del
contenedor sin errores.

---

## PASO A — Prueba local con Docker (en tu PC con Docker Desktop)

```bash
# En la raíz del proyecto (donde está docker-compose.yml)
docker compose up --build        # (o docker-compose up --build en v1)
```
Luego abre: **http://localhost:8000/api/v1/comprar/**
Debes ver la interfaz Browsable API de DRF respondiendo. ✅

Para detener: `Ctrl+C` y luego `docker compose down`.

---

## PASO B — Despliegue en AWS EC2 (lo haces tú desde tu cuenta)

> Requiere tu cuenta de AWS Academy. Estos pasos son manuales en la consola de AWS.

### B.1 — Subir el proyecto a GitHub (si aún no está)
En AWS clonarás desde GitHub. Sube este proyecto a un repo tuyo:
```bash
git init
git add .
git commit -m "Taller 04: dockerizacion"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

### B.2 — Lanzar la instancia EC2
1. AWS Academy LMS → inicia el laboratorio → consola AWS → EC2 → Launch Instance.
2. **Name:** Servidor-Django
3. **OS Image:** Amazon Linux 2023 AMI (Free tier)
4. **Instance Type:** t2.micro
5. **Key Pair:** vockey
6. **Network Settings:** marca Allow SSH, Allow HTTP, Allow HTTPS
7. Launch.

### B.3 — Conectar por SSH
Selecciona la instancia → **Connect** → pestaña "EC2 Instance Connect" → abre terminal.

### B.4 — Instalar Git y Docker en la instancia
```bash
sudo dnf update -y
sudo dnf install git docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
exit            # cierra y vuelve a conectar para aplicar permisos
```

### B.5 — Clonar y desplegar
```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO
docker compose up -d --build     # (o docker-compose up -d --build)
docker ps                        # verifica que los contenedores corren
```

### B.6 — Abrir el puerto 8000 (Security Group)
1. EC2 → Instances → selecciona tu instancia → pestaña **Security**.
2. Clic en el Security Group (ej. launch-wizard-1).
3. **Edit inbound rules → Add rule**.
4. Type: **Custom TCP** | Port range: **8000** | Source: **0.0.0.0/0**.
5. Save rules.

---

## 📸 Entrega del Taller 04

Toma una captura del navegador accediendo a:
```
http://<IP-PUBLICA-DE-TU-EC2>:8000/api/v1/comprar/
```
Debe verse la respuesta JSON de la API (interfaz Browsable de DRF) **servida desde AWS**.
Esa captura es la evidencia que se sube a la asignación "tutorial04".

### Consejos / problemas comunes
- Si ves "DisallowedHost": ya está resuelto (ALLOWED_HOSTS=*), pero si lo
  restringiste, exporta `DJANGO_ALLOWED_HOSTS` con la IP pública.
- Si el puerto no responde: revisa el Security Group (Paso B.6) y que
  `docker ps` muestre el contenedor `web` arriba.
- Si la BD da error al arrancar: vuelve a correr `docker compose up` (a veces
  Postgres tarda en estar listo la primera vez); el `migrate` reintenta al relanzar.
