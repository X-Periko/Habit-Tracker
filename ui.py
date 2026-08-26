"""
UI Flet del Habit Tracker.
Estética neomorfista mobile-first, ejecutada como app de escritorio nativa.

Ejecutar con:
    source venv/bin/activate
    python ui.py
"""

"""
UI Flet del Habit Tracker.
Estética neomorfista mobile-first, ejecutada como app de escritorio nativa.

Ejecutar con:
    source venv/bin/activate
    python ui.py
"""

# --------------------------------------------------------------------------- #
#  Parche de certificados para macOS + python.org (falla en 3.14 sin
#  Install Certificates.command). Crea un contexto SSL por defecto que
#  apunta al bundle de `certifi` antes de cualquier import que haga red.
# --------------------------------------------------------------------------- #
import ssl
import certifi

_DEFAULT_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = lambda: _DEFAULT_SSL_CONTEXT
# Forzar también el contexto que urllib instala por defecto
try:
    import urllib.request as _ur
    _ur.install_opener(_ur.build_opener(
        _ur.HTTPSHandler(context=_DEFAULT_SSL_CONTEXT)
    ))
except Exception:
    pass

from datetime import date
import flet as ft

import database
import Habito


# --------------------------------------------------------------------------- #
#  Paleta neomorfista (fondo gris-azulado claro, acentos suaves)
# --------------------------------------------------------------------------- #
BG = "#E4E9F2"          # fondo principal (también de las tarjetas)
BG_DEEP = "#D6DCE5"     # tono más oscuro para sombras
BG_LIGHT = "#F2F6FC"    # tono más claro para luces
TEXT_PRIMARY = "#3A4256"
TEXT_SECONDARY = "#7B8499"
ACCENT = "#6C8CFF"      # azul-violeta suave para acciones positivas
ACCENT_DANGER = "#E27D88"  # rosa apagado para borrar


# --------------------------------------------------------------------------- #
#  Helpers de estilo neomorfista
# --------------------------------------------------------------------------- #
def _box_shadow(dark, light, blur=18, offset=6):
    """Devuelve la lista de box_shadows que da el efecto neomorfista."""
    return [
        ft.BoxShadow(spread_radius=0, blur_radius=blur, color=dark,
                     offset=ft.Offset(offset, offset)),
        ft.BoxShadow(spread_radius=0, blur_radius=blur, color=light,
                     offset=ft.Offset(-offset, -offset)),
    ]


def neo_surface(content, *, width=None, height=None, padding=18, radius=22,
                on_click=None):
    """Contenedor que parece 'salido' del fondo (tarjeta / botón elevado)."""
    return ft.Container(
        content=content,
        width=width,
        height=height,
        padding=padding,
        border_radius=ft.BorderRadius(radius, radius, radius, radius),
        bgcolor=BG,
        shadow=_box_shadow(BG_DEEP, BG_LIGHT),
        ink=on_click is not None,           # ripple si es clickable
        on_click=on_click,
        animate_scale=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
    )


def neo_inset(content, *, width=None, height=None, padding=14, radius=18):
    """Contenedor que parece 'hundido' (inputs, áreas de selección)."""
    return ft.Container(
        content=content,
        width=width,
        height=height,
        padding=padding,
        border_radius=ft.BorderRadius(radius, radius, radius, radius),
        bgcolor=BG,
        shadow=_box_shadow(BG_LIGHT, BG_DEEP, blur=10, offset=4,
                           ),  # nota: orden invertido en runtime
        # Flet no permite invertir offsets nativamente sin trucos; usamos gradiente sutil:
        gradient=ft.RadialGradient(
            colors=[BG_LIGHT, BG, BG_DEEP],
            radius=160,
        ),
    )


def neo_textfield(label, *, value="", hint="", password=False,
                  keyboard_type=ft.KeyboardType.TEXT, width=240):
    """TextField con look neomorfista hundido."""
    return ft.Container(
        width=width,
        padding=4,
        border_radius=ft.BorderRadius(16, 16, 16, 16),
        bgcolor=BG,
        shadow=_box_shadow(BG_LIGHT, BG_DEEP, blur=8, offset=3),
        content=ft.TextField(
            label=label,
            value=value,
            hint_text=hint,
            password=password,
            can_reveal_password=password,
            keyboard_type=keyboard_type,
            border=ft.InputBorder.NONE,
            filled=True,
            fill_color=BG,
            color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=TEXT_SECONDARY, size=12),
            text_size=14,
            cursor_color=ACCENT,
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        ),
    )


def neo_button(label, *, on_click, icon=None, primary=True, width=None):
    """Botón elevado estilo neomorfista."""
    color = ACCENT if primary else TEXT_SECONDARY
    return neo_surface(
        ft.Row(
            controls=[
                ft.Icon(icon, color=color, size=18) if icon else ft.Container(),
                ft.Text(label, color=color, size=14, weight=ft.FontWeight.W_600),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            tight=True,
        ),
        width=width,
        height=44,
        padding=ft.Padding.symmetric(horizontal=18, vertical=10),
        radius=18,
        on_click=on_click,
    )


# --------------------------------------------------------------------------- #
#  Lógica de dominio (idéntica a la versión CLI, encapsulada en métodos UI)
# --------------------------------------------------------------------------- #
DIAS_LIMITE = {"d": 1, "s": 7, "m": 30}


def _resetear_habitos_vencidos(lista):
    hoy = date.today()
    for habito in lista:
        if not habito.cumplido or not habito.ultima_actualizacion:
            continue
        dias = (hoy - date.fromisoformat(habito.ultima_actualizacion)).days
        limite = DIAS_LIMITE.get(habito.frecuencia, 1)
        if dias >= limite:
            habito.cumplido = False
            habito.guardar()


# --------------------------------------------------------------------------- #
#  Aplicación Flet
# --------------------------------------------------------------------------- #
class HabitTrackerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.lista_habitos: list[Habito.Habito] = []

        # --- Configuración de ventana tipo móvil ---
        self.page.title = "Habit Tracker"
        self.page.bgcolor = BG
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window.width = 400
        self.page.window.height = 760
        self.page.window.resizable = True
        self.page.theme = ft.Theme(
            color_scheme_seed=ACCENT,
            scaffold_bgcolor=BG,
        )

        # --- Inicialización de datos ---
        database.crear_tablas()
        self.lista_habitos = Habito.Habito.cargar_todos()
        _resetear_habitos_vencidos(self.lista_habitos)

        # --- Contenedor raíz (cambia entre vistas) ---
        self.body = ft.Container(expand=True, padding=20)
        self.page.add(self.body)
        self._show_main()

    # ------------------------------------------------------------------ #
    #  Navegación
    # ------------------------------------------------------------------ #
    def _show_main(self):
        self.lista_habitos = Habito.Habito.cargar_todos()
        self.body.content = self._build_main_view()
        self.page.update()

    def _show_detail(self, habito: Habito.Habito):
        self.body.content = self._build_detail_view(habito)
        self.page.update()

    # ------------------------------------------------------------------ #
    #  Vista principal
    # ------------------------------------------------------------------ #
    def _build_main_view(self):
        # --- Encabezado ---
        header = ft.Column(
            controls=[
                ft.Text("Mis hábitos",
                        size=26, weight=ft.FontWeight.W_700,
                        color=TEXT_PRIMARY),
                ft.Text("Mantén tu racha día a día",
                        size=13, color=TEXT_SECONDARY),
            ],
            spacing=4,
        )

        # --- Lista de hábitos ---
        if not self.lista_habitos:
            lista = neo_surface(
                ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.ROCKET_LAUNCH_OUTLINED,
                                size=48, color=TEXT_SECONDARY),
                        ft.Text("Aún no tienes hábitos",
                                size=15, weight=ft.FontWeight.W_600,
                                color=TEXT_PRIMARY),
                        ft.Text("Pulsa + para crear el primero",
                                size=12, color=TEXT_SECONDARY),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                padding=30,
            )
        else:
            lista = ft.Column(
                controls=[self._build_habit_card(h) for h in self.lista_habitos],
                spacing=14,
                scroll=ft.ScrollMode.AUTO,
            )

        # --- FAB (botón flotante) para crear ---
        fab = ft.Container(
            width=60, height=60,
            border_radius=ft.BorderRadius(30, 30, 30, 30),
            bgcolor=BG,
            shadow=_box_shadow(BG_DEEP, BG_LIGHT, blur=20, offset=8),
            content=ft.Icon(ft.Icons.ADD, color=ACCENT, size=30),
            ink=True,
            on_click=lambda _: self._open_form_dialog(),
            alignment=ft.Alignment.CENTER,
        )

        return ft.Column(
            controls=[
                header,
                ft.Container(height=18),
                ft.Container(content=lista, expand=True),
                ft.Row(controls=[fab],
                       alignment=ft.MainAxisAlignment.END,
                       vertical_alignment=ft.CrossAxisAlignment.END),
            ],
            expand=True,
        )

    def _build_habit_card(self, habito: Habito.Habito):
        freq_texto = {"d": "Diaria", "s": "Semanal", "m": "Mensual"}.get(
            habito.frecuencia, habito.frecuencia)
        estado_color = ACCENT if habito.cumplido else TEXT_SECONDARY
        estado_texto = "Cumplido ✓" if habito.cumplido else "Pendiente"

        # Indicador circular de estado
        dot = ft.Container(
            width=14, height=14,
            border_radius=ft.BorderRadius(7, 7, 7, 7),
            bgcolor=ACCENT if habito.cumplido else BG_DEEP,
            shadow=_box_shadow(BG_LIGHT, BG_DEEP, blur=6, offset=2)
            if not habito.cumplido else [],
        )

        card_content = ft.Row(
            controls=[
                # Columna izquierda: info
                ft.Column(
                    controls=[
                        ft.Text(habito.nombre,
                                size=16, weight=ft.FontWeight.W_700,
                                color=TEXT_PRIMARY),
                        ft.Row(
                            controls=[
                                dot,
                                ft.Text(f"{freq_texto} · {habito.duracion} min",
                                        size=12, color=TEXT_SECONDARY),
                            ],
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Text(estado_texto, size=11,
                                color=estado_color,
                                weight=ft.FontWeight.W_600),
                    ],
                    spacing=6,
                    expand=True,
                ),
                # Icono papelera
                ft.Container(
                    width=38, height=38,
                    border_radius=ft.BorderRadius(12, 12, 12, 12),
                    bgcolor=BG,
                    shadow=_box_shadow(BG_DEEP, BG_LIGHT, blur=10, offset=3),
                    content=ft.Icon(ft.Icons.DELETE_OUTLINE,
                                    size=18, color=ACCENT_DANGER),
                    ink=True,
                    on_click=lambda _, h=habito: self._open_confirm_delete(h),
                    alignment=ft.Alignment.CENTER,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        )

        return neo_surface(
            card_content,
            padding=16,
            radius=20,
            on_click=lambda _, h=habito: self._show_detail(h),
        )

    # ------------------------------------------------------------------ #
    #  Vista detalle
    # ------------------------------------------------------------------ #
    def _build_detail_view(self, habito: Habito.Habito):
        freq_texto = {"d": "Diaria", "s": "Semanal", "m": "Mensual"}.get(
            habito.frecuencia, habito.frecuencia)
        estado_texto = "Cumplido ✓" if habito.cumplido else "Pendiente"

        # Card con info
        info_card = neo_surface(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_color=TEXT_SECONDARY,
                                on_click=lambda _: self._show_main(),
                            ),
                            ft.Text(habito.nombre,
                                    size=20, weight=ft.FontWeight.W_700,
                                    color=TEXT_PRIMARY),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    ft.Divider(height=20, color=BG_DEEP, thickness=1),
                    _detail_row("Frecuencia", freq_texto),
                    _detail_row("Duración", f"{habito.duracion} minutos"),
                    _detail_row("Estado", estado_texto),
                    _detail_row("Última actualización",
                                habito.ultima_actualizacion or "—"),
                ],
                spacing=12,
            ),
            padding=20,
        )

        # Botones de acción
        actions = ft.Column(
            controls=[
                neo_button(
                    "Marcar como cumplido",
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                    on_click=lambda _, h=habito: self._on_mark_done(h),
                    primary=True,
                    width=260,
                ),
                ft.Container(height=10),
                neo_button(
                    "Editar hábito",
                    icon=ft.Icons.EDIT_OUTLINED,
                    on_click=lambda _, h=habito: self._open_form_dialog(h),
                    primary=False,
                    width=260,
                ),
                ft.Container(height=10),
                neo_button(
                    "Eliminar",
                    icon=ft.Icons.DELETE_OUTLINE,
                    on_click=lambda _, h=habito: self._open_confirm_delete(h),
                    primary=False,
                    width=260,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )

        return ft.Column(
            controls=[
                info_card,
                ft.Container(height=24),
                actions,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    # ------------------------------------------------------------------ #
    #  Diálogos
    # ------------------------------------------------------------------ #
    def _open_form_dialog(self, habito: Habito.Habito | None = None):
        es_edicion = habito is not None
        titulo = "Editar hábito" if es_edicion else "Nuevo hábito"

        # Campos
        nombre_field = ft.TextField(
            label="Nombre", value=habito.nombre if es_edicion else "",
            border=ft.InputBorder.NONE, filled=True, fill_color=BG,
            color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=TEXT_SECONDARY, size=12),
            text_size=14,
        )

        inicial_freq = habito.frecuencia if es_edicion else "d"
        freq_radio = ft.RadioGroup(
            content=ft.Row(
                controls=[
                    ft.Radio(value="d", label="Diaria"),
                    ft.Radio(value="s", label="Semanal"),
                    ft.Radio(value="m", label="Mensual"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            value=inicial_freq,
        )

        duracion_field = ft.TextField(
            label="Duración (minutos)",
            value=str(habito.duracion) if es_edicion else "",
            keyboard_type=ft.KeyboardType.NUMBER,
            border=ft.InputBorder.NONE, filled=True, fill_color=BG,
            color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=TEXT_SECONDARY, size=12),
            text_size=14,
        )

        # Error label
        error_text = ft.Text("", color=ACCENT_DANGER, size=12)

        def guardar(_):
            nombre = nombre_field.value.strip()
            try:
                duracion = int(duracion_field.value)
                if duracion <= 0:
                    raise ValueError
            except ValueError:
                error_text.value = "La duración debe ser un entero positivo"
                self.page.update()
                return
            if not nombre:
                error_text.value = "El nombre no puede estar vacío"
                self.page.update()
                return
            if es_edicion:
                habito.nombre = nombre
                habito.frecuencia = freq_radio.value
                habito.duracion = duracion
                habito.guardar()
            else:
                nuevo = Habito.Habito(
                    nombre=nombre,
                    frecuencia=freq_radio.value,
                    duracion=duracion,
                    cumplido=False,
                )
                nuevo.guardar()
                self.lista_habitos.append(nuevo)
            self.page.pop_dialog()
            self._show_main()
            self._snack("Hábito guardado ✓")

        def cancelar(_):
            self.page.pop_dialog()

        dialog = ft.AlertDialog(
            modal=True,
            bgcolor=BG,
            shape=ft.RoundedRectangleBorder(radius=24),
            title=ft.Text(titulo, color=TEXT_PRIMARY,
                          weight=ft.FontWeight.W_700, size=18),
            content=ft.Container(
                width=300,
                content=ft.Column(
                    controls=[
                        nombre_field,
                        ft.Container(height=14),
                        ft.Text("Frecuencia", size=12, color=TEXT_SECONDARY),
                        freq_radio,
                        ft.Container(height=14),
                        duracion_field,
                        ft.Container(height=8),
                        error_text,
                    ],
                    tight=True,
                ),
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Guardar", on_click=guardar),
            ],
        )
        self.page.show_dialog(dialog)

    def _open_confirm_delete(self, habito: Habito.Habito):
        def si(_):
            if habito in self.lista_habitos:
                self.lista_habitos.remove(habito)
            habito.eliminar()
            self.page.pop_dialog()
            self._show_main()
            self._snack("Hábito eliminado")

        def no(_):
            self.page.pop_dialog()

        dialog = ft.AlertDialog(
            modal=True,
            bgcolor=BG,
            shape=ft.RoundedRectangleBorder(radius=24),
            title=ft.Text("¿Eliminar hábito?",
                          color=TEXT_PRIMARY,
                          weight=ft.FontWeight.W_700, size=18),
            content=ft.Text(
                f"Vas a eliminar «{habito.nombre}». Esta acción no se puede deshacer.",
                color=TEXT_SECONDARY, size=13),
            actions=[
                ft.TextButton("Cancelar", on_click=no),
                ft.TextButton("Eliminar", on_click=si),
            ],
        )
        self.page.show_dialog(dialog)

    # ------------------------------------------------------------------ #
    #  Acciones
    # ------------------------------------------------------------------ #
    def _on_mark_done(self, habito: Habito.Habito):
        habito.marcar_cumplido()
        self._show_main()
        self._snack("Hábito marcado con éxito ✓")

    def _snack(self, mensaje: str):
        sb = ft.SnackBar(
            content=ft.Text(mensaje, color=BG_LIGHT, size=13,
                            weight=ft.FontWeight.W_600),
            bgcolor=ACCENT,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=20,
            shape=ft.RoundedRectangleBorder(radius=14),
        )
        self.page.overlay.append(sb)
        sb.open = True
        self.page.update()


# --------------------------------------------------------------------------- #
#  Pequeño helper de UI reutilizable
# --------------------------------------------------------------------------- #
def _detail_row(label, value):
    return ft.Row(
        controls=[
            ft.Text(label, size=12, color=TEXT_SECONDARY, expand=True),
            ft.Text(value, size=13, color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_600),
        ],
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def main(page: ft.Page):
    HabitTrackerApp(page)


if __name__ == "__main__":
    ft.run(main)
