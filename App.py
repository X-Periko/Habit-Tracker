import Habito
import database
from datetime import date

DIAS_LIMITE = {"d": 1, "s": 7, "m": 30}


def clear():
    for x in range(0, 1000):
        print("")


class App:
    def __init__(self):
        database.crear_tablas()
        self.lista_habitos = Habito.Habito.cargar_todos()
        self._resetear_habitos_vencidos()

    def _resetear_habitos_vencidos(self):
        hoy = date.today()
        for habito in self.lista_habitos:
            if not habito.cumplido or not habito.ultima_actualizacion:
                continue
            dias_transcurridos = (hoy - date.fromisoformat(habito.ultima_actualizacion)).days
            limite = DIAS_LIMITE.get(habito.frecuencia, 1)
            if dias_transcurridos >= limite:
                habito.cumplido = False
                habito.guardar()

    def crear_habito(self, nombre, frecuencia, duracion):
        habito = Habito.Habito(nombre=nombre, frecuencia=frecuencia, duracion=duracion, cumplido=False)
        habito.guardar()
        self.lista_habitos.append(habito)

    def mainloop(self):
        usr_input = input(">")
        while usr_input != "q":
            clear()
            print("Qué desea hacer? \n\nc - Crear un hábito\ne - Eliminar un hábito\nq - Salir\n")
            for pos, habito in enumerate(self.lista_habitos, start=0):
                print(f"{pos} - {habito.nombre}")

            usr_input = input("> ")
            if usr_input == "c":
                nombre = input("Qué hábito quiere adquirir?: ")
                frecuencia = input("Con que frecuencia desea hacerlo? (d/s/m): ")
                duracion = int(input("Durante cuánto tiempo desea hacerlo? (minutos): "))
                self.crear_habito(nombre=nombre, frecuencia=frecuencia, duracion=duracion)

            elif usr_input == "e":
                pos = int(input("Introduzca la posición del hábito a eliminar: "))
                try:
                    habito = self.lista_habitos.pop(pos)
                    habito.eliminar()
                except IndexError:
                    print("[!] Ningún hábito coincide con esa posición")
                    input(" ")

            elif usr_input == "q":
                pass 

            else:
                try:
                    habito = self.lista_habitos[int(usr_input)]
                    print(habito.imprimir())
                    print("Qué desea hacer?: \n\nc - Marcar como cumplido \ne - Editar hábito\nq - Volver al menú")
                    accion = input("> ")

                    if accion == "c":
                        habito.marcar_cumplido()
                        print("Hábito marcado con éxito")

                    elif accion == "e":
                        habito.frecuencia = input("Con qué frecuencia desea realizar este hábito? (d/s/m): ")
                        habito.duracion = int(input("Durante cuánto tiempo desea realizar este hábito? (minutos): "))
                        habito.guardar()

                except ValueError:
                    print("Por favor, escoja una de las opciones")
                    input(" ")


app = App()
app.mainloop()