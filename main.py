import pyodbc
import random
import time
from faker import Faker

#conexion base de datos
server = "DESKTOP-9345VIR"
database = "Northwind"
username = ""
password = ""

connection_string = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

# Intentar conectar a la base de datos
try:
    conexion = pyodbc.connect(connection_string)
    comandos = conexion.cursor()
    comandos.execute("SELECT 1")
    result = comandos.fetchone()
    if result:
        print("Conexión exitosa a la base de datos.")
    else:
        print("Conexión fallida a la base de datos.")
except pyodbc.Error as ex:
    print("Error al conectar a la base de datos:")
    print(ex)
finally:
    # Cerrar la conexión si se abrió
    if 'conexion' in locals() and conexion:
        comandos.close()
        conexion.close()

conexion = pyodbc.connect(connection_string)
comandos = conexion.comandos()

#generador de datos
fake = Faker()

#creacion de una nueva tabla
comandos.execute('''
    CREATE TABLE TestTable (
        Id INT PRIMARY KEY,
        Name NVARCHAR(100),
        Age INT,
        Salary DECIMAL(18,2),
        CreateDate DATETIME
    )
'''  
)

conexion.commit()

#insercion de datos
tiempo = time.time()
while time.time() - tiempo < 10:
    for i in range(1000): #inserta lotes de 1000 registros
        id = random.randint(1, 1000000)
        name = fake.name()
        age = random.randint(18, 78)
        salary = round(random.uniform(30000, 150000), 2)
        create_date = fake.date_time_this_year()
        
        comandos.execute('''
            INSERT INTO TestTable (Id, Name, Age, Salary, CreateDate)
            VALUES (?, ?, ?, ?, ?)
        ''', (id, name, age, salary, create_date))
    conexion.commit()
    
#actualizar el 30 % de los registros

total_registros = comandos.execute('SELECT COUNT(*) FROM TestTable').fetchaval()
registros_update = int(total_registros * 0.3)
comandos.execute('''
    UPDATE TestTable
    SET Salary = Salary * 1.1
    WHERE Id IN (SELECT TOP (?) Id FROM TestTable ORDER BY NEWID())
''', (registros_update,))  
conexion.commit()

#eliminar registros

registros_delete = int(total_registros * 0.5)
comandos.execute('''
    DELETE FROM TestTable
    WHERE Id IN (SELECT TOP (?) Id FROM TestTable ORDER BY NEWID())
''', (registros_delete,))
conexion.commit()

#eliminacion de tabla
comandos.execute('DROP TABLE TestTable')
conexion.commit()

comandos.close()
conexion.close()