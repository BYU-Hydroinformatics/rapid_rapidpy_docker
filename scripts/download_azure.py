import os
import uuid
from azure.storage.file import FileService


connection_string =  # Obtain from Azure


file_share = "rapid-input-files"
region = os.environ['REGION']

file_service = FileService(connection_string=connection_string)
output_path = os.path.join('/home/rapid-io/input', region)

if not os.path.exists(output_path):
    generator = file_service.list_directories_and_files(file_share + '/' + region)
    for file_or_dir in generator:
        path_to_file = os.path.join(region, file_or_dir.name)
        output_file_path = os.path.join(output_path, file_or_dir.name)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        file_service.get_file_to_path(file_share, region, file_or_dir.name, output_file_path)
