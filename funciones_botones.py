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
    # TODO: Definir la función que se ejecuta al presionar el botón Comprar
    def buy_skin():
        # TODO: Intentar comprar la skin usando StoreManager
        if store_manager.purchase_skin(skin_num):
            # TODO: Forzar la actualización del menú para mostrar el cambio (skin desbloqueada)
            menu.force_surface_update()
            return True
        # TODO: Retornar False si no se pudo comprar (puntos insuficientes)
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
    # TODO: Definir la función que se ejecuta al presionar el botón Regresar
    def return_to_main():
        # TODO: Deshabilitar el menú de la tienda para volver al menú principal
        menu.disable()
    return return_to_main