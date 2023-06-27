from tkinter import *
from uwuclasses import Client


def main():
    window = Tk()

    # Establece el estado de la ventana a 'zoomed' para que se maximice al iniciar
    window.state('zoomed')

    # Permite que la ventana pueda ser redimensionada por el usuario
    window.overrideredirect(False)

    # Obtiene el tamaño actual de la ventana
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Asigna el tamaño a la ventana
    window.geometry(f"{window_width}x{window_height}")

    # Establece el título de la ventana
    window.title('Administrador de tareas')

    # Crea una instancia del objeto Client y pasa la ventana como parámetro
    window_manager = Client(window)

    # Muestra el marco de inicio de sesión en la ventana
    window_manager.show_frame_login()

    # Inicia el bucle principal de la aplicación
    window.mainloop()


if __name__ == '__main__':
    main()
