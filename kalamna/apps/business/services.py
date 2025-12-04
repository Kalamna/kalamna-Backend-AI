from passlib.context import CryptContext

hashed_text = CryptContext(schemes=['bcrypt'], deprecated='auto')

# to make the plain password hased and compare it to the database password
def verify_password(plain_password, hashed_password) ->bool:
    return hashed_text.verify(plain_password, hashed_password)

# get permission flag for payload
def permission_flag(employee):
    if employee == 'OWNER':
        return 'owner'
    else:
        return 'staff'