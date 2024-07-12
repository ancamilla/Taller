import mysql.connector
from mysql.connector import Error

# Datos de conexión
user = 'AAncamilla'
password = 'manchester12,'
host = 'yury.mysql.database.azure.com'
port = 3306
database = 'correo_yury'
ssl_ca = ''  # Reemplaza esto con la ruta correcta al certificado CA si es necesario

try:
    # Crear la conexión
    conn = mysql.connector.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database,
        ssl_ca=ssl_ca,
        ssl_disabled=False
    )
    if conn.is_connected():
        print('Conexión exitosa a la base de datos MySQL de Azure')

        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()
        print(f"Conectado a la base de datos: {db_name[0]}")

        cursor.execute("SELECT * FROM usuario;")
        usuario = cursor.fetchall()
        #usuario = cursor.fetchall()
        # Mostrar los resultados
        print("Contenido de la tabla Usuario:")
        for row in usuario:
            print(row)
        print(row[4])
       # print(rows[2][4])
        print(usuario[0][4])
        
        if usuario:
            if usuario[0][4] == 'Trabajador':
                print('trabajador')
            elif usuario[0][4] == 'JefeRRHH':
                print('jefazo')
            elif usuario[4] == 'PersonalRRHH':
                print('perkin')
        else:
            print('ni una wea wena')


        cursor.close()

except Error as e:
    print(f"Error al conectar a MySQL: {e}")

finally:
    if conn.is_connected():
        conn.close()
        print("Conexión cerrada")

