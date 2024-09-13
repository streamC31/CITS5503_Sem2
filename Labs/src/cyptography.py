import logging
import os
import boto3
from botocore.exceptions import ClientError


s3 = boto3.client('s3', region_name="ap-southeast-2")
kms = boto3.client('kms', region_name="ap-southeast-2")

bucket_name = '23011392-cloudstorage'
kms_alias = 'alias/23011392'

def get_kms_key_id(alias_name):
    try:
        response = kms.describe_key(KeyId=alias_name)
        return response['KeyMetadata']['KeyId']
    except ClientError as e:
        logging.error(f"Error retrieving KMS key ID: {e}")
        return None

def encrypt_file(file_path, kms_key_id):
    try:
        with open(file_path, 'rb') as file:
            file_contents = file.read()

        response = kms.encrypt(KeyId=kms_key_id, Plaintext=file_contents)
        encrypted_data = response['CiphertextBlob']

        encrypted_file_path = f"{file_path}.encrypted"
        with open(encrypted_file_path, 'wb') as file:
            file.write(encrypted_data)

        print(f"File encrypted: {encrypted_file_path}")
        return encrypted_file_path
    except (IOError, ClientError) as e:
        logging.error(f"Error encrypting file {file_path}: {e}")
        return None

def decrypt_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            encrypted_data = file.read()

        response = kms.decrypt(CiphertextBlob=encrypted_data)
        decrypted_data = response['Plaintext']

        decrypted_file_path = file_path.replace('.encrypted', '.decrypted')
        with open(decrypted_file_path, 'wb') as file:
            file.write(decrypted_data)

        print(f"File decrypted: {decrypted_file_path}")
        return decrypted_file_path
    except (IOError, ClientError) as e:
        logging.error(f"Error decrypting file {file_path}: {e}")
        return None

def process_s3_files(kms_key_id):
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' not in response:
            print("No objects found in the bucket.")
            return

        for obj in response['Contents']:
            file_key = obj['Key']
            local_file_path = os.path.join('/tmp', file_key)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            # Download the file
            s3.download_file(bucket_name, file_key, local_file_path)
            print(f"Downloaded: {local_file_path}")

            # Encrypt the file
            encrypted_file_path = encrypt_file(local_file_path, kms_key_id)
            if encrypted_file_path:
                # Upload encrypted file
                encrypted_key = f"{file_key}.encrypted"
                s3.upload_file(encrypted_file_path, bucket_name, encrypted_key)
                print(f"Uploaded encrypted file: {encrypted_key}")

                # Decrypt the file
                decrypted_file_path = decrypt_file(encrypted_file_path)
                if decrypted_file_path:
                    # Upload decrypted file
                    decrypted_key = f"{file_key}.decrypted"
                    s3.upload_file(decrypted_file_path, bucket_name, decrypted_key)
                    print(f"Uploaded decrypted file: {decrypted_key}")

            # Clean up local files
            for path in [local_file_path, encrypted_file_path, decrypted_file_path]:
                if path and os.path.exists(path):
                    os.remove(path)

    except ClientError as e:
        logging.error(f"Error processing S3 files: {e}")

def main():
    kms_key_id = get_kms_key_id(kms_alias)
    if not kms_key_id:
        logging.error("Could not retrieve KMS key ID.")
        return

    process_s3_files(kms_key_id)

if __name__ == '__main__':
    main()