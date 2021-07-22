import os
import requests
import gspread
import json
from authlib.integrations.requests_client import AssertionSession
import re

from google.oauth2 import service_account
import googleapiclient.discovery



def create_assertion_session(conf_file, scopes, subject=None):
    with open(conf_file, 'r') as f:
        conf = json.load(f)

    token_url = conf['token_uri']
    issuer = conf['client_email']
    key = conf['private_key']
    key_id = conf.get('private_key_id')

    header = {'alg': 'RS256'}
    if key_id:
        header['kid'] = key_id

    # Google puts scope in payload
    claims = {'scope': ' '.join(scopes)}
    return AssertionSession(
        grant_type=AssertionSession.JWT_BEARER_GRANT_TYPE,
        token_endpoint=token_url,
        issuer=issuer,
        audience=token_url,
        claims=claims,
        subject=subject,
        key=key,
        header=header,
    )

scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
REG_CHECK_RANGE = 'C4:H42'

session = create_assertion_session('srw.json', scopes)

"""SHEETS"""
REGISTRATION_SHEET_URL = 'https://docs.google.com/spreadsheets/d/your_id'
HN_REGISTRATION_SHEET_URL = 'https://docs.google.com/spreadsheets/d/your_id'
HOMEWORK_SHEET_URL = 'https://docs.google.com/spreadsheets/d/your_id'
MED_SHEET_URL = 'https://docs.google.com/spreadsheets/d/your_id'

client = gspread.Client(None, session)
sheet = client.open_by_url(REGISTRATION_SHEET_URL) #default to this url
#sheet1 by default
sheet_index = 0
worksheet = sheet.sheet1

#
def openSheet(url):
    global sheet 
    sheet = client.open_by_url(url)
    
#set worksheet methods
#NOTE: this func copies a worksheet to the FIRST index (0)
def duplicateWorksheetById(index, new_title):
    global worksheet
    worksheet = sheet.get_worksheet(index).duplicate(None, None, new_title)

def chooseWorksheet(index):
    global worksheet 
    worksheet = sheet.get_worksheet(index)
    global sheet_index 
    sheet_index = index
def chooseWorksheetByName(name):
    global worksheet 
    worksheet = sheet.worksheet(name)    
    #add statement to change sheet_index here
def getCurrentWorksheetTitle():
    return worksheet.title
    
def getWorksheetList():
    return sheet.worksheets()    
def getWorksheetTitleList():
    li = getWorksheetList()
    return [i.title for i in li]
    
def clearChecks():
    r = getRange_label(REG_CHECK_RANGE)
    for cell in r:
        setCellValue(cell.row, cell.col, '')

#basically same as parseWeekFolderName
def parseWorksheetTitle(title):
    return parseWeekFormat(title, day_number=6)
#sheet manipulate methods  
def getCell_rc(row,col):
    return worksheet.cell(row,col)
def getCell_label(lbl):
    return worksheet.acell(lbl)    
    
def getColumn(cell):
    return cell.col
def getRow(cell):
    return cell.row

#FIND methods
def findCellByContent(content):
    return worksheet.find(content)
def findCellByPattern(pat):
    date_re = re.compile(r"%s" % (pat,))
    return worksheet.find(date_re)

#cell_range example: 'A1:B5'
def getRange_label(cell_range):
    return worksheet.range(cell_range)
    
#GET VALUE methods
def getCellValue(cell):
    return cell.value
def getRangeValues(cell_range):
    cells = getRange_label(cell_range)
    res =  [cell.value for cell in cells]
    return res

#SET methods
def setCellValue(r, c, val):
    worksheet.update_cell(r, c, val)

"""DRIVE"""

"""Structure of the 12L2 shared drive"""
"""
    BT Tet keo dai - 12L2     #this is the root folder with root_id
      | 
      |-- 02/03-06/03            #this is called week_folder****format: DD/MM-DD/MM
      |      \-- Thu 2        #this is called day_folder*****format: Thu i  , 2<=i<=6
      |      |      \-- Su    #this is called subject_folder
      |      |      |-- Toan
      |      |-- Thu 3
      |      |      \--...
      |      |--...
      |-- 09/03-13/03
      |........
"""

subjects = ["Sử", "Toán", "Văn", "Địa", "Lý", "Hóa", "Tiếng Anh", "Sinh", "GDCD"]
subjects_by_day = [["Sử", "Toán"], ["Văn"], ["Địa", "Lý"], ["Hóa", "Tiếng Anh"], ["Sinh", "GDCD"]]
root_id = 'your_id'
reg_root_id = 'your_id'
hn_reg_root_id = 'your_id'
med_root_id = 'your_id'
med_url='https://drive.google.com/drive/folders/your_id'

creds = service_account.Credentials.from_service_account_file('srw.json', scopes=scopes)
drive = googleapiclient.discovery.build('drive', 'v3', credentials=creds)

def createFolderWithName(name, parent_id):
    metadata = {
    'name': name,
    'parents': [parent_id],
    'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.files().create(body=metadata,
                                    fields='id').execute()
    return folder.get('id')

def listFilesInFolder(folder_id):
    return drive.files().list(q="'{}' in parents".format(folder_id)).execute().get('files', [])
def listFilesInFolderWithPat(folder_id, pat):
    query = "'{}' in parents".format(folder_id)
    query += " and name contains '{}'".format(pat)
    # print(query)
    return drive.files().list(q=query).execute().get('files', [])
def listFilesInFolderWithName(folder_id, name):
    query = "'{}' in parents".format(folder_id)
    query += " and name = '{}'".format(name)
    # print(query)
    return drive.files().list(q=query).execute().get('files', [])
def listFoldersInFolder(folder_id):
    return drive.files().list(q="'{}' in parents and mimeType = 'application/vnd.google-apps.folder'".format(folder_id)).execute().get('files', [])
def listFoldersInFolderWithPat(folder_id, pat):
    query = "'{}' in parents and mimeType = 'application/vnd.google-apps.folder'".format(folder_id)
    query += " and name contains '{}'".format(pat)
    # print(query)
    return drive.files().list(q=query).execute().get('files', [])

def getFolderId(folder):
    return folder.get('id')
def getFolderNamesAndId(folder):
    return [folder.get('name'), folder.get('id')]
def getFileId(f):
    return f.get('id')
def getFileName(f):
    return f.get('name')
def getFileSize(f):
    return f.get('size')

def parseWeekFolderName(week_folder_name):
    return parseWeekFormat(week_folder_name, day_number=5)

def changeFileName(file_id, new_name):
    #API v3 test - WORKING
    #basically, create a new empty "file" f (just metadata actually)
    f = {'name': new_name}   
    return drive.files().update(fileId=file_id, body=f).execute()

    #REST API - doesnt work, not sure why
    # url = "https://www.googleapis.com/drive/v3/files/" + file_id
    
    # headers = {
    #     'Authorization': "Bearer" + creds.token,
    #     'Accept': "application/json",
    #     'Content-Type': "application/json"
    # }
    # body = {
    #     'name': "{}".format(new_name)
    # }
    # response = requests.request("PATCH", url, headers=headers)
    # return response.headers

def updateFile(file_path, dest_file_id, rmv_after_upload):
    print("Update file")
    print(dest_file_id)
    url = "https://www.googleapis.com/upload/drive/v3/files/{}?uploadType=resumable".format(dest_file_id)
    print(url)

    headers = {
        'Content-Length': "38",
        'Content-Type': "application/json",
        'X-Upload-Content-Type': "application/octet-stream",
        'Authorization': "Bearer " + creds.token
        }

    response = requests.request("PATCH", url, headers=headers) 
    
    print(response) 
       
    uri = response.headers['Location']

    #Open the file and stored it in data
    in_file = open(file_path, "rb")  # opening for [r]eading as [b]inary
    data = in_file.read()
    file_size = os.path.getsize(file_path)
    headers = {
        'Content-Length': "{}".format(file_size),
        # 'Content-Type': "image/jpeg"  
    }

    #Send the file in the request
    response = requests.request(
        "PUT", uri, data=data, headers=headers)
    
    print("File uploaded")
    
    if rmv_after_upload:
        os.remove(file_path)
    print("File removed")

def uploadFile(file_path, file_name, dest_folder_id, rmv_after_upload):
    print("Upload file")
    url = "https://www.googleapis.com/upload/drive/v3/files"

    querystring = {"uploadType": "resumable"}

    # payload = '{"name": "test.txt", "parents": ["1roKXszQZVBINfbkNbsl5yFw5AtIIPlk0"]}'
    payload = '{"name": "'+file_name+'", "parents": ["'+dest_folder_id+'"]}'  
    headers = {
        'Content-Length': "38",
        'Content-Type': "application/json",
        'X-Upload-Content-Type': "application/octet-stream",
        'Authorization': "Bearer " + creds.token
        }

    response = requests.request(
        "POST", url, data=payload.encode('utf-8'), headers=headers, params=querystring) 
        
    uri = response.headers['Location']

    #Open the file and stored it in data
    in_file = open(file_path, "rb")  # opening for [r]eading as [b]inary
    data = in_file.read()
    file_size = os.path.getsize(file_path)
    headers = {
        'Content-Length': "{}".format(file_size),
        # 'Content-Type': "image/jpeg"  
    }

    #Send the file in the request
    response = requests.request(
        "PUT", uri, data=data, headers=headers)
    
    print("File uploaded")
    
    if rmv_after_upload:
        os.remove(file_path)
    print("File removed")

#not tested!!
def chunkUpload(file_path, file_name, dest_folder_id):
    file_metadata = {"name":file_name,"parents":[dest_folder_id]}
    media = googleapiclient.discovery.MediaFileUpload(file_path,chunksize=1048576,resumable=True)
    request = drive.files().create(body=file_metadata,media_body=media,fields='id')
    response=None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Uploaded {}%.".format(int(status.progress() * 100)))
    file_uploaded = request.execute()
    if file_uploaded:
        print("Done")

def deleteFile(file_id):
    drive.files().delete(fileId=file_id).execute()

def countFilesInFolder(folder_id):
    return len(listFilesInFolder(folder_id))    

def parseWeekFormat(week_range, day_number): #format: DD/MM-DD/MM
    s = re.split(r'[-/]', week_range)
    if s[1]<s[3]: #if there is change in month
        week_days_end = ['{}/{}'.format(str_f(i), s[3]) for i in range(1,int(s[2])+1)]
        end_of_first_month = int(s[0])+day_number-1-len(range(1,int(s[2])+1))
        week_days_begin = ['{}/{}'.format(str_f(i), s[1]) for i in range(int(s[0]),end_of_first_month+1)]
        return week_days_begin+week_days_end
    else:
        return ['{}/{}'.format(str_f(i), s[3]) for i in range(int(s[0]),int(s[2])+1)]
    

#formatted intToString:  e.g.: 3 -> '03'. Accept i>0 only.
def str_f(i):
    if i < 10:
        return "0"+str(i)
    return str(i)

#main
if __name__ == '__main__':
    # print(creds.token)
    # li = listFoldersInFolderWithPat(root_id, "/03")
    # for item in li:
        # print(item.get('name'))
    # uploadFile('test2.txt', 'test3.txt', root_id, True)
    # print(getColumn(getCell_label('B2')))
    # li = listFilesInFolder('1ZPDOhDRaBiZT__kc0k0upyZCnHfJhcE0')
    # for item in li:
        # print(item.get('name'))
    openSheet(REGISTRATION_SHEET_URL)
    chooseWorksheetByName("dummy")
    setCellValue(1,4,"Thứ 2")
    print(getRangeValues('C1:H1'))
    print(getCellValue(getCell_label('D1')))
