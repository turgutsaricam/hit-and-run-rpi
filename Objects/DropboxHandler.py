import dropbox
import os


class DropboxHandler:
    """ Uploads files to Dropbox and provides their URL.
    """

    # Dropbox app credentials
    APP_KEY = 'ci7ep1rk2cirvd8'
    APP_SECRET = 'delirr9sclkgxyb'

    # Access token was generated manually in the app console on Dropbox.
    ACCESS_TOKEN = 'KEkmBtQjsiUAAAAAAAAoi4TpDwBCLx_B895nDFSb6mFCLj8RxcuC_69EmcMPzv0a'

    dbx = None

    # DROPBOX_STORAGE_DIR = 'storage/file/dropbox'
    # DROPBOX_ACCESS_TOKEN_FILE_NAME = 'access-token.pickle'

    def __init__(self):
        super().__init__()

        self.dbx = dropbox.Dropbox(self.ACCESS_TOKEN)

    def upload_file(self, file_path):
        """
        :param file_path: Path of the file to be uploaded to Dropbox
        :return: Link of the uploaded file
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError("File not found.")

        file_name = os.path.basename(file_path)
        dest_path = '/' + file_name

        # with open(file_path, "rb") as f:
        #     self.dbx.files_upload(f.read(), dest_path, mute=True)

        with open(file_path, 'rb') as f:
            file_size = os.path.getsize(file_path)

            chunk_size = 1 * 1024 * 1024

            if file_size <= chunk_size:
                self.dbx.files_upload(f.read(), dest_path)

            else:
                upload_session_start_result = self.dbx.files_upload_session_start(f.read(chunk_size))
                cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                           offset=f.tell())
                commit = dropbox.files.CommitInfo(path=dest_path)

                while f.tell() < file_size:
                    if (file_size - f.tell()) <= chunk_size:
                        self.dbx.files_upload_session_finish(f.read(chunk_size),
                                                        cursor,
                                                        commit)
                    else:
                        self.dbx.files_upload_session_append_v2(f.read(chunk_size), cursor)
                        cursor.offset = f.tell()

        # Create a shared link
        shared_link = self.dbx.sharing_create_shared_link_with_settings(dest_path)

        return shared_link.url

    # def init_authorization(self):
    #     """ Initializes authorization process and saves the received access token.
    #
    #     :return: @See self.get_stored_access_token
    #     """
    #     flow = dropbox.DropboxOAuth2FlowNoRedirect(self.APP_KEY, self.APP_SECRET)
    #
    #     # Have the user sign in and authorize this token
    #     authorize_url = flow.start()
    #     print('1. Go to: ' + authorize_url)
    #     print('2. Click "Allow" (you might have to log in first)')
    #     print('3. Copy the authorization code.')
    #
    #     self.access_token = input("Enter the authorization code here: ").strip()
    #
    #     flow.finish(self.access_token)
    #
    #     data = {
    #         'access_token': self.access_token
    #     }
    #
    #     file_path = self._get_access_token_file_path()
    #     file_dir = os.path.dirname(file_path)
    #
    #     # Create the directories if they do not exist
    #     try:
    #         if not os.path.exists(file_dir):
    #             os.makedirs(file_dir)
    #
    #     except OSError as e:
    #         # Raise an error if the dir does not exist. Although we are checking the existence of the dir in the try
    #         # statement, the dir might have been created just after we check it and found out it does not exist. So,
    #         # this handles that situation.
    #         if e.errno != errno.EEXIST:
    #             raise
    #
    #     # Store the file
    #     with open(file_path, 'wb') as fp:
    #         pickle.dump(data, fp)
    #
    #     return self.get_stored_access_token()
    #
    # def get_stored_access_token(self):
    #     """
    #     :return: Access token string.
    #     """
    #
    #     # If the access token already exists, directly return it.
    #     if self.access_token is not None:
    #         return self.access_token
    #
    #     file_path = self._get_access_token_file_path()
    #
    #     if not os.path.isfile(file_path):
    #         raise FileNotFoundError("Access token file is not found.")
    #
    #     # Read the file and set the sensor data
    #     with open(file_path, 'rb') as fp:
    #         access_token_data = pickle.load(fp)
    #
    #     self.access_token = access_token_data['access_token']
    #
    #     return self.access_token
    #
    # def _get_access_token_file_path(self):
    #     return os.path.join(APP_DIR, self.DROPBOX_STORAGE_DIR, self.DROPBOX_ACCESS_TOKEN_FILE_NAME)

# if __name__ == '__main__':
#     handler = DropboxHandler()
#     access_token = handler.init_authorization()
#     print("You are all set! Access Token: {0}".format(access_token))