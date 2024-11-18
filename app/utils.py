from passlib.context import CryptContext

pwd_context =  CryptContext(schemes=['bcrypt'], deprecated="auto")

def hashing_pass(plain):
    return pwd_context.hash(plain)

def verify_pass(plain, hashed):
    return pwd_context.verify(plain,hashed)