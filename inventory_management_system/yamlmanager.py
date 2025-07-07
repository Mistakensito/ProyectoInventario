import yaml
from pathlib import Path
import streamlit as st

class YamlManager:
    def __init__(self, config_path="config.yaml"):
        self.config_path = Path(__file__).parent / config_path

    def load_config(self):
        """Load the YAML configuration file"""
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)

    def save_config(self, data):
        """Save data back to the YAML file"""
        with open(self.config_path, 'w') as file:
            yaml.safe_dump(data, file, sort_keys=False)

    def add_user(self, username, user_data):
        """Add a new user to the config"""
        config = self.load_config()
        if username in config['credentials']['usernames']:
            raise ValueError(f"Username '{username}' already exists")
        config['credentials']['usernames'][username] = user_data
        self.save_config(config)

    def update_user(self, username, user_data):
        """Update an existing user"""
        config = self.load_config()
        if username not in config['credentials']['usernames']:
            raise ValueError(f"Username '{username}' not found")
        config['credentials']['usernames'][username].update(user_data)
        self.save_config(config)

    def delete_user(self, username):
        """Delete a user from the config"""
        config = self.load_config()
        if username not in config['credentials']['usernames']:
            raise ValueError(f"Username '{username}' not found")
        del config['credentials']['usernames'][username]
        self.save_config(config)

    def get_user(self, username):
        """Get a user's data"""
        config = self.load_config()
        return config['credentials']['usernames'].get(username)

    def list_users(self):
        """List all users"""
        config = self.load_config()
        return config['credentials']['usernames']
