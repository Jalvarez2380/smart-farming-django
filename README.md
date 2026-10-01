# Smart Farming

Módulo académico de un Sistema Inteligente de Monitoreo Agrícola mediante IoT.
Permite administrar parcelas y sensores desde Django Admin, registrar lecturas,
consultar su histórico y detectar humedad baja. Las lecturas se ingresan manualmente;
la conexión física con dispositivos IoT queda fuera del alcance de esta entrega.

## Objetivo académico

Aplicar Ingeniería de Software mediante una implementación pequeña y verificable,
con pruebas unitarias, de integración y de aceptación, análisis estático e integración
continua. El proyecto utiliza la estructura Django existente.

## Stack

- Python 3.13 y Django 6.1.1 (versiones comprobadas en el entorno original).
- SQLite para persistencia.
- Django Templates, HTML y CSS propio, sin frameworks frontend.
- Ruff para análisis estático.
- Git/GitHub y GitHub Actions para versionado y CI.

## Instalación en Windows (PowerShell)

Desde la carpeta del proyecto, activa el entorno virtual existente:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_demo
python manage.py runserver
```

Abre **http://127.0.0.1:8000/**. Detén el servidor con `Ctrl+C`.
Si trabajas en una copia nueva que no tiene entorno virtual, créalo primero con
`py -3.13 -m venv .venv`. No es necesario ejecutar `startproject` ni `startapp`.

Si PowerShell no permite activar scripts, usa directamente el intérprete:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

La configuración usa SQLite (`db.sqlite3`), idioma español y zona horaria
`America/Guayaquil`. Django descubre los templates y archivos estáticos dentro
de la aplicación mediante `APP_DIRS` y `django.contrib.staticfiles`.

## Administración y uso

Para crear, modificar y administrar parcelas, sensores y mediciones:

```powershell
python manage.py createsuperuser
```

Ingresa a **http://127.0.0.1:8000/admin/** con las credenciales que tú definas.
No se incluye ningún usuario ni contraseña predefinidos.

| Página | Ruta | Función |
| --- | --- | --- |
| Resumen | `/` | Totales y ocho mediciones recientes con alertas |
| Parcelas | `/parcelas/` | Listado de parcelas y acceso a sus lecturas |
| Sensores | `/sensores/` | Tipo, parcela, unidad y estado |
| Registrar medición | `/mediciones/registrar/` | Formulario con validación y confirmación |
| Histórico | `/historico/` | Filtros combinados por parcela y tipo; 20 registros por página |

`cargar_demo` crea dos parcelas, seis sensores (uno de cada tipo en cada parcela)
y doce mediciones. Es transaccional y se puede repetir sin duplicar los ejemplos
ni sobrescribir registros existentes. Usa nombres y códigos con prefijo demo;
no deben cambiarse si se desea conservar esta identificación entre ejecuciones.

## Reglas y mantenibilidad

- La constante `UMBRAL_HUMEDAD_BAJA` está centralizada en
  `smart_farming/settings.py` y su valor inicial es 30 (%).
- La propiedad `Medicion.humedad_baja` evalúa la regla: tipo HUMEDAD y valor
  estrictamente inferior al umbral. En el umbral no se activa la alerta.
- La alerta **Humedad del suelo baja** aparece en resumen e histórico.
- Humedad entre 0 y 100 %, radiación no negativa y temperatura negativa permitida.
- Valores decimales de hasta dos posiciones; se rechazan valores no finitos.
- Los sensores tienen código único y opciones restringidas para tipo y estado.
- Los sensores de humedad deben usar `%`; solo se registran nuevas lecturas de sensores activos.
- `PROTECT` evita borrar parcelas con sensores o sensores con mediciones.
- Los formularios y el administrador ejecutan la validación de los modelos.
  Si se escribe desde scripts propios mediante el ORM, llamar `full_clean()` antes
  de `save()`: Django no ejecuta la validación del modelo automáticamente al guardar.
- Una tabla compartida evita duplicar la presentación y la alerta. El histórico
  conserva filtros al paginar y usa relaciones precargadas para evitar consultas por fila.

Esta entrega es una demostración local: `DEBUG=True` y formulario público, sin
autenticación para el registro manual. La clave incluida es un marcador de desarrollo,
no un secreto real; puede reemplazarse con `DJANGO_SECRET_KEY` en el entorno.
El administrador sí requiere autenticación.

## Pruebas automatizadas

```powershell
python manage.py test
```

Se incluyen **16 pruebas**, separadas en archivos:

| Archivo en `monitoreo/tests/` | Cantidad | Evidencia |
| --- | ---: | --- |
| `test_unitarias.py` | 3 | Crear parcela, crear sensor asociado, regla de humedad y sus límites |
| `test_integracion.py` | 2 | Relaciones persistidas y registro visible en histórico/dashboard |
| `test_aceptacion.py` | 1 | Usuario abre formulario, envía con CSRF y recibe confirmación |
| `test_calidad.py` | 10 | Valores inválidos, límites, sensores, filtros, demo idempotente, protección, páginas y paginación |

Las pruebas usan una base de datos de prueba independiente y no modifican los datos demo.
No requieren Selenium ni dispositivos físicos.

## Calidad de software

| Característica | Evidencia en la implementación |
| --- | --- |
| Adecuación funcional | Modelos, registro, listados, filtros, administración y alerta comprobados por tests |
| Fiabilidad | Validaciones, relaciones protegidas y carga demo transaccional e idempotente |
| Capacidad de interacción | Navegación en español, etiquetas, mensajes de error y éxito, diseño adaptable y alerta textual |
| Mantenibilidad | Umbral único, formularios y vistas separados, template compartido, pruebas y Ruff |

La revisión visual manual puede realizarse abriendo las cinco páginas a tamaño de
escritorio y móvil. Para comprobar la alerta, registrar humedad inferior al umbral;
para comprobar errores, intentar registrar humedad superior a 100.

## Análisis estático y verificaciones

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py check
python manage.py test
ruff check .
```

Ruff está configurado en `pyproject.toml`: errores básicos, nombres/importaciones
incorrectos y orden de imports. Puede ejecutarse sin activar el entorno con
`.\.venv\Scripts\ruff.exe check .`.

## Integración continua

`.github/workflows/django.yml` se activa con `push` y `pull_request`.
Usa Python 3.13, instala `requirements.txt`, comprueba Django, aplica migraciones,
verifica que no falten migraciones, ejecuta las pruebas y ejecuta Ruff.
Cualquier fallo detiene el trabajo y marca el pipeline como fallido.

El workflow está preparado; su ejecución remota requiere subir el proyecto a GitHub.
Esta entrega no crea repositorios remotos ni realiza commits o push. Las ramas,
commits y Pull Requests se harán manualmente para conservar evidencia académica.

## Estructura general

```text
smart-farming-django/
├── manage.py
├── smart_farming/          # Configuración y rutas principales
├── monitoreo/
│   ├── models.py           # Parcela, Sensor, Medicion y reglas
│   ├── forms.py            # Registro y filtros
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── migrations/
│   ├── management/commands/cargar_demo.py
│   ├── templates/monitoreo/
│   ├── static/monitoreo/css/styles.css
│   └── tests/              # Pruebas por categoría
├── .github/workflows/django.yml
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

`db.sqlite3`, el entorno virtual, cachés y `.env` están excluidos de Git.
