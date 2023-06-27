import sqlite3
import hashlib

# Conectarse a la base de datos (creará un nuevo archivo si no existe)
conn = sqlite3.connect('uwudatabase.db')

# Crear un cursor
cursor = conn.cursor()

# Crear la tabla 'users' (si no existe)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        password TEXT NOT NULL,
        last_connection TEXT,
        name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        birthdate TEXT NOT NULL,
        dni TEXT NOT NULL
    )
''')

# Insertar usuarios en la tabla 'users'
users_data = [
    ('usuario1', hashlib.md5('contraseña1'.encode()).hexdigest(),
     None, 'Manda', 'Rina', '1990-01-01', '123456789'),
    ('usuario2', hashlib.md5('contraseña2'.encode()).hexdigest(),
     None, 'Manza', 'Nita', '1995-05-10', '987654321'),
    ('usuario3', hashlib.md5('contraseña3'.encode()).hexdigest(),
     None, 'San', 'Dia', '1985-11-15', '456789123')
]

cursor.executemany('''
    INSERT INTO users (user, password, last_connection, name, last_name, birthdate, dni)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', users_data)

# Guardar los cambios en la tabla 'users'
conn.commit()

# Crear las tablas 'tasks' para cada usuario
users = cursor.execute('SELECT id FROM users').fetchall()
for user in users:
    user_id = user[0]
    task_table_name = 'tasks_{}'.format(user_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS {} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            state TEXT NOT NULL,
            date_created TEXT NOT NULL,
            date_updated TEXT DEFAULT NULL
        )
    '''.format(task_table_name))

# Guardar los cambios en las tablas 'tasks'
conn.commit()

# Cerrar la conexión
conn.close()

print("La base de datos ha sido inicializada correctamente.")
