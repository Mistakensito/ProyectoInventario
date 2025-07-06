from product import Product
from user import User
from role_permission import RolePermission
import random
import streamlit as st
import pandas as pd

class InventorySystem:
    def __init__(self):
        self.product_manager = Product()
        self.user_manager = User()
        self.role_permission_manager = RolePermission()

    def validate_fields(self, fields):
        """
        Verifica que los inputs sean correctos para evitar problemas
        Cada input se pasa como un diccionario con el nombre como llave
        Devuelve error si la verificacion falla
        """
        for field, value in fields.items():
            # Revisa los strings
            if value in [None, '']:  # Verifica que el string no esté vacio
                return f"{field.replace('_', ' ').capitalize()} es requerido."

            # Additional specific field validations
            if field == "price" and value <= 0:
                return "El precio debe ser mayor a 0."
            if field == "stock_quantity" and value < 0:
                return "El stock debe ser mayor a 0."
        
        return None  # No hay errores

    def display_home(self):
        st.subheader("Sistema de Inventario Masas y Empanadas Ayelén")

    def display_product_management(self):
        st.markdown(
            """
            <div style='margin: 0px; padding: 0px;'>
                <h3 style='margin: 0px; padding: 0px;'>Manejo de productos</h3>
                <hr style='margin-top: 16px; margin-bottom: 16px;' />
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.container():
            # Muestra los filtros de productos
            filter_column, value_column, button_column = st.columns([2, 4, 1.65])
            with filter_column:
                filter_option = st.selectbox("Buscar por", ["ID de producto", "Nombre de producto", "Categoría", "Cantidad en stock"])
            with value_column:
                filter_value = st.text_input(f"Enter {filter_option}", "")
            with button_column:
                st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
                filter_button = st.button("Filtrar productos", key="filter_products_button")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                """ <hr style='margin-top: 8px; margin-bottom: 8px;' /> """,
                unsafe_allow_html=True
            )

            # Muestra selector de sucursal y añadir producto
            branch_column, add_column = st.columns([1, 1])
            with branch_column:
                branch_options = ["Sucursal 1", "Sucursal 2", "Sucursal 3"]
                branch_option = st.selectbox("Buscar por", branch_options)

                # Guardar el índice en session_state
                st.session_state.branch = branch_options.index(branch_option)
                if 'last_branch' not in st.session_state:
                    st.session_state.last_branch = st.session_state.branch

                if st.session_state.branch != st.session_state.last_branch:
                    st.session_state.pop("original_stock_quantity", None)
                    st.session_state.pop("original_stock_map", None)
                    st.session_state.last_branch = st.session_state.branch
            with add_column:
                if st.session_state.get("role", "user") == "admin":
                    st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
                    if st.button("Añadir producto", key="add_product_button_main"):
                        st.session_state.page = "add_product"  # Muestra la pagina de añadir productos
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                """ <hr style='margin-top: 8px; margin-bottom: 8px;' /> """,
                unsafe_allow_html=True
            )

            if "filtered_data" not in st.session_state:
                st.session_state.filtered_data = self.product_manager.products
            
            filtered_data = st.session_state.filtered_data

            if filter_button:
                # Añadir filtrado basado en input del usuario
                if filter_option == "ID de producto":
                    filtered_data = [prod for prod in filtered_data if str(filter_value).lower() in str(prod["product_id"]).lower()]
                elif filter_option == "Nombre de producto":
                    filtered_data = [prod for prod in filtered_data if str(filter_value).lower() in str(prod["name"]).lower()]
                elif filter_option == "Categoría":
                    filtered_data = [prod for prod in filtered_data if str(filter_value).lower() in str(prod["category"]).lower()]
                elif filter_option == "Cantidad en stock":
                    try:
                        filter_value_int = int(filter_value)
                        filtered_data = [prod for prod in filtered_data if prod["stock_quantity"] == filter_value_int]
                    except ValueError:
                        st.error("Ingrese un valor de stock valido.")
                        filtered_data = []

            # Muestra los productos encontrados
            if len(filtered_data) == 0:
                st.write("No se encontró productos.")
            else:
                original_df = pd.DataFrame(filtered_data).copy()

                # Elige los datos de la sucursal elegida
                if "original_stock_quantity" not in st.session_state:
                    st.session_state.original_stock_quantity = [
                        {"product_id": row["product_id"], "stock_quantity": row["stock_quantity"]}
                        for _, row in original_df.iterrows()
                    ]
                if "original_stock_map" not in st.session_state:
                    st.session_state.original_stock_map = {item["product_id"]: item["stock_quantity"] for item in st.session_state.original_stock_quantity}
                original_stock_map = st.session_state.original_stock_map

                original_df["stock_quantity"] = original_df["stock_quantity"].apply(lambda lista: lista[st.session_state.branch])

                # Editor interactivo
                edited_df = st.data_editor(
                    original_df,
                    column_config={
                        "product_id": None,
                        "name": "Producto",
                        "category": "Categoría",
                        "price": "Precio",
                        "stock_quantity": "Cantidad",
                        "sales_history": st.column_config.LineChartColumn(
                            "Ventas (últimos 30 días)", y_min=0, y_max=100000
                        ),
                    },
                    disabled=["product_id", "sales_history"],
                    hide_index=True,
                )

                # Comparar y actualizar
                for i, row in edited_df.iterrows():
                    original_row = original_df.loc[i]

                    if not row.equals(original_row):
                        # Cuando hubo un cambio, guarda la fila cambiada
                        product_id = original_row["product_id"]
                        updated_product = row.to_dict()
                        updated_product["product_id"] = product_id

                        # Copia el nuevo stock en la sucursal especifica
                        updated_stock_map = original_stock_map[product_id]
                        updated_stock_map[st.session_state.branch] = updated_product["stock_quantity"]
                        updated_product["stock_quantity"] = updated_stock_map

                        self.product_manager.update_product(product_id, updated_product)

    def display_add_product_form(self):
        st.subheader("Añadir nuevo producto")

        with st.form(key='add_product_form_unique'):
            product_id = st.text_input("ID de producto", placeholder="Ingrese ID de producto")
            name = st.text_input("Nombre de producto", placeholder="Ingrese nombre de producto")
            category = st.text_input("Categoría de producto", placeholder="Ingrese categoría de producto")
            price = st.number_input("Precio de producto", min_value=0.01, step=0.01, placeholder="Ingrese precio de producto")
            stock_quantity = st.number_input("Cantidad en stock", min_value=0, step=1, placeholder="Ingrese cantidad de stock")
            # Añadir un boton de añadir y uno de cancelar
            col1, col2 = st.columns(2)
            with col1:
                add_button = st.form_submit_button(label='Añadir producto')
            with col2:
                cancel_button = st.form_submit_button(label='Cancelar')
                
            if add_button:
                validation_error = self.validate_fields({
                    "product_id": product_id,
                    "name": name,
                    "category": category,
                    "price": price,
                    "stock_quantity": stock_quantity
                })

                # Valida antes de añadir producto
                if validation_error:
                    st.error(validation_error)
                else:
                    # Add the product to product manager
                    new_product = {
                        "product_id": product_id,
                        "name": name,
                        "category": category,
                        "price": price,
                        "stock_quantity": stock_quantity
                    }
                    self.product_manager.add_product(new_product)
                    st.success(f"Producto '{name}' ha sido añadido correctamente!")
                    
                    st.session_state.page = "product_management"  # Redirige a control de producto
                    st.rerun()  # Inicia el rerun
            elif cancel_button:
                # Si se preciona cancelar, se vuelve al inicio
                st.session_state.page = "product_management"
                st.rerun()        

    def display_update_product_form(self):
        if st.session_state.product_id_to_update:
            product_id = st.session_state.product_id_to_update
            product = self.product_manager.get_product_by_id(product_id)

            if product:
                st.subheader("Actualizar producto")
                with st.form(key="update_product_form"):
                    name = st.text_input("Nombre de producto", value=product["name"], placeholder="Ingrese nombre de producto")
                    category = st.text_input("Categoría", value=product["category"], placeholder="Ingrese categoría del producto")
                    price = st.number_input("Precio", min_value=0.01, step=0.01, value=product["price"], placeholder="Ingrese precio del producto")
                    stock_quantity = st.number_input("Cantidad de stock", min_value=0, step=1, value=product["stock_quantity"], placeholder="Ingrese cantidad de stock")
                    # Add two submit buttons for "Add Product" and "Cancel"
                    col1, col2 = st.columns(2)
                    with col1:
                        update_button = st.form_submit_button(label='Actualizar producto')
                    with col2:
                        cancel_button = st.form_submit_button(label='Cancelar')

                    if update_button:
                        validation_error = self.validate_fields({
                            "name": name,
                            "category": category,
                            "price": price,
                            "stock_quantity": stock_quantity
                        })
                        # Validate form fields before adding the product
                        # validation_error = self.validate_product_fields(product_id, name, category, price, stock_quantity)
                        
                        if validation_error:
                            st.error(validation_error)
                        else:

                            if validation_error:
                                st.error(validation_error)
                            else:
                                updated_product = {
                                    "product_id": product_id,
                                    "name": name,
                                    "category": category,
                                    "price": price,
                                    "stock_quantity": stock_quantity
                                }
                                self.product_manager.update_product(product_id, updated_product)
                                st.success(f"Producto '{name}' actualizado correctamente!")
                                st.session_state.page = "product_management"  # Redirige a manejo de producto
                                st.rerun()  # Recarga la pagina
                    elif cancel_button:
                        # Si se cancela, se regresa a manejo de producto
                        st.session_state.page = "product_management"
                        st.rerun()  

    def delete_product(self, product_id):
        # Muestra la confirmación de borrado
        product = self.product_manager.get_product_by_id(product_id)

        if product:
            st.warning(f"Seguro que quieres eliminar '{product['name']}'?")
            confirm_delete = st.button("Confirmar", key=f"confirm_delete_button_{product_id}")

            if confirm_delete:
                self.product_manager.delete_product(product_id)
                st.success(f"Producto '{product['name']}' eliminado correctamente!")
                st.session_state.page = "product_management"
                st.rerun()

    def display_user_management(self):
        st.subheader("Control de usuarios")

        with st.container():
            # Add User button with a unique key
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.session_state.get("role", "user") == "admin":
                    if st.button("Añadir usuario", key="unique_add_user_button"):  # Asegura una key aleatoria unica
                        st.session_state.page = "add_user"  # Redirige a la página de añadir usuario

            # Muestra filtros de usuario
            filter_column, value_column = st.columns([2, 4])
            with filter_column:
                filter_option = st.selectbox("Buscar por", ["ID de usuario", "Nombre de usuario", "Rol"])
            with value_column:
                filter_value = st.text_input(f"Ingrese {filter_option}", "")

            filter_button = st.button("Filtrar usuarios", key="filter_users_button")  # Ensure unique key
            filtered_data = self.user_manager.users

            if filter_button:
                # Aplica filtro basado en el input
                if filter_option == "ID de usuario":
                    filtered_data = [usr for usr in filtered_data if "user_id" in usr and str(filter_value).lower() in str(usr["user_id"]).lower()]
                elif filter_option == "Nombre de usuario":
                    filtered_data = [usr for usr in filtered_data if "username" in usr and str(filter_value).lower() in str(usr["username"]).lower()]
                elif filter_option == "Rol":
                    filtered_data = [usr for usr in filtered_data if "role" in usr and str(filter_value).lower() in str(usr["role"]).lower()]

            # Muestra los resultados del filtro
            if len(filtered_data) == 0:
                st.write("No se encontraron usuario.")
            else:
                for idx, user in enumerate(filtered_data):
                    # Busca por user_id para evitar errores de llave
                    if "user_id" in user:
                        user_row = f"**{user.get('username', 'Usuario desconocido')}** - {user.get('role', 'Sin rol')}"
                        col1, col2, col3 = st.columns([4, 2, 2])
                        
                        with col1:
                            st.write(user_row)
                        with col2:
                            if st.session_state.get("role", "user") == "admin":
                                # Ensure unique key for each button in the loop
                                if st.button("Actualizar", key=f"update_user_{user['user_id']}_{idx}"):
                                    st.session_state.user_id_to_update = user['user_id']
                                    st.session_state.page = "update_user"  # Redirect to update page
                        with col3:
                            if st.session_state.get("role", "user") == "admin":
                                # Ensure unique key for each button in the loop
                                if st.button("Eliminar", key=f"delete_user_{user['user_id']}_{idx}"):
                                    self.delete_user(user['user_id'])
                    else:
                        st.error("Usuario no tiene ID. Revisar consistencia en los datos.")

    def display_add_user_form(self):
        st.subheader("Añadir nuevo usuario")

        with st.form(key='add_user_form'):
            user_id = st.text_input("ID de usuario")
            username = st.text_input("Nombre de usuario")
            role = st.text_input("Rol")
            # Botones para añadir y para cancelar
            col1, col2 = st.columns(2)
            with col1:
                add_button = st.form_submit_button(label='Añadir usuario')
            with col2:
                cancel_button = st.form_submit_button(label='Cancelar')

            if add_button:
                # Add the user to user manager
                new_user = {
                    "user_id": user_id,
                    "username": username,
                    "role": role
                }
                self.user_manager.add_user(new_user)
                st.success(f"Usuario '{username}' añadido correctamente!")

                st.session_state.page = "user_management"  # Redirige a manejo de usuario
                st.rerun()  # Recarga la pagina
            elif cancel_button:
                # Si se cancela, se vuelve a control de usuarios
                st.session_state.page = "user_management"
                st.rerun()

    def display_update_user_form(self):
        if "user_id_to_update" in st.session_state:
            user_id = st.session_state.user_id_to_update
            user = self.user_manager.get_user_by_id(user_id)

            if user:
                st.subheader("Actualizar usuario")
                col1, col2 = st.columns(2)
                with st.form(key="update_user_form"):
                    username = st.text_input("Nombre de usuario", value=user["username"])
                    role = st.text_input("Rol", value=user["role"])
                    submit_col, cancel_col = st.columns(2)
                    with submit_col:
                        submit_button = st.form_submit_button(label="Actualizar usuario")
                    with cancel_col:
                        cancel_button = st.form_submit_button(label="Cancelar")
                    if submit_button:
                        updated_user = {
                            "user_id": user_id,
                            "username": username,
                            "role": role
                        }
                        self.user_manager.update_user(user_id, updated_user)
                        st.success(f"Usuario '{username}' actualizado correctamente!")
                        st.session_state.page = "user_management"
                        st.rerun()
                    elif cancel_button:
                        st.session_state.page = "user_management"
                        st.rerun()


    def delete_user(self, user_id):
        user = self.user_manager.get_user_by_id(user_id)

        if user:
            st.warning(f"Seguro que quieres eliminar a '{user['username']}'?")
            confirm_delete = st.button("Confirmar", key=f"confirm_delete_user_{user_id}")

            if confirm_delete:
                self.user_manager.delete_user(user_id)
                st.success(f"Usuario '{user['username']}' eliminado correctamente!")
                st.session_state.page = "user_management"
                #st.rerun()

    def display_role_permission_management(self):
        st.subheader("Control de roles y permisos.")
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("Añadir rol", key="unique_add_role_button"):
                    st.session_state.page = "add_role"
            filter_column, value_column = st.columns([2, 4])
            with filter_column:
                filter_option = st.selectbox("Buscar por", ["ID de rol", "Nombre de rol", "Nivel de permiso"])
            with value_column:
                filter_value = st.text_input(f"Ingresa {filter_option}", "")

            filter_button = st.button("Filtrar roles", key="filter_roles_button")
            filtered_data = self.role_permission_manager.roles

            if filter_button:
                if filter_option == "ID de rol":
                    filtered_data = [role for role in filtered_data if "role_id" in role and str(filter_value).lower() in str(role["role_id"]).lower()]
                elif filter_option == "Nombre de rol":
                    filtered_data = [role for role in filtered_data if "name" in role and str(filter_value).lower() in str(role["name"]).lower()]
                elif filter_option == "Nivel de permiso":
                    filtered_data = [role for role in filtered_data if "permission_level" in role and str(filter_value).lower() in str(role["permission_level"]).lower()]

            # Mostrar el rol
            if len(filtered_data) == 0:
                st.write("No se encontró rol.")
            else:
                for idx, role in enumerate(filtered_data):
                    if "role_id" in role:
                        role_row = f"**{role.get('role_id', 'ID desconocido')}** - {role.get('name', 'Nombre desconocido')}"
                        col1, col2, col3 = st.columns([4, 2, 2])
                        
                        with col1:
                            st.write(role_row)
                        with col2:
                            if st.button("Actualizar", key=f"update_role_{role['role_id']}_{idx}"):
                                st.session_state.role_id_to_update = role['role_id']
                                st.session_state.page = "update_role"
                        with col3:
                            if st.button("Eliminar", key=f"delete_role_{role['role_id']}_{idx}"):
                                self.delete_role(role['role_id'])
                    else:
                        st.error("Rol no tiene ID de rol.")

    def display_add_role_form(self):
        st.subheader("Añadir nuevo rol")

        with st.form(key='add_role_form'):
            role_id = st.text_input("ID de rol")
            name = st.text_input("Nombre de rol")
            permission_level = st.text_input("Nivel de permiso")
            submit_button = st.form_submit_button(label='Añadir rol')

            if submit_button:
                new_role = {
                    "role_id": role_id,
                    "name": name,
                    "permission_level": permission_level
                }
                self.role_permission_manager.add_role(new_role)
                st.success(f"Rol '{name}' añadido correctamente!")

                st.session_state.page = "role_permission_management"
                st.rerun()

    def display_update_role_form(self):
        if 'role_id_to_update' in st.session_state:
            role_id = st.session_state.role_id_to_update
            role = self.role_permission_manager.get_role_by_id(role_id)
            if role:
                st.subheader("Actualizar rol")
                with st.form(key="update_role_form"):
                    name = st.text_input("Nombre del rol", value=role["name"])
                    permission_level = st.text_input("Nivel de permiso", value=role["permission_level"])
                    submit_button = st.form_submit_button(label="Actualizar rol")
                col1, col2 = st.columns(2)
                with col2:
                    cancel_button = st.button("Cancelar")

                if submit_button:
                    updated_role = {
                        "role_id": role_id,
                        "name": name,
                        "permission_level": permission_level
                    }
                    self.role_permission_manager.update_role(role_id, updated_role)
                    st.success(f"Rol '{name}' actualizado correctamente!")
                    st.session_state.page = "role_permission_management"
                    st.rerun()
                elif cancel_button:
                    st.session_state.page = "role_permission_management"
                    st.rerun()


    def delete_role(self, role_id):
        role = self.role_permission_manager.get_role_by_id(role_id)

        if role:
            st.warning(f"Eliminar el rol '{role['name']}'?")
            confirm_delete = st.button("Confirmar", key=f"confirm_delete_role_{role_id}")

            if confirm_delete:
                self.role_permission_manager.delete_role(role_id)
                st.success(f"Rol '{role['name']}' eliminado correctamente!")
                st.session_state.page = "role_permission_management"
                st.rerun()
