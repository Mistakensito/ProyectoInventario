import streamlit_authenticator as stauth

# List of plain text passwords to hash
passwords = ['admin123', 'user123']  # Replace with your actual passwords

# Generate hashed passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# Print the hashed passwords
print("Hashed passwords:")
for i, password in enumerate(passwords):
    print(f"Original: {password} -> Hashed: {hashed_passwords[i]}")
