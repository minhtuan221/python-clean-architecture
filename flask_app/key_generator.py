from Cryptodome.PublicKey import RSA
key = RSA.generate(2048)
pv_key_string = key.exportKey()
with open("private.pem", "w") as prv_file:
    print("{}".format(pv_key_string.decode()), file=prv_file)

pb_key_string = key.publickey().exportKey()
with open("public.pem", "w") as pub_file:
    print("{}".format(pb_key_string.decode()), file=pub_file)

# run below code for installation of Cryptodome
# sudo apt-get install build-essential python3-dev