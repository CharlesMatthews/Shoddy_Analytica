import os
import json
class Gauth:
	def build_client_secret():


		G_Client_Params = ["G_TYPE","G_PROJECT_ID","G_PRIVATE_KEY_ID","G_PRIVATE_KEY","G_CLIENT_EMAIL","G_CLIENT_ID","G_AUTH_URL","G_TOKEN_URI","G_AUTH_PROVIDER_X509_CERT_URL","G_CLIENT_X509_CERT_URL"]
		G_Client = {}

		for item in G_Client_Params:
			G_Client[str.lower(item[2:])] = os.getenv(item)

		with open("client_secrets.json", "w") as outfile:
			outfile.write("{")
			for item in G_Client:
				if item != "client_x509_cert_url":
					outfile.write("\n  \""+item+"\": \""+G_Client[item]+"\",")
				else:
					outfile.write("\n  \""+item+"\": \""+G_Client[item]+"\"\n}\n")

	def credentials_from_file():
			#Retrieves a credentials object token using a service account ///  Docs vvvv
			#https://developers.google.com/identity/protocols/OAuth2ServiceAccount
			from google.oauth2 import service_account
			import googleapiclient.discovery

			# https://developers.google.com/identity/protocols/googlescopes#drivev3

			SCOPES = [
					'https://www.googleapis.com/auth/drive'
			]
			Gauth.build_client_secret()
			SERVICE_ACCOUNT_FILE = os.getcwd()+'/client_secrets.json'
			#print(SERVICE_ACCOUNT_FILE)


			credentials = service_account.Credentials.from_service_account_file(
							SERVICE_ACCOUNT_FILE, scopes=SCOPES)

			return credentials
