import json

class Product:
    def __init__(self, data_file="data/products.json"):
        self.data_file = data_file
        self.load_data()

    def load_data(self):
        with open(self.data_file, "r") as file:
            self.products = json.load(file)

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
