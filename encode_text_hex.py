message = "iss baar Paper presentation bhi karna hai" 
with open("temp.jpg", "ab") as f:
    f.write(message.encode('utf8'))