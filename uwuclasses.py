import sqlite3
from datetime import datetime
from fastapi import HTTPException
import requests
import hashlib
from requests.exceptions import RequestException
from tkinter import *
from tkinter import messagebox, ttk


class ApiManager():
    def __init__(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        # Inicialización de la clase ApiManager con un cursor y una conexión a la base de datos SQLite
        self.cursor = cursor
        self.conn = conn

    def authentication(self, user_data: dict):
        # Autenticación de usuario
        username = user_data.get('username')
        password = user_data.get('password')

        # Verificar si el usuario y la contraseña coinciden en la base de datos
        self.cursor.execute(
            "SELECT * FROM users WHERE user = ? AND password = ?", (username, password))
        user = self.cursor.fetchone()

        if user is None:
            # Si no se encuentra el usuario en la base de datos, se lanza una excepción HTTP
            raise HTTPException(
                status_code=401, detail="Autenticacion fallida")

        # Actualizar la última conexión del usuario en la base de datos
        last_connection = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        self.cursor.execute(
            "UPDATE users SET last_connection = ? WHERE id = ?", (last_connection, user[0]))
        self.conn.commit()

        # Devolver los datos del usuario autenticado en un diccionario
        user_dict = {
            "id": user[0],
            "last_connection": user[3],
            "name": user[4],
            "last_name": user[5],
            "birthdate": user[6],
            "dni": user[7]
        }
        return user_dict

    def add_task(self, task_data: dict):
        # Agregar una tarea a la base de datos
        user_id = task_data.get('user_id')
        title = task_data.get('title')
        description = task_data.get('description')

        # Obtener el nombre de la tabla de tareas correspondiente al usuario
        table_name = f"tasks_{user_id}"

        # Obtener la fecha y hora actual
        current_datetime = datetime.now().strftime("%d/%m/%y %H:%M:%S")

        # Insertar la tarea en la tabla correspondiente
        try:
            self.cursor.execute(
                f"INSERT INTO {table_name} (title, description, state, date_created, date_updated) VALUES (?, ?, ?, ?, ?)",
                (title, description, 'Programada', current_datetime, None)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            # Si ocurre un error al agregar la tarea, se lanza una excepción HTTP
            raise HTTPException(
                status_code=500, detail="Error al agregar la tarea") from e

    def search_task(self, task_id: dict):
        # Buscar una tarea en la base de datos
        user_id = task_id.get('user_id')
        task_id = task_id.get('task_id')

        # Obtener el nombre de la tabla de tareas correspondiente al usuario
        table_name = f"tasks_{user_id}"

        # Realizar la búsqueda de la tarea en la tabla correspondiente
        self.cursor.execute(
            f"SELECT * FROM {table_name} WHERE id = ?", (task_id,))
        task = self.cursor.fetchone()

        if task is None:
            # Si no se encuentra la tarea en la base de datos, se lanza una excepción HTTP
            raise HTTPException(status_code=404, detail="Tarea no encontrada")

        # Devolver los datos de la tarea en un diccionario
        task_dict = {
            "id": task[0],
            "title": task[1],
            "description": task[2],
            "state": task[3],
            "date_created": task[4],
            "date_updated": task[5]
        }
        return task_dict

    def delete_task(self, task_id: dict):
        # Eliminar una tarea de la base de datos
        user_id = task_id.get('user_id')
        task_id = task_id.get('task_id')

        # Obtener el nombre de la tabla de tareas correspondiente al usuario
        table_name = f"tasks_{user_id}"

        # Verificar si la tarea existe en la tabla del usuario
        self.cursor.execute(
            f"SELECT * FROM {table_name} WHERE id = ?", (task_id,)
        )
        task = self.cursor.fetchone()

        if task is None:
            # Si la tarea no existe en la base de datos, se lanza una excepción HTTP
            raise HTTPException(
                status_code=404, detail="La tarea no existe"
            )

        # Eliminar la tarea de la tabla del usuario
        try:
            self.cursor.execute(
                f"DELETE FROM {table_name} WHERE id = ?", (task_id,)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            # Si ocurre un error al eliminar la tarea, se lanza una excepción HTTP
            raise HTTPException(
                status_code=500, detail="Error al eliminar la tarea") from e

    def update_state(self, task_data: dict):
        # Actualizar el estado de una tarea en la base de datos
        user_id = task_data.get('user_id')
        task_id = task_data.get('task_id')
        state = task_data.get('state')

        # Obtener el nombre de la tabla de tareas correspondiente al usuario
        table_name = f"tasks_{user_id}"

        # Verificar si la tarea existe antes de actualizar
        try:
            self.cursor.execute(
                f"SELECT id FROM {table_name} WHERE id = ?", (task_id,))
            result = self.cursor.fetchone()
            if not result:
                # La tarea no se encontró en la base de datos
                raise HTTPException(
                    status_code=404, detail="Tarea no encontrada")

            # Obtener la fecha y hora actual
            current_datetime = datetime.now().strftime("%d/%m/%y %H:%M:%S")

            # Actualizar el estado y la fecha de actualización de la tarea
            try:
                self.cursor.execute(
                    f"UPDATE {table_name} SET state = ?, date_updated = ? WHERE id = ?",
                    (state, current_datetime, task_id)
                )
                self.conn.commit()
                return True
            except sqlite3.Error as e:
                # Si ocurre un error al actualizar el estado de la tarea, se lanza una excepción HTTP
                raise HTTPException(
                    status_code=500, detail="Error al actualizar el estado de la tarea") from e

        except sqlite3.Error as e:
            # Si ocurre un error al buscar la tarea en la base de datos, se lanza una excepción HTTP
            raise HTTPException(
                status_code=500, detail="Error al buscar la tarea en la base de datos") from e

    def get_tasks(self, user_id: int):
        # Obtener todas las tareas de un usuario de la base de datos
        user_id = str(user_id)
        table_name = f"tasks_{user_id}"
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            tasks = self.cursor.fetchall()
        except sqlite3.Error as e:
            # Si ocurre un error al obtener las tareas, se lanza una excepción HTTP
            raise HTTPException(
                status_code=500, detail="Error al obtener las tareas") from e

        tasks_list = []
        for task in tasks:
            task_dict = {
                "id": task[0],
                "title": task[1],
                "description": task[2],
                "state": task[3],
                "date_created": task[4],
                "date_updated": task[5]
            }
            tasks_list.append(task_dict)

        return tasks_list


class TaskManager():
    def __init__(self):
        self.path = 'http://127.0.0.1:8000/'
        self.data_user = None

    def authentication(self, user: str, password: str):
        # Se hashean los datos de usuario y contraseña utilizando MD5
        hpassword = hashlib.md5(password.encode()).hexdigest()
        body = {
            'username': user,
            'password': hpassword
        }

        try:
            # Se envía una solicitud POST al endpoint de autenticación
            response = requests.post(f'{self.path}authentication/', json=body)
            response.raise_for_status()
            response_data = response.json()
            if 'id' in response_data:
                # Si la autenticación es exitosa, se guarda la información del usuario
                self.data_user = User(response_data['id'], response_data['name'], response_data['last_name'],
                                      response_data['birthdate'], response_data['dni'], hpassword, response_data['last_connection'], response_data['access_token'])
                return True
            else:
                return False
        except requests.RequestException as e:
            return False

    def update_state(self, task_id: str, new_state: str):
        body = {
            "user_id": self.data_user.id,
            "task_id": task_id,
            "state": new_state
        }

        try:
            # Se envía una solicitud POST para actualizar el estado de la tarea
            headers = {"Authorization": f"Bearer {self.data_user.access_token}"}
            response = requests.post(
                f'{self.path}update/', json=body, headers=headers)
            response.raise_for_status()

            # Verificar si la respuesta indica que se actualizó correctamente la tarea
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.RequestException as e:
            return False

    def add_task(self, title: str, description: str):
        body = {
            "user_id": self.data_user.id,
            "title": title,
            "description": description
        }

        try:
            # Se envía una solicitud POST para agregar una nueva tarea
            headers = {"Authorization": f"Bearer {self.data_user.access_token}"}
            response = requests.post(
                f'{self.path}addtask/', json=body, headers=headers)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            return False

    def search(self, task_id: str):
        body = {
            "user_id": self.data_user.id,
            "task_id": task_id,
        }

        try:
            # Se envía una solicitud POST para buscar una tarea específica
            headers = {"Authorization": f"Bearer {self.data_user.access_token}"}
            response = requests.post(
                f'{self.path}search/', json=body, headers=headers)
            response.raise_for_status()
            data_task = response.json()
            return Task(data_task['id'], data_task['title'], data_task['description'], data_task['state'], data_task['date_created'], data_task['date_updated'])
        except requests.RequestException as e:
            return False

    def delete(self, task_id: str):
        body = {
            "user_id": self.data_user.id,
            "task_id": task_id,
        }

        try:
            # Se envía una solicitud POST para eliminar una tarea
            headers = {"Authorization": f"Bearer {self.data_user.access_token}"}
            response = requests.post(
                f'{self.path}delete/', json=body, headers=headers)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            return False

    def tasks(self):
        params = {
            "user_id": self.data_user.id
        }

        try:
            # Se envía una solicitud GET para obtener todas las tareas del usuario
            headers = {"Authorization": f"Bearer {self.data_user.access_token}"}
            response = requests.get(
                f'{self.path}tasks/', params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return False

    def logout(self):
        self.data_user = None


class Person:
    def __init__(self, id, name, last_name, birthdate, dni):
        # Constructor de la clase Person que recibe los datos de la persona
        self.id = id  # ID de la persona
        self.name = name  # Nombre de la persona
        self.last_name = last_name  # Apellido de la persona
        self.birthdate = birthdate  # Fecha de nacimiento de la persona
        self.dni = dni  # DNI (Documento Nacional de Identidad) de la persona


class User(Person):
    def __init__(self, id, name, last_name, birthdate, dni, hpassword, last_connection, access_token):
        # Constructor de la clase User que hereda de la clase Person
        super().__init__(id, name, last_name, birthdate, dni)
        self.hpassword = hpassword  # Contraseña de usuario en formato de hash
        self.last_connection = last_connection  # Última conexión del usuario
        self.access_token = access_token


class Task():
    def __init__(self, id: str, title: str, description: str, state: str, date_created: str, date_updated: str):
        # Constructor de la clase Task
        self.id = id  # ID de la tarea
        self.title = title  # Título de la tarea
        self.description = description  # Descripción de la tarea
        self.state = state  # Estado de la tarea
        self.date_created = date_created  # Fecha de creación de la tarea
        self.date_updated = date_updated  # Fecha de actualización de la tarea


class Client():
    def __init__(self, window: Tk):
        # Inicializa una instancia de la clase TaskManager
        self.manager: TaskManager = TaskManager()
        # Guarda una referencia a la ventana principal de la aplicación
        self.window: Tk = window
        # Almacena el frame actual que se muestra en la ventana
        self.current_frame: Frame = None

    def show_frame_login(self):
        # Definir la función de inicio de sesión
        def login():
            # Obtener el nombre de usuario y la contraseña ingresados
            username = entry_user.get()
            password = entry_password.get()

            # Verificar las credenciales del usuario utilizando el método 'authentication' del objeto 'self.manager'
            if self.manager.authentication(username, password) != False:
                # Si la autenticación es exitosa, mostrar la pantalla de inicio
                self.show_frame_home()
            else:
                # Si la autenticación falla, mostrar un mensaje de error
                messagebox.showerror(
                    "Error de inicio de sesión", "No se pudo iniciar sesión. Verifica tus credenciales.")

        # Si hay un marco actual, eliminarlo y destruirlo
        if self.current_frame is not None:
            self.current_frame.pack_forget()
            self.current_frame.destroy()

        # Crear un nuevo marco para la pantalla de inicio de sesión
        frame_login = Frame()

        # Etiqueta y campo de entrada para el nombre de usuario
        label_user = Label(frame_login, text="Usuario", font=("Arial", 16))
        label_user.pack()
        entry_user = Entry(frame_login,)
        entry_user.pack(pady=10)

        # Etiqueta y campo de entrada para la contraseña
        label_password = Label(
            frame_login, text="Contraseña", font=("Arial", 16,))
        label_password.pack()
        entry_password = Entry(frame_login, show="*")
        entry_password.pack(pady=10)

        # Botón de inicio de sesión que llama a la función 'login'
        button_login = Button(
            frame_login, text="Iniciar Sesión", command=lambda: login(), width=15)
        button_login.pack(side="left", padx=5, pady=20)

        # Empaquetar el marco de inicio de sesión en la ventana
        frame_login.pack(expand=True, anchor="center")

        # Establecer el marco actual como el marco de inicio de sesión
        self.current_frame = frame_login

    def show_frame_home(self):
        # Función para cerrar sesión
        def logout():
            self.manager.logout()
            self.show_frame_login()

        # Si hay un marco actual, eliminarlo y destruirlo
        if self.current_frame != None:
            self.current_frame.pack_forget()
            self.current_frame.destroy()

        # Crear un nuevo marco para la pantalla de inicio
        frame_home = Frame()

        # Etiqueta con el nombre completo del usuario obtenido del objeto 'self.manager.data_user'
        label_fullname = Label(
            frame_home, text=f'{self.manager.data_user.name} {self.manager.data_user.last_name}', font=("Arial", 24))
        label_fullname.pack()

        # Etiqueta con el número de DNI del usuario obtenido del objeto 'self.manager.data_user'
        label_dni = Label(
            frame_home, text=f'DNI: {self.manager.data_user.dni}', font=("Arial", 20))
        label_dni.pack()

        # Etiqueta con la fecha de nacimiento del usuario obtenida del objeto 'self.manager.data_user'
        label_birthdate = Label(
            frame_home, text=f'Fecha de nacimiento: {self.manager.data_user.birthdate}', font=("Arial", 20))
        label_birthdate.pack()

        # Botones para realizar diferentes acciones en la aplicación
        button_add_task = Button(frame_home, text="Agregar tarea",
                                 width=15, command=lambda: self.show_frame_addtask())
        button_add_task.pack(side="left", padx=5, pady=20)

        button_view_tasks = Button(
            frame_home, text="Tareas", width=15, command=lambda: self.show_frame_tasks())
        button_view_tasks.pack(side="left", padx=5, pady=20)

        button_logout = Button(
            frame_home, text="Cerrar sesión", width=15, command=lambda: logout())
        button_logout.pack(side="left", padx=5, pady=20)

        # Empaquetar el marco de inicio en la ventana
        frame_home.pack(expand=True, anchor="center")

        # Establecer el marco actual como el marco de inicio
        self.current_frame = frame_home

    def show_frame_addtask(self):
        # Función para agregar una tarea
        def add_task(title: str, description: str):
            # Verificar si los campos están vacíos
            if title == '' or description == '':
                # Mostrar un mensaje de error si los campos están incompletos
                messagebox.showerror('Campos incompletos',
                                     'Debe completar todos los campos')
                return
            else:
                # Llamar al método add_task del objeto 'self.manager' para agregar la tarea
                if self.manager.add_task(title, description) == True:
                    # Mostrar mensaje de éxito si la tarea se agrega correctamente
                    messagebox.showinfo(
                        'Tarea agregada', 'Tarea agregada correctamente')
                else:
                    # Mostrar mensaje de error si la tarea no se puede agregar
                    messagebox.showerror(
                        'Tarea no agregada', 'La tarea no pudo ser agregada')

                # Mostrar el marco de inicio después de agregar la tarea
                self.show_frame_home()

        # Si hay un marco actual, eliminarlo y destruirlo
        if self.current_frame != None:
            self.current_frame.pack_forget()
            self.current_frame.destroy()

        # Crear un nuevo marco para la pantalla de agregar tarea
        frame_addtask = Frame()

        # Etiqueta para el título del marco
        label_frame = Label(
            frame_addtask, text='Nueva tarea', font=("Arial", 24))
        label_frame.pack(pady=20)

        # Etiqueta y campo de entrada para el título de la tarea
        label_title = Label(frame_addtask, text='Titulo', font=("Arial", 16))
        label_title.pack()

        entry_title = Entry(frame_addtask)
        entry_title.pack()

        # Etiqueta y campo de entrada para la descripción de la tarea
        label_description = Label(
            frame_addtask, text='Descripcion', font=("Arial", 16))
        label_description.pack()

        entry_description = Text(frame_addtask, width=50, height=20)
        entry_description.pack()

        # Botón para agregar la tarea
        button_add_task = Button(frame_addtask, text="Agregar tarea", width=15, command=lambda: add_task(
            entry_title.get(), entry_description.get("1.0", "end-1c")))
        button_add_task.pack(side="left", padx=5, pady=20)

        # Botón para cancelar y mostrar el marco de inicio
        button_cancel = Button(frame_addtask, text="Cancelar",
                               width=15, command=lambda: self.show_frame_home())
        button_cancel.pack(side="left", padx=5, pady=20)

        # Empaquetar el marco de agregar tarea en la ventana
        frame_addtask.pack(expand=True, anchor="center")

        # Establecer el marco actual como el marco de agregar tarea
        self.current_frame = frame_addtask

    def show_frame_tasks(self):
        # Verificar si hay un marco actual y eliminarlo
        if self.current_frame is not None:
            self.current_frame.pack_forget()
            self.current_frame.destroy()

        # Crear un nuevo marco para mostrar las tareas
        frame_tasks = Frame()

        label_title = Label(frame_tasks, text="Tareas", font=("Arial", 24))
        label_title.pack()

        # Obtener las tareas desde el gestor
        data_tasks = self.manager.tasks()

        # Verificar si no hay tareas o si ocurrió un error al obtener las tareas
        if data_tasks is None or len(data_tasks) == 0:
            label_no_data = Label(
                frame_tasks, text='No hay tareas', font=("Arial", 20))
            label_no_data.pack()
        elif data_tasks == False:
            messagebox.showerror('Error', 'No se pudieron obtener las tareas')
        else:
            # Crear una tabla para mostrar las tareas
            table = ttk.Treeview(frame_tasks, columns=(
                "ID", "Título", "Descripción", "Estado", "Fecha de Creación", "Fecha de Actualización"))
            table.heading("ID", text="ID")
            table.heading("Título", text="Título")
            table.heading("Descripción", text="Descripción")
            table.heading("Estado", text="Estado")
            table.heading("Fecha de Creación", text="Fecha de Creación")
            table.heading("Fecha de Actualización",
                          text="Fecha de Actualización")

            # Agregar cada tarea a la tabla
            for task in data_tasks:
                task_id = task['id']
                title = task['title']
                description = task['description']
                state = task['state']
                date_created = task['date_created']
                date_updated = task['date_updated']

                table.insert("", "end", values=(task_id, title,
                                                description, state, date_created, date_updated))

            table.pack(padx=10, pady=10)

        # Botón para cancelar y volver al marco de inicio
        button_cancel = Button(frame_tasks, text="Volver",
                               width=15, command=lambda: self.show_frame_home())
        button_cancel.pack(padx=5, pady=20)

        # Empaquetar el marco de tareas en la ventana
        frame_tasks.pack(expand=True, anchor="center")

        # Establecer el marco actual como el marco de tareas
        self.current_frame = frame_tasks
