import csv

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload


import WEB.utils.utils as ut

import os
import secrets
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from DataPush import Auth


class Gdrive:
	def __init__(self, FILE_NAME, FILE_PATH, USER_EMAIL):
		self.credentials = Auth.Gauth.credentials_from_file()
		self.drive_service = discovery.build('drive', 'v3', credentials=self.credentials)
		self.FILE_PATH = FILE_PATH
		self.FILE_NAME = FILE_NAME
		self.FILE_ID =  'Null'
		self.USER_EMAIL = USER_EMAIL

	def upload_csv(self):
		time = str(time.strftime("%H:%M:%S"))
		file_metadata = {'name': 'Twitter Data /// ' + self.FILE_NAME + time, 'mimeType': 'application/vnd.google-apps.spreadsheet', 'parents': '1PRyStjpIFY3RnoAnJ3ZPOgiB-18j3ogh'}
		self.FILE_PATH = str(self.FILE_PATH)
		media = MediaFileUpload(self.FILE_PATH, mimetype='text/csv', resumable=True)

		file = self.drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()
		print ('File ID: %s' % file.get('id'))
		self.FILE_ID = file.get('id')


	def share_file(self):
		self.drive_service.permissions().create(fileId=self.FILE_ID,body={'type': 'user', 'role': 'writer', 'emailAddress': self.USER_EMAIL}).execute()

		self.drive_service.permissions().create(fileId=self.FILE_ID,body={'type': 'anyone', 'role': 'writer'}).execute()

		link = "https://docs.google.com/spreadsheets/d/"+ self.FILE_ID
		return link



class PUSHA:
	def __init__(self, author, tok):
		self.utoken = tok
		self.author = author
		self.dataprep = self.database_to_csv()


	def database_to_csv(self):
		collist = ut.getcollist("tweets")
		aid = ut.getauthoridhandle(self.author)
		data = db.execute("SELECT * from tweets where  authorid =  :aid", {"aid": aid}).fetchall()


		csvWriter = csv.writer(open(self.author+".csv", "w", encoding="utf-8"))
		csvWriter.writerows(data)


	def TweetExport(self):
		USER_EMAIL = db.execute("SELECT email from users where token =  :utok", {"utok": self.utoken}).fetchone()

		CSVFILE = os.getcwd()+ self.author + ".csv"

		DAYTONA = Gdrive(self.author,CSVFILE,USER_EMAIL[0])
		DAYTONA.upload_csv()
		print(self.author)
		print(CSVFILE)
		print(USER_EMAIL[0])

		link = DAYTONA.share_file()

		return link
