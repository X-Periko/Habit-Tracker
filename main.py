import Habito
import os

def clear():
    for x in range(0,1000):
        print("")
lista_habitos = []

with open("data.txt", "r", encoding="utf-8") as file:
        for numero_linea, linea in enumerate(file, start=1):
            linea_lista = linea.split(" ")
            nombre = linea_lista[0]
            frecuencia = linea_lista[1]
            duración = linea_lista[2]
            id = numero_linea
            habito = Habito.Habito(nombre=nombre, duración=duración, frecuencia=frecuencia, id=id)
            lista_habitos.append(habito)

usr_input = input(">")
while usr_input != "q":
    clear()
    print("Qué desea hacer? \n\nc - Crear un hábito\ne - Eliminar un hábito\nq - Salir\n")
    for pos, habito in enumerate(lista_habitos, start = 0):
        print(f"{pos} - {habito.nombre}")

    usr_input = input("> ")
    if usr_input == "c":
        nombre = input("Qué hábito quiere adquirir?: ")
        frecuencia = input("Con que frecuencia desea hacerlo? (diario, semanal, mensual): ")
        duración = input("Durante cuánto tiempo desea hacerlo? (duración en minutos): ")
        id = len(lista_habitos) +1
        habito = Habito.Habito(nombre=nombre, frecuencia=frecuencia, duración=duración, id=id)
        lista_habitos.append(habito)

    elif usr_input == "e":
        id = int(input("Introduzca el ID del hábito a eliminar: "))
        del lista_habitos[id-1]

    elif usr_input == "q":
        with open("data.txt", "w", encoding="utf-8") as file:    
            for habito in lista_habitos:
                file.write(f"{habito.nombre} {habito.frecuencia} {habito.duración}")
            file.write("")

    else:
        try:
            habito = lista_habitos[int(usr_input)]
            print(habito.imprimir())
            print("Qué desea hacer?: \n\nc - Marcar como cumplido \ne - Editar hábito\nq - Volver al menú")
            usr_input = input("> ")

            if usr_input == "c":
                habito.cumplido = True
                print("Hábito marcado con éxito")

            elif usr_input == "e":
                habito.frecuencia = input("Con qué frecuencia desea realizar este hábito? ")
                habito.duración = "".join(input("Durante cuánto tiempo desea realizar este hábito? "), "\n")
        except:
            print("Por favor, escoja una de las opciones")
            input(" ")