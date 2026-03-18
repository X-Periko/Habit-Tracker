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
    for habito in lista_habitos:
        print(f"{habito.nombre} {habito.duración} {habito.frecuencia}")
    
    usr_input = input("> ")
    if usr_input == "c":
        nombre = input("Qué hábito quiere adquirir?: ")
        frecuencia = input("Con que frecuencia desea hacerlo? (diario, semanal, mensual): ")
        duración = input("Durante cuánto tiempo desea hacerlo? (duración en minutos): ")
        id = len(lista_habitos) +1
        habito = Habito.Habito(nombre=nombre, frecuencia=frecuencia, duración=duración, id=id)
        lista_habitos.append(habito)

    elif usr_input == "d":
        nombre = input("Qué hábito desea eliminar? ")
        for x in lista_habitos:
            if x.nombre == nombre:
                numero_linea = lista_habitos.index(x)
                del x
        habito = Habito.Habito(nombre=nombre, duración=None, frecuencia=None, id = numero_linea)
        habito.eliminar_habito()

    elif usr_input == "q":
        with open("data.txt", "w", encoding="utf-8") as file:    
            for habito in lista_habitos:
                file.write(f"{habito.nombre} {habito.duración} {habito.frecuencia}")

    else:
        print(lista_habitos[int(usr_input)].imprimir())
        input(" ")