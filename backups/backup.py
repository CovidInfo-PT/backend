import boto3
import os
from botocore.exceptions import NoCredentialsError
import argparse
import zipfile
from datetime import datetime
import shutil



class BackupJob():

    def __init__(self, backups_output_dir, dirs_to_backup, bucket_name):

        # Check  dirs  passed
        if backups_output_dir == None:
            print("Bad backups_output_dir")
            exit(1)

        if dirs_to_backup == None:
            print("Bad dirs_to_backup")
            exit(1)
        
        for p in dirs_to_backup:
            if backups_output_dir == None:
                print("Bad dir to back up")
                exit(1)

        self.backups_output_dir = backups_output_dir 
        self.dirs_to_backup = dirs_to_backup

        # We will have to save this as env variables
        self.ACCESS_KEY = os.getenv('COVID_AWS_S3_ACCESS_KEY')
        self.SECRET_KEY = os.getenv('COVID_AWS_S3_SECRET_KEY') 
        self.BUCKET_NAME = bucket_name

        # chek if we have the credencials we need to authenticate in s3 buckets
        if self.ACCESS_KEY == None or self.SECRET_KEY == None:
            print("No env variables to authenticate into S3 buckets. Please set COVID_AWS_S3_ACCESS_KEY and COVID_AWS_S3_SECRET_KEY")
            exit(1)


    # funtion to zip a dir
    def zip_dir(self, path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))


    def upload_to_aws(self, local_file, bucket, s3_file=None):
        # create client
        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

        # if no s3_file_name use the local file name
        if s3_file == None:
            s3_file = local_file

        try:
            s3.upload_file(local_file, bucket, s3_file)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False


    def make_backups(self):
        try:
            for dir_to_be_backed_up in self.dirs_to_backup:

                # get the time of the backup
                now = datetime.now()
                dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")

                # set the name of the backup
                backup_name = "backup-{}.zip".format(dt_string)

                # zip the Data dir
                zipf = zipfile.ZipFile(backup_name, 'w', zipfile.ZIP_DEFLATED)
                self.zip_dir(dir_to_be_backed_up, zipf)
                zipf.close()    

                # upload the zip to s3 buckets
                uploaded = self.upload_to_aws(backup_name, self.BUCKET_NAME)

                # move the zip file to the directory passed
                shutil.move(backup_name, self.backups_output_dir)

                if not uploaded:
                    print("ERROR")
                    exit()

                print("ALL GOOD!")
        except:
            print("ERROR!")
