import streamlit_authenticator as stauth

password = "mypassword123"
hashed_pw = stauth.Hasher([password]).generate()[0]
print("Hashed:", hashed_pw)
