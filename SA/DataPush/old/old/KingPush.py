from apiclient import discovery
from apiclient.http import MediaFileUpload
import os 

from DataPush import Auth
from DataPush import Email

#Things to Develop ///
#Link share ->> Check perms first and then create if not shared - Preserves Sharing link for multiple uses with same data
#File Update - overwrite new changes + keep same file ID rather than new file!!!!


class Gdrive:
	def __init__(self, FILE_PATH,FILE_NAME):
		self.credentials = Auth.Gauth.credentials_from_file()
		self.drive_service = discovery.build('drive', 'v3', credentials=self.credentials)
		self.FILE_PATH = FILE_PATH
		self.FILE_NAME = FILE_NAME
		self.FILE_ID =  'Null'
		self.CSV_FILENAME = 'Null'
	
	def get_file_list(self):
	#Get list of files currently stored on Gdrive
		NameList = []
		IdList = []
		#Initialises empty lists
		
		results = self.drive_service.files().list(
    pageSize=100, fields="nextPageToken, files(id, name)").execute()
	#Requests list of stored files, max 100 per page (look at scalability /repetitions)'
		items = results.get('files', [])
		#Extract files from returned API DATA
	
		if not items:
		#if no data returned by API.
			print('No files found.')
			#No files
		else:
		#Otherwise
				print('Files:')
				#Print 
				for item in items:
					"""
					with open("GDriveFileList.txt", "a") as outfile:
						outfile.write(item['name'])
					"""

					print('{0} ({1})'.format(item['name'], item['id']))
					if item['id'] != '1PRyStjpIFY3RnoAnJ3ZPOgiB-18j3ogh':
						IdList.append(item['id'])
						NameList.append(item['name'])
				return NameList, IdList


	def filecheck(self, CSV_FILENAME):
		"""
		import os.path
		PATH ='./GDriveFileList.txt'
		if os.path.isfile(PATH):
			with open("GDriveFileList.txt") as GDriveList:
				NameList = GDriveList.read()
		else:
		"""
		NameList, IdList = self.get_file_list()
		#Get list of all files on Gdrive & assoc IDs
		print("======================")
		print(CSV_FILENAME)
		self.CSV_FILENAME = "Twitter Data /// " + CSV_FILENAME
		#print(CSV_FILENAME)
		#print(NameList)
		#print("======================")
		print(self.CSV_FILENAME)
		print(NameList)
		if self.CSV_FILENAME in NameList:
		#If csv filename is within the returned API data
			index = NameList.index(self.CSV_FILENAME)
			#Get index of CSV_FILENAME
			self.FILE_ID =IdList[index]
			#Set obj file id to id
			return True
			#Return true - file does already exist
		else:
		#Otherwise (if not in list)
			return False
			#Return false - file does not currently exist.


	def drive_purge(self):
		NameList, IdList = self.get_file_list()
		#Get list of files & IDs
		for item in IdList:
			print("===================")
			#request = 
			self.drive_service.files().delete(fileId=item).execute()
			print("Trashed: " + item)


			
##################################################################
	 #def GetPermissions(self):
    #Downloads all permissions from Google Drive, as this information is
    #not downloaded by FetchMetadata by default.
    #:return: A list of the permission objects.
    #:rtype: object[]
    #
   # self.FetchMetadata(fields='permissions')
    #return self.metadata.get('permissions')

 # def _FilesTrash(self, param=None):
#
#		Soft-delete (Trash) a file using Files.Trash().
#    :param param: additional parameter to file.
#    :type param: dict.
#    :raises: ApiRequestError
#    """
#		"""
#    if param is None:
#      param = {}
#    param['fileId'] = self.metadata.get('id') or self['id']#
#
#    # Teamdrive support
#    param['supportsTeamDrives'] = True

#    try:
#      self.auth.service.files().trash(**param).execute(
#        http=self.http)
#    except errors.HttpError as error:
#      raise ApiRequestError(error)
#    else:
#      if self.metadata:
#        self.metadata[u'labels'][u'trashed'] = True
#      return True
#
##############################################################

	def update_csv(self):
		print(self.FILE_ID)
		file = self.drive_service.files().get(fileId=self.FILE_ID).execute
		print("!!!!!!!!!!!!!!!11")

		print(file)
		media = MediaFileUpload(self.CSV_FILENAME, mimetype='text/csv', resumable=True)
#                                  # now send the update request
#                                  #   to the API.
		updated_file = self.drive_service.files().update(fileId=self.FILE_ID,body=file, media_body=media).execute()
		print(updated_file)
		"""
		media = MediaIoBaseUpload(fh,
                        mimetype='text/plain')
    # Send the request to the API.
    #print(BytesIO(contents.encode()).read())
    print(fileID)
    updated_file = service.files().update(
        body=file_metadata,
        #uploadType = 'media',
        fileId=fileID,
        #fields = fileID,
        media_body=media).execute()
		"""


	def upload_csv(self):
		file_metadata = {
    'name': 'Twitter Data /// ' +self.FILE_NAME,
    'mimeType': 'application/vnd.google-apps.spreadsheet',
		'parents': 'root'
		}
		self.FILE_PATH = str(self.FILE_PATH)
		print(self.FILE_PATH)
		print(self.FILE_NAME)
		media = MediaFileUpload(self.FILE_PATH,
													mimetype='text/csv',
													resumable=True)

		file = self.drive_service.files().create(body=file_metadata,
																			media_body=media,
																			fields='id').execute()
		print ('File ID: %s' % file.get('id'))
		self.FILE_ID = file.get('id')


	def notify(self):
	
	#Update to retrieve email from web & send generated link too -- Setup mailgun on my domain
		DRIVE_LINK =[]
		#Initialises blank list
		with open("linkholder.txt") as links:
		#Opens txt file 
			DRIVE_LINK = links.read()
			#Reads drive links into list
			os.remove('linkholder.txt')
			#Cleans up residue
			
		PUSH = Email.Notify('chenrymatthews@gmail.com','http://aaaaaaaa', DRIVE_LINK)
		#Sets up email obj with values
		PUSH.send_mail()
		#Sends email


	def share_file(self):

		#self.FILE_ID = '1vyX6NfRykXnYLsaLas1_EAP-XrcEis9fAZM9lR21dpE'
		#cloudPermissions = self.drive_service.permissions().create(fileId=self.FILE_ID,body={'type': 'user', 'role': 'writer', 'emailAddress': userEmail}).execute()

		#Get permissions - if shared write link to file - otherwise creeate link.


		self.drive_service.permissions().create(fileId=self.FILE_ID,body={'type': 'anyone', 'role': 'writer'}).execute()

		#results = self.drive_service.files().list(
        #pageSize=1,fields="nextPageToken, files(id, name, webViewLink)").execute() 
		#temp = results["files"]
		#temp2 = temp[1]
		with open("linkholder.txt", "a") as outfile:
			outfile.write(self.FILE_NAME + " /// https://docs.google.com/spreadsheets/d/"+ self.FILE_ID + " \n\n")

