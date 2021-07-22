import os
import gg
import random
from datetime import datetime, timedelta
from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = b'your_key'

#constants and variables
name_range = 'B4:B42'
reg_day_name_range = 'C1:M1'
hn_reg_day_name_range = 'C1:H1'
register_symbol = 'x'
day_name_eng_to_vie = {
    'Mon': "Thứ 2",
    'Tue': "Thứ 3",
    'Wed': "Thứ 4",
    'Thu': "Thứ 5",
    'Fri': "Thứ 6",
    'Sat': "Thứ 7",
    'Sun': "Chủ nhật"
}

"""--------------------------------------------"""
"""_______________VIEWERS______________________"""
"""INDEX"""
@app.route('/')
def index():
    # print('Hey it\'s Index here')

    return render_template('index.html', 
                            server_time=display_time().strftime('%d/%m/%Y %H:%M'))

"""--------------------------------------------"""
"""TV REGISTRATION"""
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    week_folder_id=0 #dummy value
    
    submit_date=display_time(14) #######reset at 14 o'clock
    submit_date_pat = submit_date.strftime('%d/%m')
    submit_date_dmy = submit_date.strftime('%d/%m/%Y')
    date_filename = submit_date.strftime('%d%m')
    
    if int(get_day_name(submit_date,14)) == 0:
        return redirect(url_for('registration_closed'))
    
    gg.openSheet(gg.REGISTRATION_SHEET_URL)
    gg.chooseWorksheet(0) #choose the latest worksheet, of course
    
    #generate new sheet and drive folder
    if int(get_day_name(submit_date,14)) == 1:
        week_name = '{}-{}'.format(submit_date.strftime('%d/%m'), 
                                     (submit_date + timedelta(days=5)).strftime('%d/%m'))
        if gg.getCurrentWorksheetTitle() != week_name: #if the sheet was not created
            gg.duplicateWorksheetById(-1, week_name)  #duplicate from the dummy worksheet
            #set day names
            day_names = generateDayNameRow(submit_date, 5)
            cell_range = gg.getRange_label(reg_day_name_range)
            for i in range(0,len(cell_range),2):
                gg.setCellValue(cell_range[i].row, cell_range[i].col, day_names[int(i/2)])
        
        if len(gg.listFoldersInFolderWithPat(gg.reg_root_id, week_name))==0:
            week_folder_id = gg.createFolderWithName(week_name, gg.reg_root_id)
            for i in range(2,8):
                gg.createFolderWithName("Thứ {}".format(i), week_folder_id)
    
    #generate html elements
    #name list
    dropdown_content = gg.getRangeValues(name_range)
    #subject list
    day_row = 1 #kinda constant
    subject_row = 3 #kinda constant
    day_cell = gg.findCellByPattern(submit_date_pat)
    day_col = gg.getColumn(day_cell)
    subjects_today = {}
    subjects_num = 3 if (int(get_day_name(submit_date,14)) == 6) else 2
    for i in range(0,subjects_num):
        subjects_today[gg.getCellValue(gg.getCell_rc(subject_row,day_col+i))] = [subject_row,day_col+i]
    dropdown_subjects = [key for key in subjects_today] #display this
    
    #find folder name
    week_begin = (submit_date - timedelta(days=(int(get_day_name(submit_date,14))-1))).strftime('%d/%m')
    week_end = (submit_date + timedelta(days=(6-int(get_day_name(submit_date,14))))).strftime('%d/%m')
    week_folder_name = week_begin+'-'+week_end
    dest_folder_name = day_name_eng_to_vie[submit_date.strftime('%a')]
    # week_folder_id = gg.listFoldersInFolderWithPat(gg.reg_root_id, week_folder_name)[0].get('id')
    if week_folder_id == 0: #to reduce some work
        week_folder_id = gg.listFoldersInFolderWithPat(gg.reg_root_id, week_folder_name)[0].get('id')
    dest_folder_id = gg.listFoldersInFolderWithPat(week_folder_id, dest_folder_name)[0].get('id')


    if request.method=='POST':
        register_subject = dropdown_subjects[int(request.form['subject_index'])]
        register_name = dropdown_content[int(request.form['name_index'])]
        
        row = gg.getRow(gg.findCellByContent(register_name))
        col = subjects_today[register_subject][1]

        # if not_registered(request.form['name_index'], submit_date_pat):
        f = request.files['file']
        file_type = os.path.splitext(f.filename)[1]
        # raw_file_name = some_random_name+file_type
        raw_file_name = "f_"+str(int(random.random()*1000))+file_type
        f.save(secure_filename(raw_file_name))
        
        # file_name = '[12L2]{}-{}-{}'.format(register_name,date_filename,register_subject) + '.{}'.format(f.filename.split('.')[1])
        file_name = '[12L2]{}-{}-{}'.format(register_name,date_filename,register_subject) + file_type
        existed_files = gg.listFilesInFolderWithName(dest_folder_id, file_name)
        
        #perform upload/update, then delete temp file
        if len(existed_files) == 0:
            gg.uploadFile(raw_file_name, file_name, dest_folder_id, True)
        else:
            gg.updateFile(raw_file_name, existed_files[0].get('id'), True)            
        gg.setCellValue(row, col, register_symbol)
        
        print('Success...Redirecting...')
        return redirect(url_for('success_registration'))

    return render_template('registration.html',
                            submit_date=submit_date,
                            submit_date_dmy=submit_date_dmy,
                            len_dropdown_content=len(dropdown_content),
                            dropdown_content=dropdown_content,
                            dropdown_subjects=dropdown_subjects,
                            len_dropdown_subjects=len(dropdown_subjects))

@app.route('/success_registration')
def success_registration():
    submit_date_dmy= display_time(14).strftime('%d/%m')
    return render_template('success_registration.html',
                            submit_date_dmy=submit_date_dmy)

@app.route('/fail_registration')
def fail_registration():
    submit_date_dmy= display_time(14).strftime('%d/%m')
    return render_template('fail_registration.html',
                            submit_date_dmy=submit_date_dmy)

@app.route('/registration/closed')
def registration_closed():
    return render_template('registration_closed.html')
    
@app.route('/registration/help')
def registration_help():
    return render_template('registration_help.html')

"""--------------------------------------------"""        
"""HANOISTUDY REGISTRATION"""
@app.route('/hnstudy', methods=['GET', 'POST'])
def hn_registration():
    submit_date=display_time() ############reset at 0 o'clock
    submit_date_pat = submit_date.strftime('%d/%m')
    submit_date_dmy = submit_date.strftime('%d/%m/%Y')
    date_filename = submit_date.strftime('%d%m')
    
    if int(get_day_name(submit_date)) == 0:
        return redirect(url_for('registration_closed')) #same template as [registration]
    
    gg.openSheet(gg.HN_REGISTRATION_SHEET_URL)
    gg.chooseWorksheet(0) #choose the latest worksheet, of course
    
    #generate new sheet and drive folder
    if int(get_day_name(submit_date)) == 1:
        week_name = '{}-{}'.format(submit_date.strftime('%d/%m'), 
                                     (submit_date + timedelta(days=5)).strftime('%d/%m'))
        if gg.getCurrentWorksheetTitle() != week_name: #if the sheet was not created
            gg.duplicateWorksheetById(-1, week_name)  #duplicate from the dummy worksheet
            #set day names
            day_names = generateDayNameRow(submit_date, 5)
            cell_range = gg.getRange_label(hn_reg_day_name_range)
            for i in range(len(cell_range)):
                gg.setCellValue(cell_range[i].row, cell_range[i].col, day_names[i])
    
    #generate html elements
    #name list
    dropdown_content = gg.getRangeValues(name_range)
    
    if request.method=='POST':
        register_name = dropdown_content[int(request.form['name_index'])]
        
        row = gg.getRow(gg.findCellByContent(register_name))
        col = gg.getColumn(gg.findCellByPattern(submit_date_pat))

        gg.setCellValue(row, col, register_symbol)
        
        print('Success...Redirecting...')
        return redirect(url_for('hn_success_registration'))

    return render_template('hn_registration.html',
                            submit_date=submit_date,
                            submit_date_dmy=submit_date_dmy,
                            len_dropdown_content=len(dropdown_content),
                            dropdown_content=dropdown_content)

@app.route('/hnstudy/success_registration')
def hn_success_registration():
    submit_date_dmy= display_time().strftime('%d/%m')
    return render_template('hn_success_registration.html',
                            submit_date_dmy=submit_date_dmy)
    
"""--------------------------------------------"""
"""FILE UPLOAD"""
@app.route('/file_upload', methods=['GET', 'POST'])
def file_upload_home():
    week_folders = gg.listFoldersInFolder(gg.root_id)
    week_folders_metadata = [gg.getFolderNamesAndId(f) for f in week_folders]
    week_folders_names = [wfm[0] for wfm in week_folders_metadata]
    len_week_folders_names = len(week_folders_names)
    week_folders_ids = [wfm[1] for wfm in week_folders_metadata]
    
    if request.method=='POST':
        week_folder_index = int(request.form['week_folder_index'])
        session['week_folder_name'] = week_folders_names[week_folder_index]
        session['week_folder_id'] = week_folders_ids[week_folder_index]
        return redirect(url_for('select_day'))
        
    return render_template('file_upload_home.html', week_folders_names=week_folders_names,
                            len_week_folders_names = len_week_folders_names)
    
@app.route('/file_upload/select_day', methods=['GET', 'POST'])
def select_day():
    week_folder_name = session['week_folder_name']
    #display this
    days_selections = gg.parseWeekFolderName(week_folder_name)
    len_days_selections = len(days_selections)
    
    if request.method=='POST':
        session['day'] = days_selections[int(request.form['day_index'])]
        session['day_index'] = request.form['day_index']
        
        return redirect(url_for('file_upload'))
        
    return render_template('file_upload_sel_day.html',
                            days_selections=days_selections,
                            len_days_selections=len_days_selections)

@app.route('/file_upload/select_day/upload', methods=['GET', 'POST'])    
def file_upload():
    #just retrieving data
    week_folder_name = session['week_folder_name']
    week_folder_id = session['week_folder_id']
    day_index = int(session['day_index'])
    day = session['day']
    subjects_today = gg.subjects_by_day[day_index]
    len_subjects_today=len(subjects_today)
    #real processing
    day_name = str(day_index+2) #0 - Mon, 1 - Tue, 2 - Wed...
    
    gg.openSheet(gg.HOMEWORK_SHEET_URL)
    gg.chooseWorksheetByName(week_folder_name)
    student_name_list = gg.getRangeValues(name_range)
    len_student_name_list = len(student_name_list)
    
    if request.method == 'POST': #handle file, name, subject
        #FIRST, save the file to current folder
        f = request.files['file']
        # f.save(secure_filename(f.filename))
        file_type = os.path.splitext(f.filename)[1]
        raw_file_name = "f_"+str(int(random.random()*1000))+file_type
        f.save(secure_filename(raw_file_name))
        #SECOND, retrieve student_name and subject
        student_name = student_name_list[int(request.form['student_name'])]
        subject = subjects_today[int(request.form['subject'])]
        #THIRD, compose the filename, destination folder
        day_folder = gg.listFoldersInFolderWithPat(week_folder_id, day_name)[0]
        # print("day_folder found! "+day_folder.get('id'))
        # print("subject: "+subject)
        subject_folder_id = gg.listFoldersInFolderWithPat(day_folder.get('id'),subject)[0].get('id')
        file_name = '[12L2{}]{}'.format(subject,student_name) + '.{}'.format(f.filename.split('.')[1])
        session['file_name'] = file_name
        #FOURTH, upload the file, then remove it from server
        gg.uploadFile(raw_file_name, file_name, subject_folder_id, True)
        #FIFTH, check in the sheet
        row = gg.getRow(gg.findCellByContent(student_name))
        col = gg.getColumn(gg.findCellByContent(subject))
        gg.setCellValue(row, col, register_symbol)
        #FINAL, redirect
        return redirect(url_for('file_upload_success'))
    
    return render_template('file_upload_upload.html',
                            subjects_today=subjects_today,
                            len_subjects_today=len_subjects_today,
                            student_name_list=student_name_list,
                            len_student_name_list=len_student_name_list)

@app.route('/file_upload/select_day/upload/success')
def file_upload_success():
    
    return render_template('file_upload_success.html',
                            file_name=session['file_name'])

"""--------------------------------------------"""
"""MED"""
@app.route('/med', methods=['GET','POST'])
def med_home():
    gg.openSheet(gg.MED_SHEET_URL)
    gg.chooseWorksheet(0) #choose the latest worksheet, of course
   
    dropdown_content = gg.getRangeValues(name_range)
    
    gg.listFilesInFolder(gg.med_root_id) #just ping-ing

    if request.method=='POST':
        student_name = dropdown_content[int(request.form['name_index'])]
        row = gg.getRow(gg.findCellByContent(student_name))
        col = 3
        
        f = request.files['file']
        file_type = os.path.splitext(f.filename)[1]
        # raw_file_name = "temp"+file_type
        raw_file_name = "f_"+str(int(random.random()*1000))+file_type
        f.save(secure_filename(raw_file_name))
        
        file_name = '[12L2]{}'.format(student_name) + '.{}'.format(f.filename.split('.')[1])
        
        gg.uploadFile(raw_file_name, file_name, gg.med_root_id, True)
        gg.setCellValue(row, col, register_symbol)
        
        print('Success...Redirecting...')
        return redirect(url_for('med_success'))

    return render_template('med_home.html',
                            len_dropdown_content=len(dropdown_content),
                            dropdown_content=dropdown_content)

@app.route('/med/med_success')
def med_success():
    return render_template('med_success.html')
"""--------------------------------------------"""
"""OTHER PAGES"""
@app.route('/CH34T')
def cheat_site():
    submit_date = display_time()
    submit_date_pat = submit_date.strftime('%d/%m')
    
    return render_template('CH34T.html')

@app.route('/test')
def test():
    return render_template('test.html')

"""--------------------------------------------"""
"""HELPER METHODS"""
#formatted intToString:  e.g.: 3 -> '03'. Accept i>0 only.
def str_f(i):
    if i < 10:
        return "0"+str(i)
    return str(i)

def listToStr(l):
    res = ""
    for i in l:
        res+=i
    return res
    

#starting_day: a datetime object
def generateDayNameRow(starting_day, days_following):
    res=[]
    for i in range(0,days_following+1):
        res.append("Thứ " + str(i+2) + "({})".format((starting_day+timedelta(days=i)).strftime('%d/%m')))
    return res
    
#time in UTC+7, for use in remote server
def current_time():
    return datetime.now()+timedelta(hours=7)

def display_time(reset_hour=0):
    #use datetime.now if running locally
    # t = current_time()
    t = datetime.now()
    
    hour = int(t.strftime('%H'))
    if hour >= reset_hour:
        return t
    else:
        return t - timedelta(days=1)

def get_day_name(arg=None, reset_hour=0):
    if arg != None:
        return arg.strftime('%w')
    t = display_time(reset_hour).strftime('%w')
    return t

def a_random_day(days_from_today):
    return current_time() + timedelta(days=days_from_today)

#run some exciting functions here
print('Server start time:')
print(datetime.now())
