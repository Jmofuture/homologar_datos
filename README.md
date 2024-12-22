
# Proyecto CRM: Limpieza de Datos y Generación de Archivo Homologado

## Descripción

Este proyecto se encarga de realizar la limpieza y homologación de datos, generando un archivo Excel (`Datos - homologados.xlsx`). El proceso incluye:
- Verificación de la existencia previa del archivo.
- Procesamiento de los datos usando funciones personalizadas.
- Creación del archivo Excel solo si no existe previamente.

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

📁 CRM  
│  
├── 📁 assets  
│   ├── Consigna.docx         # Documento con las instrucciones del proyecto  
│   ├── Datos.xlsx            # Archivo con los datos de entrada  
│   ├── formato.xlsx          # Plantilla para el archivo final  
│   └── lut_paises.csv        # Archivo de lookup para homologación de datos  
│  
├── 📁 src  
│   ├── __init__.py           # Archivo de inicialización  
│   ├── clean_data.py         # Contiene la función principal de limpieza de datos  
│  
├── requirements.txt          # Archivo con las dependencias del proyecto  
└── main.py                   # Script principal que ejecuta el programa  
└── Datos - homologados.xlsx  # Archivo generado al procesar los datos (si no existe)  

## Requisitos Previos

Asegúrate de tener instalado lo siguiente antes de ejecutar el proyecto:

- **Python**: Versión 3.8 o superior.
- Las dependencias necesarias están listadas en `requirements.txt`.

Instala las dependencias ejecutando:

- pandas
- duckdb
- openpyxl
- Unidecode

```bash
pip install -r requirements.txt

```
## Ejecución

- Asegúrate de que los archivos necesarios estén en la carpeta `assets` (por ejemplo, `Datos.xlsx`, `formato.xlsx`).
- Ejecuta el script principal usando:
```bash
python main.py


```

### Entrada (Datos originales sin procesar)
| ID  | Fecha de creación y hora de creación | Nombre   | Correo               | País   | Estado            | Código país | Teléfono       | Puesto de trabajo                          |
|-----|--------------------------------------|----------|----------------------|--------|-------------------|-------------|----------------|--------------------------------------------|
| 1   | 28/04/2022 7:43                     | MARITZA  | correo1@empresa.com  | MEXICO | CIUDAD DE MÉXICO  | 52          | 55 5555 5555   | Ingeniero de proyectos y logística         |
| 2   | 28/04/2022 11:07                    | ROSARIO  | correo2@empresa.com  | MEXICO | MÉXICO            | 52          | 55 5555 5555   | Supervisor de logística y embarques        |

### Salida (Datos transformados)
| Nombre   | Correo               | País         | Código país   | Teléfono      | Puesto de trabajo                          | Área       |
|----------|----------------------|--------------|---------------|---------------|--------------------------------------------|------------|
| MARITZA  | correo1@empresa.com  | MEXICO       | México (+52)  | 55 5555 5555  | Ingeniero de proyectos y logística         | INGENIERO  |
| ROSARIO  | correo2@empresa.com  | MEXICO       | México (+52)  | 55 5555 5555  | Supervisor de logística y embarques        | SUPERVISOR |

