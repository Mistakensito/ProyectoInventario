import json
import streamlit as st

class User:
    def __init__(self, data_file="data/users.json"):
        self.data_file = data_file
        self.load_data()

    def clear_json_file(self):
        """Overwrite the JSON file with an empty list."""
        with open(self.data_file, "w") as file:
            json.dump([], file)

    def verify_login(self, username, password):
        #users = self.load_users()
        self.load_data()
        for user in self.users:
            if user["username"] == username and user["password"] == password:
                return user["role"]
        return None
    
    def load_data(self):
        with open(self.data_file, "r") as file:
            self.users = json.load(file)

    def save_data(self):
        with open(self.data_file, "w") as file:
            json.dump(self.users, file, indent=4)

    def add_user(self, user):
        self.users.append(user)
        self.save_data()

    def update_user(self, user_id, updated_user):
        for idx, usr in enumerate(self.users):
            if usr["user_id"] == user_id:
                self.users[idx].update(updated_user)
                self.save_data()
                return True
        return False

    def delete_user(self, user_id):
        # Clear the JSON file first
        self.clear_json_file()
        self.users = [usr for usr in self.users if usr["user_id"] != user_id]
        st.write(self.users)
        self.save_data()

    def search_users(self, query):
        return [usr for usr in self.users if query.lower() in usr["username"].lower()]
    
    def get_user_by_id(self, user_id):
        
        for usr in self.users:
            if usr["user_id"] == user_id:
                return usr
        return None

    