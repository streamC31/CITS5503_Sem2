import logging
import os
import struct
from Crypto.Cipher import AES
from Crypto import Random
import boto3
import hashlib
from botocore.exceptions import ClientError


BLOCK_SIZE = 16
CHUNK_SIZE = 64 * 1024

s3 = boto3.client('s3', region_name="ap-southeast-2")
bucket_name = '23011392-cloudstorage'

password = 'kitty and the kat'

def encrypt_file(password, in_filename, out_filename):
    key = hashlib.sha256(password.encode("utf-8")).digest()
    iv = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(CHUNK_SIZE)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

def decrypt_file(password, in_filename, out_filename):
    key = hashlib.sha256(password.encode("utf-8")).digest()

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(CHUNK_SIZE)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)

def process_s3_files():
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' not in response:
            print("No objects found in the bucket.")
            return

        for obj in response['Contents']:
            file_key = obj['Key']
            if file_key.endswith('.encrypted') or file_key.endswith('.decrypted'):
                continue  # Skip already processed files

            local_file_path = os.path.join('/', file_key)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            # Download the file
            s3.download_file(bucket_name, file_key, local_file_path)
            print(f"Downloaded: {local_file_path}")

            # Encrypt the file
            encrypted_file_path = f"{local_file_path}.encrypted"
            encrypt_file(password, local_file_path, encrypted_file_path)
            encrypted_key = f"{file_key}.encrypted"
            s3.upload_file(encrypted_file_path, bucket_name, encrypted_key)
            print(f"Uploaded encrypted file: {encrypted_key}")

            # Decrypt the file
            decrypted_file_path = f"{local_file_path}.decrypted"
            decrypt_file(password, encrypted_file_path, decrypted_file_path)
            decrypted_key = f"{file_key}.decrypted"
            s3.upload_file(decrypted_file_path, bucket_name, decrypted_key)
            print(f"Uploaded decrypted file: {decrypted_key}")

            # Clean up local files
            for path in [local_file_path, encrypted_file_path, decrypted_file_path]:
                if path and os.path.exists(path):
                    os.remove(path)

    except ClientError as e:
        logging.error(f"Error processing S3 files: {e}")

if __name__ == '__main__':
    process_s3_files()