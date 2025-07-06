import json

class RolePermission:
    def __init__(self, data_file="data/roles.json"):
        self.data_file = data_file
        self.load_data()

    def load_data(self):
        with open(self.data_file, "r") as file:
            self.roles = json.load(file)

    def save_data(self):
        with open(self.data_file, "w") as file:
            json.dump(self.roles, file, indent=4)

    def add_role(self, role):
        self.roles.append(role)
        self.save_data()

    def update_role(self, role_name, updated_role):
        for idx, role in enumerate(self.roles):
            if role["name"] == role_name:
                self.roles[idx].update(updated_role)
                self.save_data()
                return True
        return False

    def delete_role(self, role_name):
        self.roles = [role for role in self.roles if role["name"] != role_name]
        self.save_data()

    def search_roles(self, query):
        return [role for role in self.roles if query.lower() in role["name"].lower()]

    def get_role_by_id(self, role_id):
        
        for role in self.roles:
            if role["role_id"] == role_id:
                return role
        return None