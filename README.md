# Northstar Support Ticket Classifier

Sistema automatizado de clasificación y enrutamiento de tickets de soporte técnico IT utilizando la API de OpenAI.

El sistema lee tickets en formato de texto plano (`.txt`) desde una carpeta de entrada, clasifica su contenido según una taxonomía definida y los organiza automáticamente en carpetas de destino renombrándolos según corresponda.

---

## Taxonomía de Categorías

Los tickets son clasificados en exactamente una de las siguientes categorías válidas:
- `hardware`: Problemas físicos con impresoras, monitores, periféricos, etc.
- `software`: Errores en aplicaciones, fallos del sistema operativo, SAP, etc.
- `access`: Solicitudes o problemas de permisos, credenciales, VPN, cuentas.
- `data`: Consultas sobre bases de datos, informes, inconsistencias de datos.
- `other`: Otras solicitudes de soporte técnico fuera de las anteriores.

Cualquier categoría devuelta por el modelo que no pertenezca a esta lista (por ejemplo, `network`) se catalogará como `Category not defined` y se enviará a la carpeta de errores.

---

## Estructura de Carpetas

```text
northstar-support-classifier/
├── New tickets/          # Carpeta de entrada con tickets pendientes de clasificar (.txt)
├── Classified tickets/   # Tickets clasificados exitosamente (ej: ticket_001 - Category - software.txt)
├── Error tickets/        # Tickets vacíos o con categorías no definidas
├── classifier.py         # Módulo de integración con la API de OpenAI
├── main.py               # Lógica de procesamiento de archivos y orquestación por lotes
├── test_classifier.py    # Pruebas unitarias de la función de clasificación
├── test_main.py          # Pruebas unitarias y por lotes del flujo de archivos
└── README.md             # Documentación del proyecto
```

---

## Requisitos Previos

- Python 3.10 o superior.
- Una cuenta de OpenAI con créditos activos y una clave de API generada.

---

## Instalación

1. **Clonar o descargar el repositorio**:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd northstar-support-classifier
   ```

2. **Crear y activar un entorno virtual**:
   - En Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - En Linux / macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Instalar dependencias**:
   ```bash
   pip install openai pytest
   ```

---

## Configuración Segura de la API Key

> [!WARNING]
> **Nunca incluyas tu API Key en el código fuente ni la subas a repositorios de Git**. Si una clave se expone públicamente, puede ser revocada automáticamente o generar costos no autorizados.

El sistema utiliza la variable de entorno `OPENAI_API_KEY`. Para configurarla en tu sesión de trabajo:

- **Windows PowerShell**:
  ```powershell
  $env:OPENAI_API_KEY="tu-api-key-aqui"
  ```

- **Windows CMD**:
  ```cmd
  set OPENAI_API_KEY=tu-api-key-aqui
  ```

- **Linux / macOS**:
  ```bash
  export OPENAI_API_KEY="tu-api-key-aqui"
  ```

---

## Ejecución

1. Coloca los archivos `.txt` que desees procesar en la carpeta `New tickets/`.
2. Ejecuta el script principal:
   ```bash
   python main.py
   ```

### Comportamiento del Flujo

| Situación del Ticket | Resultado | Ubicación Final |
| :--- | :--- | :--- |
| **Ticket válido y categorizado** | Renombrado con la categoría | `Classified tickets/<nombre> - Category - <categoria>.txt` |
| **Fallo de API (`APITimeoutError`)** | Se preserva sin mover | `New tickets/<nombre>.txt` (listo para reintento) |
| **Ticket vacío o solo espacios** | Identificado como error | `Error tickets/<nombre>.txt` |
| **Categoría no reconocida (ej. network)** | Identificado como categoría no definida | `Error tickets/<nombre>.txt` |

---

## Ejecución de Pruebas Automatizadas

El proyecto cuenta con una suite completa de pruebas construida con `pytest` y `unittest.mock`. Las pruebas simulan tanto las llamadas al modelo como las operaciones sobre el sistema de archivos sin consumir saldo de la API ni alterar archivos reales.

Para ejecutar todas las pruebas:
```bash
pytest -v
```

Para ejecutar un archivo de pruebas específico:
```bash
pytest -v test_classifier.py
pytest -v test_main.py
```

---

## Limitaciones Conocidas

1. **Procesamiento Secuencial (Síncrono)**:
   - Los archivos se procesan uno a uno en un bucle síncrono. En volúmenes altos (cientos o miles de tickets), el tiempo total de procesamiento puede verse afectado por la latencia acumulada de la red. Una mejora futura es implementar procesamiento concurrente (`asyncio` o `concurrent.futures`).

2. **Reintentos Inmediatos ante Timeouts**:
   - Cuando ocurre un `APITimeoutError`, el ticket se conserva en `New tickets/` pero no se realiza un reintento inmediato con retroceso exponencial (*exponential backoff*) dentro de la misma ejecución.

3. **Formatos de Archivo Admitidos**:
   - Solo se procesan archivos de texto plano con extensión `.txt` codificados en UTF-8. Archivos `.pdf`, `.docx`, correos electrónicos `.eml` o imágenes no son admitidos actualmente.

4. **Taxonomía Cerrada**:
   - La lista de categorías es fija. Si un ticket describe un problema transversal o nuevo (como infraestructura de red o telecomunicaciones), el modelo no podrá asignarle una categoría válida y el archivo se derivará a `Error tickets/`.
