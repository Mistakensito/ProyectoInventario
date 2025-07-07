from product import Product
from user import User
from role_permission import RolePermission
from yamlmanager import YamlManager
from pathlib import Path
import time
from datetime import datetime
import streamlit as st
import pandas as pd

class InventorySystem:
    def __init__(self):
        self.product_manager = Product()
        self.user_manager = User()
        self.role_permission_manager = RolePermission()
        self.yaml_manager = YamlManager()

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
        st.markdown(
            """
            <div style='margin: 0px; padding: 0px;'>
                <h3 style='margin: 0px; padding: 0px;'>Sistema de Inventario Masas y Empanadas Ayelén</h3>
                <hr style='margin-top: 16px; margin-bottom: 16px;' />
            </div>
            """,
            unsafe_allow_html=True
        )

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
                filter_option = st.selectbox("Buscar por", ["ID de producto", "Nombre de producto", "Categoría"])
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

            with add_column:
                if st.session_state.get("role", "user") == "admin":
                    st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
                    if st.button("Añadir producto", key="add_product_button_main"):
                        st.session_state.page = "add_product"
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                """ <hr style='margin-top: 8px; margin-bottom: 8px;' /> """,
                unsafe_allow_html=True
            )

            filtered_data = self.product_manager.products

            if filter_button:
                # Añadir filtrado basado en input del usuario
                if filter_option == "ID de producto":
                    filtered_data = [prod for prod in filtered_data if str(filter_value).lower() in str(prod["product_id"]).lower()]
                elif filter_option == "Nombre de producto":
                    filtered_data = [prod for prod in filtered_data if str(filter_value).lower() in str(prod["name"]).lower()]
                elif filter_option == "Categoría":
                    filtered_data = [prod for prod in filtered_data if str(filter_value).lower() in str(prod["category"]).lower()]

            # Muestra los productos encontrados
            if len(filtered_data) == 0:
                st.write("No se encontró productos.")
            else:
                # Elige los datos de la sucursal elegida
                original_df = pd.DataFrame(filtered_data).copy()
                
                # Guarda temporalmente los stocks por sucursal
                original_stock_quantity = [
                    {"product_id": row["product_id"], "stock_quantity": row["stock_quantity"]}
                    for _, row in original_df.iterrows()
                ]
                original_stock_map = {item["product_id"]: item["stock_quantity"] for item in original_stock_quantity}

                original_df["stock_quantity"] = original_df["stock_quantity"].apply(lambda lista: lista[st.session_state.branch])
                original_df["add_or_sell"] = ["" for _ in range(len(original_df))]

                # Editor interactivo
                edited_df = st.data_editor(
                    original_df,
                    column_config={
                        "product_id": None,
                        "last_sales_history": None,
                        "name": "Producto",
                        "category": "Categoría",
                        "price": "Precio",
                        "stock_quantity": "Cantidad",
                        "sales_history": st.column_config.LineChartColumn(
                            "Ventas (últimos 30 días)", y_min=0, y_max=100000
                        ),
                        "add_or_sell": "Añadir o Vender",
                    },
                    disabled=["product_id", "sales_history", "stock_quantity"],
                    hide_index=True,
                )

                # Comparar y actualizar
                has_changes = False
                stock_below_zero = False

                # Calcular días transcurridos desde ultima actualizacion
                current_seconds = int(time.time())
                seconds_passed = current_seconds - self.product_manager.last_date_update
                days_passed = int(seconds_passed // 86400) # segundos en un día

                for i, row in edited_df.iterrows():
                    original_row = original_df.loc[i]

                    # Actualiza todos los sales_history para estar al día
                    if days_passed >= 1:
                        new_sales_history = []
                        product_id = original_row["product_id"]
                        updated_product = row.to_dict()
                        updated_product["product_id"] = product_id
                        updated_product.pop("add_or_sell", None)
                        updated_product["stock_quantity"] = original_stock_map[product_id]

                        if days_passed >= 30:
                            new_sales_history = [0] * (30 - 1)
                        else:
                            # cortar los días pasados viejos
                            new_sales_history = updated_product["sales_history"][days_passed:]
                            # añadir los días pasados nuevos
                            new_sales_history += [0] * (30 - len(new_sales_history) - 1)
                        updated_product["sales_history"] = new_sales_history
                        self.product_manager.update_product(product_id, updated_product)
                        self.product_manager.update_date(
                            {
                                "date": current_seconds
                            }
                        )
                        has_changes = True
                    
                    if not row.equals(original_row):
                        # Cuando hubo un cambio, guarda la fila cambiada
                        product_id = original_row["product_id"]
                        updated_product = row.to_dict()
                        updated_product["product_id"] = product_id

                        # Copia el nuevo stock en la sucursal especifica
                        # Combinandolo con los stocks de las otras sucursales
                        updated_stock_map = original_stock_map[product_id]
                        if updated_product["add_or_sell"] != "":
                            # Si fue una venta
                            if int(updated_product["add_or_sell"]) < 0:
                                updated_product["sales_history"][-1] += abs(int(updated_product["add_or_sell"]))
                            # Actualiza el stock
                            new_stock = int(updated_product["stock_quantity"]) + int(updated_product["add_or_sell"])
                            updated_stock_map[st.session_state.branch] = new_stock
                            if new_stock < 0:
                                has_changes = True
                                stock_below_zero = True
                                break # Rompe el ciclo antes de que se actualice
                        updated_product["stock_quantity"] = updated_stock_map

                        # Quitar columnas extras para evitar subirlos a BDD
                        updated_product.pop("add_or_sell", None)

                        # Añade los cambios
                        self.product_manager.update_product(product_id, updated_product)
                        has_changes = True

                if stock_below_zero:
                    # Muestra error si se intento vender mas de lo que se tenia
                    st.session_state.stock_below_zero = True
                    st.toast('No puedes quedar en stock negativo.', icon='❌')
                    st.session_state.pop("stock_below_zero", None)
                if has_changes and not stock_below_zero:
                    st.rerun()

    def display_add_product_form(self):
        st.subheader("Añadir nuevo producto")

        # Crear nuevo ID incremental
        product_id = self.product_manager.get_next_product_id()

        with st.form(key='add_product_form_unique'):
            st.text_input("ID de producto (auto)", value=product_id, disabled=True)

            name = st.text_input("Nombre de producto", placeholder="Ingrese nombre de producto")
            category = st.text_input("Categoría de producto", placeholder="Ingrese categoría de producto")
            price = st.number_input("Precio de producto", min_value=0.01, step=0.01, placeholder="Ingrese precio de producto")

            # Selector de sucursal
            branch_names = ["Sucursal 1", "Sucursal 2", "Sucursal 3"]
            branch_name = st.selectbox("Sucursal de ingreso de stock", branch_names)
            branch_id = branch_names.index(branch_name)

            stock_quantity_input = st.number_input(
                label=f"Cantidad en stock",
                min_value=0,
                step=1,
                placeholder="Ingrese cantidad de stock",
            )

            # Botones
            add_button = st.form_submit_button(label='Añadir producto')
            cancel_button = st.form_submit_button(label='Cancelar')

            if add_button:
                validation_error = self.validate_fields({
                    "product_id": product_id,
                    "name": name,
                    "category": category,
                    "price": price,
                    "stock_quantity": stock_quantity_input
                })

                if validation_error:
                    st.error(validation_error)
                else:
                    # Construir lista de stock por sucursal (3 sucursales)
                    stock_quantity = [0, 0, 0]
                    stock_quantity[branch_id] = stock_quantity_input

                    new_product = {
                        "product_id": product_id,
                        "name": name,
                        "category": category,
                        "price": price,
                        "stock_quantity": stock_quantity
                    }

                    self.product_manager.add_product(new_product)
                    st.success(f"Producto '{name}' ha sido añadido correctamente!")

                    # Redirigir
                    st.session_state.page = "product_management"
                    st.rerun()
            elif cancel_button:
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
        st.markdown(
            """
            <div style='margin: 0px; padding: 0px;'>
                <h3 style='margin: 0px; padding: 0px;'>Control de usuarios</h3>
                <hr style='margin-top: 16px; margin-bottom: 16px;' />
            </div>
            """,
            unsafe_allow_html=True
        )

        # Add User button
        if st.session_state.get("role") == "admin":
            st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
            if st.button("Añadir usuario", key="add_user_button"):
                st.session_state.page = "add_user"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """ <hr style='margin-top: 8px; margin-bottom: 8px;' /> """,
            unsafe_allow_html=True
        )

        # User list with CRUD operations
        users = self.yaml_manager.list_users()
        for username in users:
            user = users[username]
            
            with st.container():
                col1, col2, col3 = st.columns([4, 2, 2])

                with col1:
                    st.markdown(
                        f"""
                        <div style="display: flex; flex-direction: column; gap: 4px; padding: 6px 0;">
                            <strong>👤 {username}</strong>
                            <div>📧 <a href="mailto:{user["email"]}">{user["email"]}</a></div>
                            <snap>🔐 Rol: {user["role"]}</snap>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
                    if st.button("✏️ Editar", key=f"edit_{username}"):
                        st.session_state.editing_user = username
                        st.session_state.page = "edit_user"
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                with col3:
                    st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
                    if st.button("🗑️ Eliminar", key=f"delete_{username}"):
                        try:
                            self.yaml_manager.delete_user(username)
                            st.success(f"Usuario {username} eliminado")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                """ <hr style='margin-top: 8px; margin-bottom: 8px;' /> """,
                unsafe_allow_html=True
            )

    def display_add_user_form(self):
        st.subheader("Añadir nuevo usuario")

        with st.form(key='add_user_form'):
            username = st.text_input("Nombre de usuario")
            email = st.text_input("Email")
            name = st.text_input("Nombre completo")
            password = st.text_input("Contraseña", type="password")
            role = st.selectbox("Rol", ["admin", "user"])

            if st.form_submit_button("Guardar"):
                try:
                    self.yaml_manager.add_user(username, {
                        "email": email,
                        "name": name,
                        "password": password,  # Remember to hash this in production
                        "role": role
                    })
                    st.success("Usuario creado exitosamente!")
                    st.session_state.page = "user_management"
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

            if st.form_submit_button("Cancelar"):
                st.session_state.page = "user_management"
                st.rerun()

    def display_edit_user_form(self):
        st.subheader("Editar usuario")

        if 'editing_user' not in st.session_state:
            st.error("No se ha seleccionado ningún usuario para editar")
            st.session_state.page = "user_management"
            st.rerun()
            return

        username = st.session_state.editing_user
        user = self.yaml_manager.get_user(username)

        if not user:
            st.error(f"Usuario {username} no encontrado")
            st.session_state.page = "user_management"
            st.rerun()
            return

        with st.form(key=f'edit_user_form_{username}'):
            new_username = st.text_input("Nombre de usuario", value=username)
            email = st.text_input("Email", value=user['email'])
            name = st.text_input("Nombre completo", value=user['name'])
            password = st.text_input("Nueva contraseña (dejar vacío para mantener la actual)",
                                    type="password", value="")
            role = st.selectbox("Rol", ["admin", "user"],
                               index=0 if user['role'] == "admin" else 1)

            if st.form_submit_button("Guardar cambios"):
                try:
                    updated_user = {
                        "email": email,
                        "name": name,
                        "role": role
                    }

                    if password:
                        updated_user["password"] = password

                    if new_username != username:
                        self.yaml_manager.delete_user(username)
                        self.yaml_manager.add_user(new_username, {**user, **updated_user})
                    else:
                        self.yaml_manager.update_user(username, updated_user)

                    st.success("Usuario actualizado correctamente!")
                    st.session_state.page = "user_management"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar usuario: {str(e)}")

            if st.form_submit_button("Cancelar"):
                st.session_state.page = "user_management"
                st.rerun()

    def display_role_permission_management(self):
        st.markdown(
            """
            <div style='margin: 0px; padding: 0px;'>
                <h3 style='margin: 0px; padding: 0px;'>Control de roles y permisos</h3>
                <hr style='margin-top: 16px; margin-bottom: 16px;' />
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.container():

            filter_column, value_column, button_column = st.columns([2, 4, 1.65])
            with filter_column:
                filter_option = st.selectbox("Buscar por", ["ID de rol", "Nombre de rol", "Nivel de permiso"])
            with value_column:
                filter_value = st.text_input(f"Ingresa {filter_option}", "")
            with button_column:
                st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
                filter_button = st.button("Filtrar roles", key="filter_roles_button")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                """ <hr style='margin-top: 8px; margin-bottom: 8px;' /> """,
                unsafe_allow_html=True
            )

            if st.session_state.get("role", "user") == "admin":
                st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
                if st.button("Añadir rol", key="unique_add_role_button"):
                    st.session_state.page = "add_role"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                """ <hr style='margin-top: 8px; margin-bottom: 8px;' /> """,
                unsafe_allow_html=True
            )

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
                        with st.container():
                            col1, col2, col3 = st.columns([4, 2, 2])

                            with col1:
                                st.markdown(
                                    f"""
                                    <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 4px; padding: 6px 0; justify-content: center; align-items: center">
                                        {role.get('role_id', 'ID desconocido')}
                                        <snap>Rol: {role.get('name', 'Nombre desconocido')}</snap>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                            with col2:
                                st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
                                if st.button("✏️ Editar", key=f"update_role_{role['role_id']}_{idx}"):
                                    st.session_state.role_id_to_update = role['role_id']
                                    st.session_state.page = "update_role"
                                    st.rerun()
                                st.markdown("</div>", unsafe_allow_html=True)

                            with col3:
                                st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
                                if st.button("🗑️ Eliminar", key=f"delete_role_{role['role_id']}_{idx}"):
                                    self.delete_role(role['role_id'])
                                st.markdown("</div>", unsafe_allow_html=True)

                        st.markdown(
                            """ <hr style='margin-top: 8px; margin-bottom: 8px;' /> """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.error("Rol no tiene ID de rol.")

    def display_add_role_form(self):
        st.subheader("Añadir nuevo rol")

        role_id = self.role_permission_manager.get_next_role_id()

        with st.form(key='add_role_form'):
            role_id = st.text_input("ID de rol (auto)", value=role_id, disabled=True)
            name = st.text_input("Nombre de rol")
            permission_level = st.text_input("Nivel de permiso")
            submit_button = st.form_submit_button(label='Añadir rol')
            cancel_button = st.form_submit_button(label="Cancelar")

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
            elif cancel_button:
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
                    cancel_button = st.form_submit_button(label="Cancelar")

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
