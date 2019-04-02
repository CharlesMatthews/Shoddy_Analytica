from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials


def DAYTONA(FILE_PATH, FFN):
    gauth = GoogleAuth()
    scope = ['https://www.googleapis.com/auth/drive']
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    drive = GoogleDrive(gauth)


    fid = "1PRyStjpIFY3RnoAnJ3ZPOgiB-18j3ogh"
    fname = 'SA - '+FFN

    file1 = drive.CreateFile({'title': fname, "parents": [{"kind": "drive#fileLink", "id": fid}]})
    file1.SetContentFile(FILE_PATH)
    file1.Upload({'convert': True})

    permission = file1.InsertPermission({
                            'type': 'anyone',
                            'value': 'anyone',
                            'role': 'reader'})

    print(file1['alternateLink'])
    return file1['alternateLink']
