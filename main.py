from Habito import Habito
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit import prompt
import os

def clear():
    for x in range(0,1000):
        print("")
lista_habitos = []
lista_menu = []

def menu_principal():
    return(radiolist_dialog(
        title="Menú principal",
        text="Selecciona una opción:",
        values=lista_menu).run())

usr_input = input(">")
while usr_input != "q":
    clear()
    lista_menu = []
    with open("data.txt", "r", encoding="utf-8") as file:
        for numero_linea, linea in enumerate(file, start=1):
            lista_menu.append((numero_linea, linea))
        lista_menu.append(("crear", "Crear un hábito"))
    usr_input = menu_principal()
    
    if usr_input == "crear":
        nombre = prompt("Qué hábito quiere adquirir?: ")
        frecuencia = prompt("Con que frecuencia desea hacerlo? (duración en minutos, cada día/semana/mes): ")
        Habito1 = Habito(nombre=nombre, frecuencia=frecuencia)
        lista_habitos.append(Habito1)
        globals()[nombre].id = globals()[nombre].asignar_id()
        globals()[nombre].guardar_habito()
    
    else:
        with open("data.txt", "r", encoding="utf-8") as file:
            for numero_linea, linea in enumerate(file, start=1):
                if usr_input == numero_linea:
                    print(linea)
        