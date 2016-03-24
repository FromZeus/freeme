import Crypto
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Signature import PKCS1_v1_5

# Generating of private and public keys
random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
public_key = key.publickey()

# Making the signature for sign with private key
signature = PKCS1_v1_5.new(key)
hash = SHA512.new("test")
signed_message = signature.sign(hash)

# Making verifier for verify with public key
verifier = PKCS1_v1_5.new(public_key)

# Verify that message belongs to original author
print verifier.verify(hash, signed_message)