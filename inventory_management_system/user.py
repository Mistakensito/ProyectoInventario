import yaml
import streamlit_authenticator as stauth


class User:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.load_users()

    def load_users(self):
        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)

    def save_users(self):
        with open(self.config_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)

    @property
    def users(self):
        return [
            {
                "user_id": username,
                "username": user["name"],
                "role": user["role"]
            }
            for username, user in self.config["credentials"]["usernames"].items()
        ]

    def get_user_by_id(self, user_id):
        return self.config["credentials"]["usernames"].get(user_id, None)

    def add_user(self, user):
        username = user["user_id"]
        hashed_password = stauth.Hasher([user["password"]]).generate()[0]
        self.config["credentials"]["usernames"][username] = {
            "name": user["username"],
            "email": user.get("email", ""),
            "password": hashed_password,
            "role": user["role"]
        }
        self.save_users()

    def update_user(self, user_id, updated_user):
        if user_id in self.config["credentials"]["usernames"]:
            user_entry = self.config["credentials"]["usernames"][user_id]
            user_entry["name"] = updated_user["username"]
            user_entry["role"] = updated_user["role"]
            if "password" in updated_user and updated_user["password"]:
                user_entry["password"] = stauth.Hasher([updated_user["password"]]).generate()[0]
            if "email" in updated_user:
                user_entry["email"] = updated_user["email"]
            self.save_users()
            return True
        return False

    def delete_user(self, user_id):
        if user_id in self.config["credentials"]["usernames"]:
            del self.config["credentials"]["usernames"][user_id]
            self.save_users()
            return True
        return False
