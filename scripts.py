import gg
import os

CANCUOC_URL = "https://docs.google.com/spreadsheets/d/your_id"
ANHTHE_TEN_URL = "https://drive.google.com/drive/folders/your_id"
ANHTHE_TEN_ID = "your_id"
ANHTHE_CMT_URL = ""
ANHTHE_CMT_ID = "your_id"

#break filenames into names
#Nguyen Van A - DDMMYYYY -> 12 Li 2 - Nguyen Van A - DDMMYYYY
 
if __name__ == '__main__':
    files = {} #dict contains [name]:[id]
    
    raw_files = gg.listFilesInFolder(ANHTHE_TEN_ID)
    for raw_file in raw_files:
        new_name = "Lớp " + gg.getFileName(raw_file)
        gg.changeFileName(gg.getFileId(raw_file), new_name)
        print(new_name)
    # print(files)

    

        

    

