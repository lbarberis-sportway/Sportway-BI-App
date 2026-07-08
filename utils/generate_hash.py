import streamlit_authenticator as stauth
import getpass

def main():
    print("--- Generatore di Hash per Streamlit Authenticator ---")
    password = input("Inserisci la password da criptare: ")
    
    # Generiamo l'hash della password usando direttamente bcrypt
    import bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print("\nEcco la tua password criptata da incollare nel file config.yaml:")
    print("-" * 50)
    print(hashed_password)
    print("-" * 50)

if __name__ == "__main__":
    main()
