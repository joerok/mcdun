from google.cloud import storage
import yaml

def get_bucket(config_file):
    """Creates a Cloud Storage bucket based on configuration."""
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    bucket_name = config["bucket_name"]

    storage_client = storage.Client()
    return storage_client.bucket(bucket_name)
