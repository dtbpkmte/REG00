# REG00 - A student management website 

What is it?
-----------

A student management website, originally designed to enhance remote learning experience during Covid 19. More specifically, it can do these things:
- Monitor students' attendance: the website has an interface for students to check in every school day
- Monitor students' assignment progress: when students submit their work to the website, the files will be uploaded to Google Drive, and those students will be marked as complete in Google Sheets. Teachers will know who finished and who did not and other statistics by examining the spreadsheet.
- Monitor other file uploads: students can submit medical records, forms, etc. and the activities are recorded in Google Sheets

The most important feature of this website is to manage the work submitted by students 

Why did I make it?
------------------

In 2020, when I was grade 12 at high school, Covid 19 came so all students had to study remotely from home. At first, it is quite hard for my teachers to monitor students, i.e. to know who did not attend class, who did not submit homework, etc. I was the one who helped them by counting submissions and mark into a spreadsheet. It was not only a tedious job but also prone to human errors.

After some searching, I found that Google provides API to use Docs and Sheets. I decided to create a webapp to automate my tasks, also to learn coding web. I hosted the app on Heroku, and it worked very well. A few days coding saved me the whole rest of the school year.

How does it work?
-----------------

This webapp uploads files to Google Drive and record submissions into Google Sheets using Google's API. It creates a new sheet every week to store information of each week.

The techniques I was using were Python, Flask, Google Drive API, Google Sheets API, REST API. I used both PythonAnywhere and Heroku for hosting.

Project status
--------------

This project was completed in 2020, and the webapp was fully working. A limitation is that I had to change source code each time I wanted to add a new Drive, so that's a bit inconvenient.

This project is archived for future reference.