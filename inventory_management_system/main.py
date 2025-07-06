import streamlit as st
from inventory_system import InventorySystem
from user import User

def login_screen():
    st.title("Login")
    user_manager = User()  # Assuming User class handles login verification

    # Login form with automatic submission on Enter
    with st.form(key="login_form"):
        username = st.text_input("Nombre", placeholder="Ingrese nombre")
        password = st.text_input("Contraseña", type="password", placeholder="Ingrese contraseña")
        login_button = st.form_submit_button("Login")  # Submit button for form

        if login_button:
            role = user_manager.verify_login(username, password)
            if role:
                # Set session state and query parameters on successful login
                st.session_state.logged_in = True
                st.session_state.role = role
                
                # Update query param and refresh page to apply session state
                st.query_params = {"logged_in": "true"}  # Update query param for reload
                st.success(f"Bienvenido, {username}!")
                st.rerun()  # Rerun to apply changes and refresh page with session state

            else:
                st.error("Datos incorrectos")

def check_session_status():
    # Check query params on initial page load if 'logged_in' session state is not set
    if "logged_in" in st.query_params and st.query_params["logged_in"] == "true":
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = True
            st.session_state.role = st.session_state.get("role", "user")
    else:
        st.session_state.logged_in = False

def display_sidebar(role):
    st.sidebar.image("data/logo.png", use_container_width=True)
    st.sidebar.markdown(
        """
        <div style='margin: 0px; padding: 0px;'>
            <h3 style='margin: 0px; padding: 0px;'>Sistema de Inventario</h3>
            <hr style='margin-top: 16px; margin-bottom: 16px;' />
        </div>
        """,
        unsafe_allow_html=True
    )
    # Button to Home
    if st.sidebar.button("Inicio"):
        st.session_state.page = "home"

    if role == "admin":
        #st.sidebar.write("Admin Options:")

        # Button to Manage Products
        if st.sidebar.button("Manejar productos"):
            st.session_state.page = "product_management"

        # Button to Manage Users
        if st.sidebar.button("Manejar usuarios"):
            st.session_state.page = "user_management"

        # Button to Manage Role & Permissions
        if st.sidebar.button("Permiso de roles"):
            st.session_state.page = "role_permission_management"
    else:
        if st.sidebar.button("Ver productos"):
            st.session_state.page = "product_management"

    if st.sidebar.button("Cerrar sesíon"):
        st.session_state.clear()  # Limpiar sesion basado en estado de sesion
        st.query_params = {}  # Limpiar query
        st.rerun()

def display_modules():
    
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    if 'last_page' not in st.session_state:
        st.session_state.last_page = st.session_state.page

    # Reiniciando algunos datos estaticos
    if st.session_state.page != st.session_state.last_page:
        st.session_state.pop("filtered_data", None)
        st.session_state.last_page = st.session_state.page

    # Iniciar sistema de inventario
    inventory_system = InventorySystem()

    if st.session_state.page == "home":
        inventory_system.display_home()  # Mostrar Dashboard
    elif st.session_state.page == "view_product":
        inventory_system.display_product_management()  # Mostrar lista de productos
    elif st.session_state.page == "add_product":
        inventory_system.display_add_product_form()  # Mostrar página de añadir producto
    elif st.session_state.page == "update_product":
        inventory_system.display_update_product_form()  # Mostrar página de actualización de productos
    elif st.session_state.page == "product_management":
        inventory_system.display_product_management()  # Mostrar lista de productos
    elif st.session_state.page == "add_user":
        inventory_system.display_add_user_form()  # Mostrar página de adición de usuarios
    elif st.session_state.page == "update_user":
        inventory_system.display_update_user_form()  # Mostrar página de actualización de usuarios
    elif st.session_state.page == "user_management":
        inventory_system.display_user_management()  # Mostrar lista de usuarios
    elif st.session_state.page == "role_permission_management":
        inventory_system.display_role_permission_management()  # Mostrar página de actualización de roles y permisos
    elif st.session_state.page == "add_role":
        inventory_system.display_add_role_form()
    elif st.session_state.page == "update_role":
        inventory_system.display_update_role_form()
        
def main():

    if "logged_in" not in st.session_state:
        check_session_status()  # Ver estado de sesión

    if st.session_state.logged_in:
        role = st.session_state.get("role", "user")
        # Mostrar sidebar
        display_sidebar(role)
        
        # Mostrar modulos
        display_modules()
        
    else:
        login_screen()
main()
