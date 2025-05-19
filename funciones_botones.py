# funciones_botones.py
# Maneja la lógica de los botones para la tienda del juego.

def create_buy_button(store_manager, skin_num, menu):
    """
    Crea un botón 'Comprar' para una skin específica.
    Args:
        store_manager: Instancia de StoreManager para manejar la compra.
        skin_num: Número de la skin a comprar.
        menu: Menú de pygame_menu donde se actualiza la interfaz.
    Returns:
        Función que ejecuta la lógica de compra.
    """
    def buy_skin():
        if store_manager.purchase_skin(skin_num):
            print(f"Skin {skin_num} comprada exitosamente!")
            # Actualizar el menú para reflejar que la skin está desbloqueada
            menu.force_surface_update()
            # Agregar un mensaje temporal de éxito
            menu.add.label("¡Compra exitosa!", font_size=20, font_color=(0, 255, 0), id=f"success_msg_{skin_num}")
            # Eliminar el mensaje después de 2 segundos
            menu.add.timer(2.0, lambda: menu.remove_widget(f"success_msg_{skin_num}"))
            return True
        else:
            print(f"No se pudo comprar la skin {skin_num}: Puntos insuficientes o ya desbloqueada.")
            # Agregar un mensaje temporal de error
            menu.add.label("Puntos insuficientes", font_size=20, font_color=(255, 0, 0), id=f"error_msg_{skin_num}")
            # Eliminar el mensaje después de 2 segundos
            menu.add.timer(2.0, lambda: menu.remove_widget(f"error_msg_{skin_num}"))
            return False
    return buy_skin

def create_return_button(menu):
    """
    Crea un botón 'Regresar' para volver al menú principal.
    Args:
        menu: Menú de pygame_menu para habilitar el menú principal.
    Returns:
        Función que ejecuta la lógica de regreso.
    """
    def return_to_main():
        menu.close()  # Cierra el menú de la tienda
    return return_to_main