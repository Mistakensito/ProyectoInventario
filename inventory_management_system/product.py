import json

class Product:
    def __init__(self, data_file="data/products.json", update_sales_history_file="data/last_sale_history.json"):
        self.data_file = data_file
        self.update_sales_history_file = update_sales_history_file
        self.load_data()

    def load_data(self):
        with open(self.data_file, "r") as file:
            self.products = json.load(file)
        with open(self.update_sales_history_file, "r") as file:    
            self.last_update = json.load(file)
            self.last_date_update = self.last_update["date"]

    def save_data(self):
        with open(self.data_file, "w") as file:
            json.dump(self.products, file, indent=4)

    def add_product(self, product):
        self.products.append(product)
        self.save_data()

    def update_product(self, product_id, updated_product):
        for idx, prod in enumerate(self.products):
            if prod["product_id"] == product_id:
                self.products[idx].update(updated_product)
                self.save_data()
                return True
        return False
    
    def update_date(self, date):
        with open(self.update_sales_history_file, "w") as file:
            json.dump(date, file, indent=4)

    def delete_product(self, product_id):
        # Filtra los productos con el mismo product_id
        updated_products = [prod for prod in self.products if prod["product_id"] != product_id]

        # Si el tamaño de lista cambia, actualiza y guarda los datos
        if len(updated_products) != len(self.products):
            self.products = updated_products
            self.save_data()
            return True
        else:
            # Si ningun producto se encuentra con esa ID
            return True

    def search_products(self, query):
        return [prod for prod in self.products if query.lower() in prod["name"].lower()]

    def filter_products(self, low_stock_threshold):
        return [prod for prod in self.products if prod["stock_quantity"] <= low_stock_threshold]
    
    def get_product_by_id(self, product_id):
        
        for prod in self.products:
            if prod["product_id"] == product_id:
                return prod
        return None
    
    def get_next_product_id(self):
        # Obtener el mayor ID numérico directamente
        ids = []
        for prod in self.products:
            try:
                ids.append(int(prod["product_id"]))
            except (ValueError, TypeError):
                continue

        if not ids:
            return "1"
        
        next_product_id = max(ids) + 1

        return str(next_product_id)
