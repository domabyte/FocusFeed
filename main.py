from src.auth import Authenticator

def main():
    auth = Authenticator()
    loader = auth.login()
    
if __name__ == '__main__':
    main()