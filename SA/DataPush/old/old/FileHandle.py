import os # OS TOOLS
import glob #Filename pattern matching
import time #Time module - Sleep functions etc.
import sqlite3 #SQLITE3 DB handling
import csv #CSV file handling
from pathlib import Path #Gets Filepaths - Used to get System Home.


from DataPush import KingPush # Datapushing code after scraping + prepping data


class FileManager:
	def __init__(self,TARGETS):
	#Initialises Filemanager Class
		self.TARGETS = TARGETS
		#Targets to Push 
		self.DB = self.database_to_csv()
		#Calls db to csv code to ensure all is prepped for action
		self.FILE_NAMES,self.FILE_PATHS = self.get_csv_files()
		#Gets Filenames and filepaths of CSV files ready for export


	def database_to_csv(self):
	#ConvertS .DB file to CSV ready for export
		print(self.TARGETS)
		#Print names of targets to export
		for ITEM in self.TARGETS:
		#Repeat for all accounts
			BASE = "@"+ITEM
			DBNAME = BASE+".db"
			print(DBNAME)
			os.chdir(str(Path.home())+"/Data/SQL_Databases/"+BASE+"/")
			#Change directory to Database Location
			with sqlite3.connect(DBNAME) as connection:
			#Open a sqlite3 connetcion to specified DB
				c = connection.cursor()
				table_names = c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
				#Get names of all the tables present in the database
				for extract in table_names:
				#Extract tablename data from unneeded data
					#print("extract")
					#print(extract)

					for table_name in extract:
					#Extract tablename data from unneeded data & repeat for all tables in DB#
						directory = str(Path.home())+"/Data/CSV_Files/"+BASE+"/"
						#Directo
						if not os.path.exists(directory):
						#If folder for CSV files does not exist
							os.makedirs(directory)
							#Make folder
						os.chdir(directory)
						#Change directory to CSV data folder
						csvWriter = csv.writer(open(BASE+"_"+table_name+".csv", "w"))
						#Initialise CSV writer with file naming
						c.execute("SELECT * FROM "+table_name)
						#Get all data from the table
						rows = c.fetchall()
						#Extract to rows
						csvWriter.writerows(rows)
						#Write data to CSVs
						
			os.chdir(str(Path.home()))
			#Change directory back to base DIR

		return True
		#Return true (Worked!)


	def get_csv_files(self):
	#Gets CSV file names & Filepaths 
		FILE_NAMES =[]
		FILE_PATHS = []
		#Initilse empty lists

		for ITEM in self.TARGETS:
		#Repeat for all requested Accts
			BASE = "@"+ITEM
			try:
				os.chdir(str(Path.home())+"/Data/CSV_Files/"+BASE)
			except:
				print(BASE+ ".db failed to export csv files / did not exist")
			for file in glob.glob("*.csv"):
				FILE_NAMES.append(file)
		os.chdir(str(Path.home()))	

		for FILE in FILE_NAMES:
			FILE_PATHS.append(os.getcwd()+"/Data/CSV_Files/"+BASE+"/"+FILE)
			print(FILE)
			print(FILE_PATHS)
		return FILE_NAMES, FILE_PATHS


	def file_handle(self):
		for ITEM in self.TARGETS:
		#Repeat for every listed acct 
			CSVNAME = "@"+ITEM+".csv"

			if CSVNAME in self.FILE_NAMES:
				#  
				index = self.FILE_NAMES.index(CSVNAME)
				#Get position of Filename within list of Filenames

				if os.stat(self.FILE_PATHS[index]).st_size != 0:
					#If file is not empty do this:
					PUSHA = KingPush.Gdrive(self.FILE_PATHS[index],CSVNAME)
					#Create new Object , parsing Filepath and CSVNAME	
					
					#PUSHA.drive_purge()  
					#[Purge Drive files] 

					if PUSHA.filecheck(self.FILE_PATHS[index]) == True:
					#If file already exists on Gdrive do this:

						PUSHA.update_csv()
						########WORK ON THIS so it actually works :/ ^^
						#Update existing GSheets file 
						PUSHA.share_file()
						#Get Gdrive sharing link for data file
					else:
					#Otherwise
						PUSHA.upload_csv()
						#Push files to GDrive as a new file 
						PUSHA.share_file()
						#Get Gdrive sharing link for data file
					time.sleep(3)
					#Wait 3 seconds [[REMOVE FOR deployment]]
					print(PUSHA.filecheck(self.FILE_PATHS[index]))
					#Print result if file already exists on Gdrive (T/F)

				else:
				#Otherwise if csv files are empty
					print("No data in file " + CSVNAME)
					#Msg no data
					os.remove(self.FILE_PATHS[index])
					#Remove file 
			else:
			#Otherwise if file is not in targets ( Will occur when no account)
				print("Invalid Target")
		try:
		#Try to execute user notify
			PUSHA.notify()
			#Sends email to user with links to G Sheets files + DB on server!
			
		except:
		#Notify will fail when no object hence:
			print("No valid targets entered - please rerun")
		try:
		#Try to cleanup files which will expose API Keys
			os.remove('client_secrets.json')
			print("Secrets File Cleaned")
		#Success
		except:
			print("Secrets File did not exist/ Could not remove")
		#Failure