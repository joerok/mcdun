
def create_bucket(bucket):
    """Creates a Cloud Storage bucket based on configuration."""
    if not bucket.exists():
        bucket.create()
    
