# Cómo probar el Taller 02 (Patrones Creacionales) sobre el repo base

Este es el repositorio base del profe (`Nram94/TEIS-DjangoSOLID`), que **ya trae
implementados** el Factory Method y el Builder del Tutorial 02:

- `tienda_app/infra/factories.py` → **Factory Method** (`PaymentFactory` + `MockPaymentProcessor`)
- `tienda_app/domain/builders.py` → **Builder** (`OrdenBuilder` con *fluent interface*)
- `tienda_app/services.py` → `CompraService` (integra Builder + Factory)
- `tienda_app/views.py` → `CompraView` (vista agnóstica que delega en la fábrica)

## Requisitos
```bash
pip install django djangorestframework
```

## Opción A — Probar en LOCAL con SQLite (más rápido, sin Docker)

El repo original está configurado para PostgreSQL. Para probar sin levantar una
base de datos, se incluye `Tienda/settings_sqlite.py`, que hereda del settings
original pero usa el `db.sqlite3` que ya viene en el repo.

```bash
# 1. Migrar (usando SQLite)
python manage.py migrate --settings=Tienda.settings_sqlite

# 2. Arrancar en modo MOCK (evidencia del Taller 02)
#    Windows (PowerShell):
$env:PAYMENT_PROVIDER="MOCK"; python manage.py runserver --settings=Tienda.settings_sqlite
#    Linux/Mac/GitBash:
PAYMENT_PROVIDER=MOCK python manage.py runserver --settings=Tienda.settings_sqlite
```

Luego abre en el navegador:  **http://127.0.0.1:8000/compra/1/**
(el `1` es el id del libro; usa un libro que tenga inventario con stock).

Pulsa el botón de comprar y mira la **consola de Django**. Verás:
```
[DEBUG] Mock Payment: Procesando pago de $... sin cargo real.
```
👉 **Esa es la captura que pide la entrega del Taller 02.**

En modo por defecto (banco real) se genera además el log de auditoría del
Taller 01: `pagos_locales_Juan_Camilo_Gomez.log`.

## Opción B — Probar con PostgreSQL vía Docker (como el profe)

```bash
docker-compose up --build
```
Esto levanta la app con Postgres según el `docker-compose.yml` del repo.
Para activar el modo MOCK, agrega la variable de entorno al servicio web
(`PAYMENT_PROVIDER=MOCK`) en el `docker-compose.yml`.

## Entregables del Taller 02
1. **Captura** → consola con `[DEBUG] Mock Payment...` (ver Opción A).
2. **Código fuente** → `tienda_app/infra/factories.py` y `tienda_app/domain/builders.py`.
3. **Reflexión** → ver abajo.

### Reflexión
El `OrdenBuilder` reduce el riesgo de errores frente a crear la orden
directamente en la vista porque centraliza y encapsula toda la lógica de
construcción en un solo lugar. La validación de datos obligatorios (el libro),
el cálculo del total con IVA (delegado a `CalculadorImpuestos`) y la creación de
la `Orden` ocurren siempre dentro de `build()`, por lo que ninguna vista puede
olvidar un paso ni duplicar un cálculo de forma inconsistente. Si faltan datos,
lanza un `ValueError` y nunca se crea una orden a medias. Además, su *fluent
interface* (`.con_usuario().con_libro().con_cantidad().para_envio().build()`)
hace el código legible y auto-documentado, y el `reset()` permite reutilizar el
builder de forma segura. En resumen, saca la responsabilidad de armar objetos
complejos fuera de la capa de presentación, dejando la vista limpia y enfocada
solo en orquestar.

---

# Cómo probar el Taller 03 (API REST con DRF)

El Taller 03 añade una **API REST** sobre la misma arquitectura. La API reutiliza
la misma Capa de Servicio (`CompraService`), demostrando que tanto la vista HTML
como el cliente JSON usan la misma lógica de negocio.

Archivos de la API (ya implementados en el repo):
- `tienda_app/api/serializers.py` → **Adapter** (`LibroSerializer`, `OrdenInputSerializer`/DTO)
- `tienda_app/api/views.py` → **Controlador** (`CompraAPIView`, reutiliza `CompraService`)
- Endpoint registrado en `tienda_app/urls.py`: `api/v1/comprar/`

## Requisitos
```bash
pip install django djangorestframework
```

## Probar la API

```bash
# Arrancar en modo MOCK (o quítalo para modo BANCO que genera el log)
#   Windows (PowerShell):
$env:PAYMENT_PROVIDER="MOCK"; python manage.py runserver --settings=Tienda.settings_sqlite
#   Linux/Mac/GitBash:
PAYMENT_PROVIDER=MOCK python manage.py runserver --settings=Tienda.settings_sqlite
```

### Opción A — Interfaz web de DRF (navegador)
Abre: **http://127.0.0.1:8000/api/v1/comprar/**
Verás la interfaz "Browsable API" de DRF. En el formulario inferior, pega el JSON:
```json
{"libro_id": 1, "direccion_envio": "Calle 123", "cantidad": 1}
```
y pulsa **POST**. Deberías recibir un **HTTP 201 Created** con:
```json
{"estado": "exito", "mensaje": "Orden creada. Total: 157.08..."}
```

### Opción B — Postman o curl
```bash
curl -X POST http://127.0.0.1:8000/api/v1/comprar/ \
     -H "Content-Type: application/json" \
     -d '{"libro_id": 1, "direccion_envio": "Calle 123", "cantidad": 1}'
```

## Demostrar que el inventario se descuenta (clave del taller)
1. Antes de comprar, mira el stock en el shell:
   ```bash
   python manage.py shell --settings=Tienda.settings_sqlite
   >>> from tienda_app.models import Inventario
   >>> Inventario.objects.get(libro_id=1).cantidad
   ```
2. Haz el POST a la API (Opción A o B).
3. Vuelve a consultar el stock: habrá bajado en 1. Esto prueba que la API y la
   vista HTML comparten la misma lógica de negocio.

En modo BANCO (sin `PAYMENT_PROVIDER=MOCK`) se genera además el log de auditoría
`pagos_locales_Juan_Camilo_Gomez.log`.

## Entregables del Taller 03
1. **Captura** del POST a `/api/v1/comprar/` (Browsable API o Postman) mostrando
   el 201 y la respuesta JSON.
2. **Archivo de log** `pagos_locales_Juan_Camilo_Gomez.log` (generado en modo BANCO),
   y evidencia de que el inventario cambió tras la compra por API.
3. **Código fuente** `api/serializers.py` y `api/views.py`.
