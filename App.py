import Habito
import os
import time as t

def clear():
    for x in range(0,1000):
        print("")
lista_habitos = []
habitos_añadidos = False

class App:
    def __init__(self):
        self.lista_habitos = []
        with open("data.txt", "r", encoding="utf-8") as file:
            for numero_linea, linea in enumerate(file, start=1):
                linea_lista = linea.split(" ")
                nombre = linea_lista[0]
                frecuencia = linea_lista[1]
                duración = linea_lista[2]
                cumplido = linea_lista[3]
                id = numero_linea
                habito = Habito.Habito(nombre=nombre, duración=duración, frecuencia=frecuencia, id=id, cumplido=cumplido)
                self.lista_habitos.append(habito)
        
        with open("time.txt", "r", encoding="utf-8") as time:
            date = t.strftime("%Y-%m-%d")
            sectioned_date = date.split("-")
            save_date = time.read().split("-")
            for habito in self.lista_habitos:
                if habito.cumplido == True:
                    if habito.frecuencia == "d" and save_date[2] < sectioned_date[2] or save_date[1] < sectioned_date[1] or save_date[0] < sectioned_date[0]:
                        habito.cumplido = False
                    if habito.frecuencia == "m" and save_date[1] < sectioned_date[1] or save_date[0] < sectioned_date[0]:
                        habito.cumplido = False
                    if habito.frecuencia == "s" and save_date[2] - sectioned_date[2] == 7:
                        habito.cumplido = False

    def crear_habito(self, nombre, frecuencia, duración):
        id = len(lista_habitos) +1
        habito = Habito.Habito(nombre=nombre, frecuencia=frecuencia, duración=duración, id=id, cumplido = False)
        self.lista_habitos.append(habito)
        global habitos_añadidos
        habitos_añadidos = True

    def guardar(self):
        with open("data.txt", "w", encoding="utf-8") as file:  
                for habito in self.lista_habitos:
                    file.write(f"{habito.nombre} {habito.frecuencia} {habito.duración} {habito.cumplido}")
                if habitos_añadidos:
                    file.write("\n")

        with open("time.txt", "w", encoding="utf-8") as time:
            time.write(str(t.strftime("%Y-%m-%d")))

    def mainloop(self):
        usr_input = input(">")
        while usr_input != "q":
            clear()
            print("Qué desea hacer? \n\nc - Crear un hábito\ne - Eliminar un hábito\nq - Salir\n")
            for pos, habito in enumerate(self.lista_habitos, start = 0):
                print(f"{pos} - {habito.nombre}")

            usr_input = input("> ")
            if usr_input == "c":
                nombre = input("Qué hábito quiere adquirir?: ")
                frecuencia = input("Con que frecuencia desea hacerlo? (diario, semanal, mensual): ")
                duración = input("Durante cuánto tiempo desea hacerlo? (duración en minutos): ")
                self.crear_habito(nombre=nombre, frecuencia=frecuencia, duración=duración)

            elif usr_input == "e":
                id = int(input("Introduzca el ID del hábito a eliminar: "))
                del self.lista_habitos[id]

            elif usr_input == "q":
                self.guardar()
                
            else:
                try:
                    habito = self.lista_habitos[int(usr_input)]
                    print(habito.imprimir())
                    print("Qué desea hacer?: \n\nc - Marcar como cumplido \ne - Editar hábito\nq - Volver al menú")
                    usr_input = input("> ")

                    if usr_input == "c":
                        habito.cumplido = True
                        print("Hábito marcado con éxito")

                    elif usr_input == "e":
                        habito.frecuencia = input("Con qué frecuencia desea realizar este hábito? ")
                        habito.duración = input("Durante cuánto tiempo desea realizar este hábito? ")

                    elif usr_input == "q":
                        usr_input = ""
                        continue
                except ValueError:
                    print("Por favor, escoja una de las opciones")
                    input(" ")          

app = App()  
app.mainloop()