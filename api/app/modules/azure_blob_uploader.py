from dotenv import load_dotenv
import os
from azure.storage.blob import BlobServiceClient
from datetime import datetime

# Load environment variables
load_dotenv('modules/.env')  # Ensure this path is correct

class AzureBlobUploader:
    def __init__(self):
        # Fetch connection string and container name from environment variables
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.container_name = os.getenv('AZURE_CONTAINER_NAME')
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
    
    def upload_log_file(self):
        current_date = datetime.now().strftime("%Y_%m_%d")
        blob_name = f"{current_date}.log"
        file_path = f"./{blob_name}"
        
        # Check if the blob exists
        if self.blob_exists(blob_name):
            print(f"Blob {blob_name} exists, deleting it.")
            self.delete_blob(blob_name)
        
        # Upload the new blob
        self.upload_blob(file_path, blob_name)
        
        # Delete the local log file
        self.delete_local_file(file_path)
    
    def blob_exists(self, blob_name):
        blob_client = self.container_client.get_blob_client(blob_name)
        return blob_client.exists()
    
    def delete_blob(self, blob_name):
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.delete_blob()
    
    def upload_blob(self, file_path, blob_name):
        with open(file_path, "rb") as data:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.upload_blob(data)
            print(f"Uploaded {blob_name} to blob storage.")
    
    def delete_local_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted local file {file_path}.")
        else:
            print("The file does not exist.")

# Example usage
if __name__ == "__main__":
    uploader = AzureBlobUploader()
    uploader.upload_log_file()
