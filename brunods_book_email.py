#!/Users/brunods/anaconda3/bin/python
'''
program that emails text
program that converts pdf to text
program that takes in amount to read, wpm and amount of time and returns sized text
program that gives you a wpm

'''

import textract
import time
import os
import brunods_email as bd_email
import brunods_mysql as bd_sql
import PyPDF2


'''
reader with preferences
a reader has a desired time of completion for a book
a reader has a certain number of hours available per day
a reader has a reading_list that can be updated
a reader has preferences
'''
class reader:

	def __init__(self, name, email, wpm, reading_list, minutes_per_day=None, preferences=None):
		self.name = name
		self.email = email
		self.wpm = wpm
		self.reading_list = reading_list
		self.minutes_per_day = minutes_per_day
		self.preferences = preferences
		
	# calculates reading speed getting a random text from a database of text files
	# needs to create new user instance when user gets new wpm...
	# or takes average of tries

	def get_new_wpm(self):
		text_file = get_random_text()
		print("Reading from " + text_file)
		w = [get_wpm(text_file)]
		q = input("You read: " + str(w) + " words per minute. Try again? y or n?")
		# possibly use regex here
		while q is "y" or q is "yes" or q is "YES" or q is "Yes":
			text_file = get_random_text()
			print("Reading from " + text_file)
			w.append(get_wpm(text_file))
			q = input("You read: " + str(w) + " words per minute. Try again? y or n?")
		self.wpm = sum(w) / len(w)
		print("Your new average reading speed is: " + str(self.wpm) + " wpm")

		
class book:
	
	def __init__(self, name, file_path, file, bookmark=0, word_start=0, book_path="/Users/brunods/documents/book_pages/", 
		num_words=None, num_pages=None, author=None):
		self.name = name
		self.file_path = file_path
		self.file = file
		self.bookmark = bookmark
		self.word_start = word_start
		self.book_path = book_path
		self.num_pages = self.initialize_num_pages()
		self.words_per_page, self.all_text = self.initialize_words_per_page()
		self.num_words = self.initialize_num_words()
		self.author = author

		if bookmark is not 0:
			self.word_start = sum([self.words_per_page[i] for i in range(bookmark)])

	def initialize_num_words(self):
		text_file = pdf_to_txt(self.file_path + self.file)
		text = text_to_str(text_file)
		words = get_num_words(text)
		return words

	def initialize_num_pages(self):
		pdfFileObj = open(self.file_path + self.file, 'rb')
		pdfReader = PyPDF2.PdfFileReader(pdfFileObj, strict=False)
		num_pages = pdfReader.numPages
		pdfFileObj.close()
		return num_pages

	def initialize_words_per_page(self):
		words_per_page = []
		all_text = []
		pdfFileObj = open(self.file_path + self.file, 'rb')
		pdfReader = PyPDF2.PdfFileReader(pdfFileObj, strict=False)
		for page in range(self.num_pages):
			file_name = self.book_path + self.file.strip('.pdf') + str(page) + ".pdf"
			if os.path.isfile(file_name) is not True:
				pageObj = pdfReader.getPage(page)
				pdfWriter = PyPDF2.PdfFileWriter()
				pdfWriter.addPage(pageObj)
				pdfOutputFile = open(file_name, 'wb')
				pdfWriter.write(pdfOutputFile)
				pdfOutputFile.close()
				page_text = textract.process(file_name).decode("utf-8")
				#print("words in page: ", len(str(page_text).split(' ')))
				words_in_page = len(page_text.split(' '))
				all_text.append(page_text)
				words_per_page.append(words_in_page)
			else:
				page_text = textract.process(file_name).decode("utf-8")
				#print("words in page: ", len(str(page_text).split(' ')))
				words_in_page = len(page_text.split(' '))
				all_text.append(page_text)
				words_per_page.append(words_in_page)

		pdfFileObj.close()
		return words_per_page, all_text

		

	def __repr__(self):
		return self.name

	# gets a chunk of the book and returns text; saves to txt
	# chunk = time/day * wpm
	# time/day is a reader attribute
	# returns words per day
	def write_chunk(self, wpm, minutes_per_day, save_file=True):
		wpd = minutes_per_day * wpm
		word_end = self.word_start + wpd
		text_file = pdf_to_txt(self.file, save=save_file)
		text = text_to_str(text_file)
		text_list = text.split(' ')
		'''
		with open("BRUNO_TEST2.txt", 'w') as f:
			for w in text_list[self.bookmark:wpd]:
				f.write(w + " ")
		'''
		file_email = self.book_path + self.file.strip(".pdf") + ".pdf"
		bd_email.email(text=text, file=file_email)
		print("Number of words to read: " + str(len(text_list)))
		return text_list
	
	def email_pdf_pages(self, wpm, minutes_per_day, save_file=True):
		wpd = minutes_per_day * wpm
		word_end = self.word_start + wpd
		file_email = []
		original_start = self.word_start
		original_bookmark = self.bookmark
		while self.word_start < word_end:
			try:
				text_file = pdf_to_txt(self.book_path + self.file.strip(".pdf") + str(self.bookmark) + ".pdf")
			except:
				print("could not convert pdf to txt")
			text = text_to_str(text_file)
			print(text[0:10])
			text_list = text.split(' ')
			words_in_page = len(text_list)
			print("words in page ", self.bookmark, ": ", words_in_page)
			print("ending on ", word_end)
			self.word_start += words_in_page
			file_email.append(self.book_path + self.file.strip(".pdf") + str(self.bookmark) + ".pdf")
			self.bookmark += 1
		self.word_start = word_end
		bins = enumerate([sum(self.words_per_page[0:i]) for i,j in enumerate(self.words_per_page)])
		for a_bin, start in bins:
			if self.word_start >= start:
				self.bookmark = a_bin
		print("files to email: ", file_email)
		try:
			if word_end > self.num_words:
				print("Ran out of pages! Now what?")
				print("Words remaining: ", word_end - self.num_words)
			bd_email.email(text=text, file=file_email)
			
		except:
			self.word_start = original_start
			self.bookmark = original_bookmark
			print("I tried!")
			Exception("Could not send email")


'''
reading list made of books
need to make sure can only append book objects
'''
class reading_list:

	def __init__(self, books, num_books=None):
		self.list = []
		if books is not None:
			if type(books) == list:
				self.list += books
			else:
				self.list.append(books)

	def __getitem__(self, idx):
		return self.list[idx]
	
	def __iter__(self):
		return self.list.__iter__()

	def __repr__(self):
		return "this reading list consists of: " + str(self.list)

	def add(self, book):
		return self.list.append(book)
		

def get_wpm(text_file):
		text = text_to_str(text_file)
		input("Hit enter to start. Then hit enter when finished."
			" Please read at normal pace")
		print(text)
		start = time.time()
		input()
		end = time.time()
		dt = (end - start) / 60 # elapsed time in minutes
		words = get_num_words(text)
		w = words / dt
		print("wpm: " + str(w) + " wpm")
		return w


# functions

# convert pdf to text and return text
def pdf_to_txt(pdf_file, save=True):
	text = textract.process(pdf_file).decode("utf-8") 
	if save is not True:
		return text
	else:
		# save text here
		text_file = pdf_file[:-3] + "txt"
		if os.path.isfile(text_file) is not True:
			with open(text_file, 'w') as f:
				f.write(text)
			return text_file
		else:
			return text_file
			override = input("File {} exists... override? y or n".format(pdf_file))
			if override is "y" or override is "Y" or override is "Yes":
				with open(text_file, 'w') as f:
					f.write(text)
					print("File was overwritten")
				return text_file
			else:
				print("File was not overwritten")
				return text_file
			
# takes in a text file and outputs a string containing text
def text_to_str(text_file):
	if text_file.endswith(".txt"):
		with open(text_file) as f:
			text = f.read()
		return text
	else:
		Exception("Please input text file")



# takes in a text file and outputs num of words
def get_num_words(text):
	words = text.split(" ")
	return len(words)

def get_random_text():
	return "amin.txt"



if __name__ == "__main__":
	print("This is the main script")

	me = bd.reader("Bruno", "gmail", 800, None, 10, None)

	rules_of_ml = bd.book("Rules of ML", "/Users/brunods/"
		"Library/Mobile Documents/com~apple~CloudDocs/Desktop/"
		"no clutter/Texts/rules_of_ml.pdf")
	rules_of_ml.write_chunk(me.wpm, me.minutes_per_day)

	