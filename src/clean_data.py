import os
import duckdb as db
import pandas as pd

from unidecode import unidecode

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.join(current_directory, '..')



# Funciones para cargar y hacer algunas limpiezas en los archivos

def format_text(df: pd.DataFrame, column: pd.Series) -> pd.DataFrame:
    """
    Elimina las tildes de los valores en una columna específica de un DataFrame.

    Parámetros:
    df (pd.DataFrame): El DataFrame que contiene la columna.
    column (str): El nombre de la columna de la cual se eliminarán las tildes.

    Retorna:
    pd.DataFrame: El DataFrame con la columna modificada.
    """
    df[column] = df[column].apply(unidecode)
    df[column] = df[column].str.strip()
    return df


def cargar_excel(archive: str, sheet: str = None) -> pd.DataFrame:
    """
    Carga un archivo Excel desde la carpeta 'assets'.

    Parámetros:
    archive (str): El nombre del archivo (sin extensión) que se desea cargar.
    sheet (str, opcional): El nombre de la hoja que se desea cargar. Obligatorio si el archivo es 'Formato'.

    Retorna:
    pd.DataFrame: El DataFrame con los datos cargados del archivo Excel.

    """
    try:
        if archive == "Formato" and sheet is None:
            raise ValueError("La hoja debe ser especificada para el archivo 'Formato'")
        
        data = pd.read_excel(f'{parent_path}/assets/{archive}.xlsx', sheet_name=None, header=0)

        if isinstance(data, dict):
            if sheet is not None and sheet in data:
                df = data[sheet]
                return df  # Devuelve solo el DataFrame de la hoja seleccionada
            elif sheet is None:
                df = next(iter(data.values()))  # Devuelve el primer DataFrame si no se especifica hoja
                return df
            else:
                raise ValueError(f"La hoja '{sheet}' no se encuentra en el archivo.")
        else:
            return data  # Si solo hay una hoja, devuelve directamente el DataFrame

    except UnicodeDecodeError as e:
        print("Hubo un error", {e})
    except ValueError as e:
        print("Hubo un error", {e})
    except Exception as e:
        print("Hubo un error", {e})


def lut_paises() -> pd.DataFrame:

    """
    Carga el archivo CSV 'lut_paises.csv' y devuelve una serie con los nombres de los países 
    en la equivalencia deseada.

    Parámetros:
    idiom (str, opcional): El idioma en el que se desean obtener los nombres de los países.
        Si se pasa 'esp', se devuelve la columna 'DescESP' (español). 
        Si se pasa 'eng', se devuelve la columna 'DescENG' (inglés). 
        Si no se pasa ningún idioma, se devuelven ambas columnas 'DescESP' y 'DescENG' como una serie.

    Retorna:
    pd.Series: Una serie con los nombres de los países en el idioma solicitado (o ambos idiomas si no se pasa parámetro).
    """
    try:
        countries = pd.read_csv(f'{parent_path}/assets/lut_paises.csv', sep=';', encoding='latin1')
        countries["esp_formatted"] = countries["DescESP"]
        countries = format_text(countries, 'esp_formatted')
    except UnicodeDecodeError as e:
        print("Hubo un error", {e})
    except Exception as e:
        print("Hubo un error", {e})
    
    return countries


def extract_country_code(df: pd.DataFrame, column: pd.Series) -> pd.DataFrame:
    """
    Extrae el número del código de país y el nombre del país de una columna específica de un DataFrame,
    eliminando el signo '+' y los espacios, y crea nuevas columnas 'country_code' y 'country_name_upper'.

    Parámetros:
    df (pd.DataFrame): El DataFrame que contiene la columna.
    column (str): El nombre de la columna de la cual se extraerán los datos.

    Retorna:
    pd.DataFrame: El DataFrame con nuevas columnas 'country_code' y 'country_name_upper'.
    """
    df['country_code'] = df[column].str.extract(r'\+(\d{1,5})\s*(\d*)')[0].str.cat(df[column].str.extract(r'\+(\d{1,5})\s*(\d*)')[1], sep='').str.replace(' ', '')
    df['country_name'] = df[column].str.extract(r'([^\(]+)')[0].str.strip().str.upper()
    return df


# Funciones para cargar lo df en memoria

def db_to_csv(conn: db.DuckDBPyConnection, db: str):
    """
    Exporta el resultado de una consulta SQL a un archivo CSV.

    Parámetros:
    conn (duckdb.DuckDBPyConnection): La conexión a la base de datos.
    db (str): El nombre de la tabla que se desea exportar.

    Retorna:
    None: Genera un archivo CSV con el nombre de la tabla.
    """
    try:
        file_name = f"{db}.csv"  # El nombre del archivo CSV será igual al nombre de la tabla.
        conn.execute(f"""
        COPY (SELECT * FROM {db}) TO '{file_name}' WITH (HEADER, DELIMITER ';');
        """)
        print(f"Archivo '{file_name}' creado")
    except Exception as e:
        print(f"Error al exportar la tabla '{db}' a CSV: {e}")


def db_register(conn: db.DuckDBPyConnection, df: pd.DataFrame, name: str):
    """
    Registra un DataFrame en memoria como una tabla

    Parámetros:
    con (duckdb.Connection): La conexión a la base de datos.
    df (pd.DataFrame): El DataFrame que se desea registrar.
    name (str): El nombre con el que se registrará el DataFrame en la base de datos.

    """
    return conn.register(name, df)


def raw_data_df() -> pd.DataFrame:

    raw_data: pd.DataFrame = cargar_excel(archive='Datos')
    raw_data: pd.DataFrame = format_text(df=raw_data, column="Puesto de trabajo")


    return raw_data


def countries_code_format_df() -> pd.DataFrame:

    format_country_code = cargar_excel(archive='formato', sheet='Código país')
    format_country_code = extract_country_code(df=format_country_code, column='Código país')
    format_country_code = format_text(df=format_country_code, column='country_name')

    return format_country_code


def country_name_format_strip() -> pd.DataFrame:
    format_country_name = cargar_excel(archive='formato', sheet='País')
    format_country_name["País"] = format_country_name["País"].str.replace('\u00A0', '', regex=True).str.strip()
    
    return format_country_name


# Funcion donde se realizan las tranformaciones y df final

def datos_homologados()  -> pd.DataFrame:

    # Connecion a la base de datos en memoria
    conn: db.DuckDBPyConnection = db.connect()

    format_country_name = cargar_excel(archive='formato', sheet='País')
    format_position = cargar_excel(archive='formato', sheet='Cargo')
    format_field = cargar_excel(archive='formato', sheet='Áreas')
    

    # Datos Base Paises
    db_register(conn=conn, df=raw_data_df(), name='raw_data_db')
    db_register(conn=conn, df=lut_paises(), name='lut_paises_db')
    db_register(conn=conn, df=countries_code_format_df(), name='countries_code_format_db')
    db_register(conn=conn, df=country_name_format_strip(), name='country_name_format_strip_db')
    

    data_country = conn.execute("""
        SELECT rd.Nombre ,rd.Correo ,rd."Código país" ,rd."Teléfono" ,rd."Puesto de trabajo"
        ,CASE WHEN esp_formatted = 'ESTADOS UNIDOS' THEN 'USA' 
              WHEN esp_formatted = 'REPUBLICA DEMOCRATICA DEL CONGO' THEN 'CONGO' 
              WHEN esp_formatted = 'KIRGUISTAN' THEN 'KIRGIZSTAN' 
              WHEN esp_formatted = 'REINO UNIDO (GRAN BRETANA)' THEN 'REINO UNIDO' 
              WHEN esp_formatted = 'GUINEA ECUATORIAL' THEN 'GUINEA' 
              WHEN esp_formatted = 'ESPANA' THEN 'ESPANA' 
              WHEN esp_formatted = 'YEMEN' THEN 'YEMEN' 
              ELSE cn."País" END AS "País"
        FROM raw_data_db AS rd
            INNER JOIN lut_paises_db AS lp ON lp."DescENG" = rd."País"
            LEFT JOIN country_name_format_strip_db AS cn ON cn."País" = lp.esp_formatted""").df()


    data_country_code = conn.execute("""
        SELECT dc.Nombre ,dc.Correo ,cc."Código país" ,dc."Teléfono" ,dc."Puesto de trabajo" AS "Puesto"
        ,CASE WHEN dc."País" = 'ESPANA' THEN 'ESPAÑA' ELSE dc."País" END AS "País"
        FROM data_country AS dc
            INNER JOIN countries_code_format_db AS cc ON cc.country_name = dc."País" """).df()


    # Datos base prefesion/area

    db_register(conn=conn, df=format_field, name='format_field_db')
    #dc.Nombre, Correo, dc."País", dc."Código país", dc."Teléfono",
        
    data_area = conn.execute("""
        SELECT
        dc.Correo,
        dc."Puesto",
        CASE 
            -- Presidentes
            WHEN dc."Puesto" ILIKE '%presidente%' OR 
                 dc."Puesto" ILIKE '%president%' OR
                 dc."Puesto" ILIKE '%dueno%' OR
                 dc."Puesto" ILIKE '%propietario%' OR
                 dc."Puesto" ILIKE '%fundador%' OR
                 dc."Puesto" ILIKE '%founder%' 
                 THEN 'PRESIDENTE'
            -- Vicepresidentes
            WHEN dc."Puesto" ILIKE '%vicepresidente%' OR 
                 dc."Puesto" ILIKE '%vice president%' 
                 THEN 'VICEPRESIDENTE'
            -- CEO
            WHEN dc."Puesto" ILIKE '%ceo%' OR 
                dc."Puesto" ILIKE '%director ejecutivo%' 
                THEN 'CEO'
            -- Directores
            WHEN dc."Puesto" ILIKE '%director%' OR
                 dc."Puesto" ILIKE '%head%'
                THEN 'DIRECTOR'     
            -- Subdirectores
            WHEN dc."Puesto" ILIKE '%subdirector%' OR
                 dc."Puesto" ILIKE '%subdirector%' 
                 THEN 'SUBDIRECTOR'                
            -- Gerentes
            WHEN dc."Puesto" ILIKE '%gerente%' OR 
                 dc."Puesto" ILIKE '%management%' OR 
                 dc."Puesto" ILIKE '%mgr%' OR 
                 dc."Puesto" ILIKE '%superintendente%' OR 
                 dc."Puesto" ILIKE '%superintendent%' OR 
                 dc."Puesto" ILIKE '%contralor%' OR
                 dc."Puesto" ILIKE '%manager%' 
                 THEN 'GERENTE'
            -- Subgerentes
            WHEN dc."Puesto" ILIKE '%subgerente%' OR 
                 dc."Puesto" ILIKE '%assistant manager%' 
                 THEN 'SUBGERENTE'
            -- Auditores
            WHEN dc."Puesto" ILIKE '%auditor%' OR
                 dc."Puesto" ILIKE '%auditoria%' 
                  THEN 'AUDITOR'
            -- Ingenieros
            WHEN dc."Puesto" ILIKE '%ingeniero%' OR 
                 dc."Puesto" ILIKE '%engineer%' OR
                 dc."Puesto" ILIKE '%ing%' OR
                 dc."Puesto" ILIKE '%enginner%' OR
                 dc."Puesto" ILIKE '%residente de obra%' OR
                 dc."Puesto" ILIKE '%ingenieria%' 
                 THEN 'INGENIERO'
            -- Jefes
            WHEN dc."Puesto" ILIKE '%jefe%' OR 
                 dc."Puesto" ILIKE '%chief%' OR
                 dc."Puesto" ILIKE 'jefa%' OR
                 dc."Puesto" ILIKE '%boss%' 
                 THEN 'JEFE'
            -- Coordinadores
            WHEN dc."Puesto" ILIKE '%coordinador%' OR
                 dc."Puesto" ILIKE '%coord%' OR
                 dc."Puesto" ILIKE '%cordinator%' OR
                 dc."Puesto" ILIKE '%cooerdinador%' OR
                 dc."Puesto" ILIKE '%cordinador%' OR
                 dc."Puesto" ILIKE '%coodinador%' 
                 THEN 'COORDINADOR'
            -- Líderes
            WHEN dc."Puesto" ILIKE '%líder%' OR 
                 dc."Puesto" ILIKE '%lider%' OR
                 dc."Puesto" ILIKE '%lead%' OR
                 dc."Puesto" ILIKE '%leader%' 
                 THEN 'LIDER'
            -- Responsables
            WHEN dc."Puesto" ILIKE '%responsable%' OR
                 dc."Puesto" ILIKE '%encargad%' OR
                 dc."Puesto" ILIKE '%administracion general%' OR
                 dc."Puesto" ILIKE '%contador general%' OR
                 dc."Puesto" ILIKE '%inspector%' OR
                 dc."Puesto" ILIKE '%compliance%' OR
                 dc."Puesto" ILIKE '%planeacion%' OR
                 dc."Puesto" ILIKE '%seguridad%' OR
                 dc."Puesto" ILIKE '%responable%' OR
                 dc."Puesto" ILIKE '%administrador%' OR
                 dc."Puesto" ILIKE '%administrator%' OR
                 dc."Puesto" ILIKE '%respons%' 
                 THEN 'RESPONSABLE'
            -- Supervisores
            WHEN dc."Puesto" ILIKE '%supervisor%' OR 
                 dc."Puesto" ILIKE '%supervisor%' OR
                 dc."Puesto" ILIKE '%expeditador%' OR
                 dc."Puesto" ILIKE '%scheduler%' OR
                 dc."Puesto" ILIKE '%controlador%' 
                 THEN 'SUPERVISOR'
            -- Especialistas
            WHEN dc."Puesto" ILIKE '%especialista%' OR 
                 dc."Puesto" ILIKE '%control%' OR
                 dc."Puesto" ILIKE '%supply%' OR 
                 dc."Puesto" ILIKE '%specialist%' OR
                 dc."Puesto" ILIKE '%optimizacion%' OR
                 dc."Puesto" ILIKE '%programador%' OR
                 dc."Puesto" ILIKE '%valuadora%' OR
                 dc."Puesto" ILIKE '%operacion%' OR
                 dc."Puesto" ILIKE '%expert%' OR
                 dc."Puesto" ILIKE '%cajero%' OR
                 dc."Puesto" ILIKE '%almacen%' OR
                 dc."Puesto" ILIKE '%gestion%' OR
                 dc."Puesto" ILIKE '%operative%' OR
                 dc."Puesto" ILIKE '%contador%' OR
                 dc."Puesto" ILIKE '%consultor%' OR
                 dc."Puesto" ILIKE '%tecnico%' OR
                 dc."Puesto" ILIKE '%consultant%' OR
                 dc."Puesto" ILIKE '%technician%' OR
                 dc."Puesto" ILIKE '%trade%' OR
                 dc."Puesto" ILIKE '%technical%' OR
                 dc."Puesto" ILIKE '%capacitacion%' OR
                 dc."Puesto" ILIKE '%assurance%' OR
                 dc."Puesto" ILIKE '%insights%' OR
                 dc."Puesto" ILIKE '%logist%' OR
                 dc."Puesto" ILIKE '%negociador%' OR
                 dc."Puesto" ILIKE '%facilitador%' OR
                 dc."Puesto" ILIKE '%planner%' OR
                 dc."Puesto" ILIKE '%planeador%' OR
                 dc."Puesto" ILIKE '%compras%' OR
                 dc."Puesto" ILIKE '%buyer%' OR
                 dc."Puesto" ILIKE '%docente%' OR
                 dc."Puesto" ILIKE '%generalist%' OR
                 dc."Puesto" ILIKE '%mecanico%' OR
                 dc."Puesto" ILIKE '%Advanced%' OR
                 dc."Puesto" ILIKE '%traductor%' OR
                 dc."Puesto" ILIKE '%comprador%' OR
                 dc."Puesto" ILIKE '%independiente%' OR 
                 dc."Puesto" ILIKE '%emprendedor%' OR 
                 dc."Puesto" ILIKE '%autónomo%' OR
                 dc."Puesto" ILIKE '%autonomo%' OR
                 dc."Puesto" ILIKE '%calidad%' OR
                 dc."Puesto" ILIKE '%independent professional%' OR
                 dc."Puesto" ILIKE '%freelancer%' OR
                 dc."Puesto" ILIKE '%mejora%' OR
                 dc."Puesto" ILIKE '%operador%' OR
                 dc."Puesto" ILIKE '%operaciones%' OR
                 dc."Puesto" ILIKE '%professor%' OR
                 dc."Puesto" ILIKE '%coach%' OR
                 dc."Puesto" ILIKE '%deposito%' OR
                 dc."Puesto" ILIKE '%SAP%' OR
                 dc."Puesto" ILIKE '%especificador%' OR
                 dc."Puesto" ILIKE '%profesor%'
                 THEN 'ESPECIALISTA'
            -- Secretarios
            WHEN dc."Puesto" ILIKE '%secretario%' OR 
                 dc."Puesto" ILIKE '%secretary%' 
                 THEN 'SECRETARIO/A'
            -- Analistas
            WHEN dc."Puesto" ILIKE '%analista%' OR 
                 dc."Puesto" ILIKE '%analyst%' OR
                 dc."Puesto" ILIKE '%business intelligence%' 
                 THEN 'ANALISTA'
            -- Asistentes
            WHEN dc."Puesto" ILIKE '%assistant%' OR 
                 dc."Puesto" ILIKE '%asistente%' OR
                 dc."Puesto" ILIKE '%auxiliar%' OR
                 dc."Puesto" ILIKE '%aux%' OR
                 dc."Puesto" ILIKE '%assitant%' OR
                 dc."Puesto" ILIKE '%assistance%' OR
                 dc."Puesto" ILIKE '%ayudante%' OR
                 dc."Puesto" ILIKE '%administrativo%' OR
                 dc."Puesto" ILIKE '%soporte%' OR
                 dc."Puesto" ILIKE '%Almacenista%' OR
                 dc."Puesto" ILIKE '%Almacén de herramientas%' OR
                 dc."Puesto" ILIKE '%practicas%' OR
                 dc."Puesto" ILIKE '%practicante%' OR
                 dc."Puesto" ILIKE '%apoyo%' 
                 THEN 'ASISTENTE'
            -- Representantes
            WHEN dc."Puesto" ILIKE '%sales representative%' OR
                 dc."Puesto" ILIKE '%representante%' OR
                 dc."Puesto" ILIKE '%assesor%' OR
                 dc."Puesto" ILIKE '%atencion al cliente%' OR
                 dc."Puesto" ILIKE '%impulsador%' OR
                 dc."Puesto" ILIKE '%vendedor%' OR
                 dc."Puesto" ILIKE '%ejecutiv%' OR
                 dc."Puesto" ILIKE '%asesor%' OR
                 dc."Puesto" ILIKE '%asesor%' OR
                 dc."Puesto" ILIKE '%customer%' OR
                 dc."Puesto" ILIKE '%servicio%' OR
                 dc."Puesto" ILIKE '%agente%' 
                 THEN 'REPRESENTANTE'
            ELSE 'OTRA'
        END AS Area
        FROM data_country_code AS dc """).df()

    
    data_final = conn.execute("""
        SELECT dc.Nombre ,dc.Correo, dc."País" ,dc."Código país" ,dc."Teléfono" ,dc.Puesto AS "Puesto de trabajo", da.area
        FROM data_country_code AS dc
        INNER JOIN data_area AS da ON da.Correo = dc.Correo
    """).df()
    

    conn.close()

    data_final.to_excel(f'{parent_path}/Datos - homologados.xlsx', index=False)



if __name__ == "__main__":
    datos_homologados()
