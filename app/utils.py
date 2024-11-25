from passlib.context import CryptContext

pwd_context =  CryptContext(schemes=['bcrypt'], deprecated="auto")

def hashing_pass(plain):
    return pwd_context.hash(plain)

def verify_pass(plain, hashed):
    return pwd_context.verify(plain,hashed)

# print(hashing_pass('123'))


# INSERT INTO userdb (username, email, password, is_admin) 
# VALUES ('admin_user', 'admin@example.com', 'has$2b$12$DOWax37dDLjNbaJOhMBZB.6q7pkq5g7z80K/MtloqTa6j3LMwtCA.', 1);