from cryptography.fernet import Fernet

msg = "Hello"

key = Fernet.generate_key()

fernet_instance = Fernet(key)

enc_msg = fernet_instance.encrypt(msg.encode())
dec_msg = fernet_instance.decrypt(enc_msg).decode()

print("message : ",msg)
print("key : ",key)
print("Encrypted message : ",enc_msg)
print("Decrypted message : ",dec_msg)