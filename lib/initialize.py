import sys
import os
from google.colab import userdata, auth
from google.cloud import storage

# Authenticate with Google Colab
import google.auth

auth.authenticate_user()
project_id = userdata.get('PROJECT_ID')

lib_directory = os.path.join(userdata.get('CONTENT'), 'lib')
sys.path.append(lib_directory)

from lib.deployment import cloud as dcloud
from lib import cloud
BUCKET = cloud.get_bucket(project_id, userdata.get('CONFIG_PATH'))
dcloud.create_bucket(BUCKET)
