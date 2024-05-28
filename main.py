import pyodbc
import random
import time
from faker import Faker

# conexión base de datos
server = "DESKTOP-9345VIR"
database = "Northwind"
username = "Py"
password = "123"

connection_string = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
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

# Crear la tabla TestTable si no existe
comandos.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'TestTable')
    BEGIN
        CREATE TABLE TestTable (
            Id INT IDENTITY(1,1) PRIMARY KEY,
            Name NVARCHAR(100),
            Age INT,
            Salary DECIMAL(18,2),
            CreateDate DATETIME
        )
    END
''')
conexion.commit()

# Generador de datos
fake = Faker()

# Inserción de datos
tiempo_inicio = time.time()
while time.time() - tiempo_inicio < 10:
    for i in range(1000):  # Insertar lotes de 1000 registros
        name = fake.name()
        age = random.randint(18, 78)
        salary = round(random.uniform(30000, 150000), 2)
        create_date = fake.date_time_this_year()

        comandos.execute('''
            INSERT INTO TestTable (Name, Age, Salary, CreateDate)
            VALUES (?, ?, ?, ?)
        ''', (name, age, salary, create_date))
        conexion.commit()  # Cometer cada inserción aquí

# Actualizar el 30 % de los registros
total_registros = comandos.execute('SELECT COUNT(*) FROM TestTable').fetchone()[0]
registros_update = int(total_registros * 0.3)
comandos.execute('''
    UPDATE TestTable
    SET Salary = Salary * 1.1
    WHERE Id IN (SELECT TOP (?) Id FROM TestTable ORDER BY NEWID())
''', (registros_update,))
conexion.commit()

# Eliminar registros
registros_delete = int(total_registros * 0.5)
comandos.execute('''
    DELETE FROM TestTable
    WHERE Id IN (SELECT TOP (?) Id FROM TestTable ORDER BY NEWID())
''', (registros_delete,))
conexion.commit()

# Cerrar el cursor y la conexión
comandos.close()
conexion.close()
