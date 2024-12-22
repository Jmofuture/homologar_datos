from src.clean_data import datos_homologados


def main():
    try:
        datos_homologados()
        print("Archivo de Datos Homologados Creado")
    except Exception as e:
        print("Hubo un error", {e})

if __name__ == "__main__":
    main()