import sqlite3
import secrets
import hashlib

def main():
    # promp user for info
    username = input("Enter username: ")
    password = input("Enter password: ")
    # generate salt
    salt = secrets.token_hex(6)
    salt = "1234abcd"
    # put together the salt and password
    salted_password = password+salt
    # hash
    hashed_password = hashlib.md5(salted_password.encode('ascii')).hexdigest()
    # ready
    conn = sqlite3.connect('database1.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, salt) VALUES (?,?,?)", (username, hashed_password, salt))
    conn.commit()
    cursor.close()
    conn.close()

main()