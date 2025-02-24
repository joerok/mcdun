import sys
import os
from google.cloud import storage

lib_directory = os.path.join(".", 'lib')
sys.path.append(lib_directory)

from lib.deployment import cloud as dcloud
from lib import cloud
BUCKET = cloud.get_bucket("./config.yaml")
dcloud.create_bucket(BUCKET)
