import streamlit as st
import streamlit_authenticator as stauth
import yaml
from inventory_system import InventorySystem
from user import User
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Pre-hashing all plain text passwords once
stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

def login_screen():
    try:
        authenticator.login()
    except Exception as e:
        st.error(e)

    if st.session_state.get('authentication_status') is False:
        st.error("Datos incorrectos")
    elif st.session_state.get('authentication_status') is None:
        st.warning("Por favor ingrese sus credenciales")
    elif st.session_state.get('authentication_status'):
        if st.session_state.get("logout_trigger"):
            st.session_state.clear()
            st.rerun()
        st.success(f"Bienvenido, {st.session_state.get('name')}!")
        role = config["credentials"]["usernames"][st.session_state.get('username')]["role"]
        st.session_state["role"] = role
        st.session_state["logged_in"] = True
        display_sidebar(role)
        display_modules()

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
    if st.sidebar.button("Inicio"):
        st.session_state.page = "home"

    if role == "admin":
        if st.sidebar.button("Manejar productos"):
            st.session_state.page = "product_management"

        if st.sidebar.button("Manejar usuarios"):
            st.session_state.page = "user_management"

        if st.sidebar.button("Permiso de roles"):
            st.session_state.page = "role_permission_management"
    else:
        if st.sidebar.button("Ver productos"):
            st.session_state.page = "product_management"

    logout_button = authenticator.logout("Cerrar sesión", "sidebar")
    if logout_button:
        st.session_state.clear()
        st.rerun()




def display_modules():
    if not st.session_state.get("logged_in"):
        st.warning("Debe iniciar sesión primero.")
        return
    if 'page' not in st.session_state:
        st.session_state.page = "home"

    # Iniciar sistema de inventario
    inventory_system = InventorySystem()

    if st.session_state.page == "home":
        inventory_system.display_home()
    elif st.session_state.page == "view_product":
        inventory_system.display_product_management()
    elif st.session_state.page == "add_product":
        inventory_system.display_add_product_form()
    elif st.session_state.page == "update_product":
        inventory_system.display_update_product_form()
    elif st.session_state.page == "product_management":
        inventory_system.display_product_management()
    elif st.session_state.page == "add_user":
        inventory_system.display_add_user_form()
    elif st.session_state.page == "edit_user":
        inventory_system.display_edit_user_form()
    elif st.session_state.page == "user_management":
        inventory_system.display_user_management()
    elif st.session_state.page == "role_permission_management":
        inventory_system.display_role_permission_management()
    elif st.session_state.page == "add_role":
        inventory_system.display_add_role_form()
    elif st.session_state.page == "update_role":
        inventory_system.display_update_role_form()

def main():
    login_screen()

if __name__ == "__main__":
    main()
