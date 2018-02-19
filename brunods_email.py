#!/Users/brunods/anaconda3/bin/python
import smtplib
from os.path import basename
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import PyPDF2

def email(text, file=None, filename=None, my_email="brunods1001@gmail.com", my_pass="ytothe2plusx", subject="Daily Reading"):
	# set up smtp server
	if filename is None:
		filename = ''
	text = filename
	s = smtplib.SMTP(host='smtp.gmail.com', port=587)
	s.starttls()
	s.login(my_email, my_pass)
	msg = MIMEMultipart()
	msg['From'] = my_email
	msg['To'] = my_email
	msg['Subject'] = subject + ' ' + filename
	msg.attach(MIMEText(text, 'plain'))

	if type(file) == list:
		new="/Users/brunods/Documents/python_scripts/AAAEMAILDELETE.pdf"
		pdf_cat(file, new)
		with open(new, "rb") as f:
				part = MIMEApplication(f.read(), _subtype="pdf")
		msg.attach(part)
	else:
		with open(file, "rb") as f:
				part = MIMEApplication(f.read(), _subtype="pdf")
		
		#part['Content-Disposition'] = 'attachment; filename="%s"' % "TEST"
		msg.attach(part)

	s.send_message(msg)
	del msg

	print("Email sent!")
	

def pdf_cat(input_files, output_stream):
	pdfWriter = PyPDF2.PdfFileWriter()
	for file in input_files:
		if file.split('/')[-1] not in os.listdir('/'.join(file.split('/')[:-1])):
			continue
		pdfFile = open(file, 'rb')
		pdfReader = PyPDF2.PdfFileReader(file)
		for pageNum in range(pdfReader.numPages):
			pageObj = pdfReader.getPage(pageNum)
			pdfWriter.addPage(pageObj)
		pdfFile.close()
		
	pdfOutputFile = open(output_stream, 'wb')
	pdfWriter.write(pdfOutputFile)
	pdfOutputFile.close()
	

	

	

	'''
    input_streams = []
    try:
        # First open all the files, then produce the output file, and
        # finally close the input files. This is necessary because
        # the data isn't read from the input files until the write
        # operation. Thanks to
        # https://stackoverflow.com/questions/6773631/problem-with-closing-python-pypdf-writing-getting-a-valueerror-i-o-operation/6773733#6773733
        for input_file in input_files:
            input_streams.append(open(input_file))
        writer = PyPDF2.PdfFileWriter()
        for reader in map(PyPDF2.PdfFileReader, input_streams):
            for n in range(reader.getNumPages()):
                writer.addPage(reader.getPage(n))
        writer.write(output_stream)
    finally:
        for f in input_streams:
            f.close()
            '''