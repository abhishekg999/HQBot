# TODO: add name recognition, check for word combinations in handler2, thread handler2 with a separate dict


from bs4 import BeautifulSoup
from PIL import Image
import urllib

import unidecode
import pyscreenshot
import sys, os
import socket as cv2 #FIX NO NEED SOCKET
#import pytesseract
import argparse
import webbrowser

from google import google
import json

import threading

print_lock = threading.Lock()

negative_words = []
remove_words = []


def screen_grab(to_save):
	im = pyscreenshot.grab(bbox=(40, 205, 485, 640))
	im.save(to_save)


def read_screen():
	screenshot_file = "Screens/to_ocr.png"
	screen_grab(screenshot_file)

	# load the image
	image = cv2.imread(screenshot_file)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# store grayscale image as a temp file to apply OCR
	filename = "Screens/{}.png".format(os.getpid())
	cv2.imwrite(filename, gray)

	text = pytesseract.image_to_string(Image.open(filename))
	# os.remove(filename)
	# os.remove(screenshot_file)

	return text


def parse_question():
	text = read_screen()
	lines = text.splitlines()
	question = ""
	options = list()
	flag = False

	for line in lines:
		if not flag:
			question = question + " " + line

		if '?' in line:
			flag = True
			continue

		if flag:
			if line != '':
				options.append(line)

	return question, options


def loadlists():
	global negative_words, remove_words
	remove_words = json.loads(open("settings.json").read())["remove_words"]
	negative_words = json.loads(open("settings.json").read())["negative_words"]


def split_string(source):
	splitlist = ",!-.;/?@ #"
	output = []
	atsplit = True

	for char in source:
		if char in splitlist:
			atsplit = True
		else:
			if atsplit:
				output.append(char)
				atsplit = False
			else:
				output[-1] = output[-1] + char
	return output


def smart_answer(content, qwords, inc):
	zipped = zip(qwords, qwords[1:])
	points = 0

	for el in zipped:
		if content.count(el[0] + " " + el[1]) != 0:
			points += inc
	return points


def handler(words, o, neg):
	global points

	content = ""
	maxo = ""
	maxp = - sys.maxsize

	o = o.lower()
	original = o

	temp = 0

	o += ' site:wikipedia.org'

	search_wiki = google.search(o, 1)
	link = search_wiki[0].link

	with print_lock:
		print (link)

	content = urllib.request.urlopen(link).read()

	soup = BeautifulSoup(content, "lxml")

	page = soup.get_text().lower()

	for word in words:
		temp = temp + page.count(word)

	for word in search_wiki[0].description:
		if word in words:
			temp += 1000

	temp += smart_answer(page, words, 700)

	link = search_wiki[1].link
	content = urllib.request.urlopen(link).read()

	soup = BeautifulSoup(content, "lxml")

	page = soup.get_text().lower()

	for word in words:
		temp = temp + page.count(word.lower())

	for word in search_wiki[1].description:
		if word in words:
			temp += 530

	temp += smart_answer(page, words, 870)

	if neg:
		temp *= -1

	points[original] = temp


points = {}


def cleanwords(string):
	return [word for word in string if word.lower() not in remove_words]


def handler2(words, olist, neg):
	global points2

	o = ' '.join(words)
	#print o

	"""
	try:
		search_wiki = google.search(o, 1)

		link = search_wiki[0].link

		print link
		os.system("open " + link)

		# os.system("open " + str(link))

		''' 
		try:
			f = open("HQLINKDISPLAY.html", "w+")
			f.write("<html>\n<title> HQ BOT URL DESCRIPTIONS  asd</title>\n")
			wtr = "<h1> Link " + str(1) + " : " + encode(search_wiki[1].name) + "</h1>\n<p> " + encode(search_wiki[1].description) + " </p>\n</br>"
			print wtr
			f.write(wt

r)

			f.write("</html>")
			os.system("open HQLINKDISPLAY.html")


		except Exception, e:
			print e
		'''

		try:
			user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
			request = urllib2.Request(link, headers=user_agent)
			content = urlopen(request).read()
			soup = BeautifulSoup(content, "lxml")
			page = soup.get_text().lower()

		except:
			content = urlopen(link).read()
			soup = BeautifulSoup(content, "lxml")
			page = soup.get_text().lower()

	except Exception, e:
		print ("OOPSEEEE WOOPSIEE WE MADE A FUCKY WUKCY " + str(e))
		o += " site:wikipedia.org"
		print o
		search_wiki = google.search(o, 1)
		link = search_wiki[0].link
		os.system("open " + link)
		content = urlopen(link).read()
		soup = BeautifulSoup(content, "lxml")

		page = soup.get_text().lower()
	"""

	o += " site:wikipedia.org"
	print (o)
	search_wiki = google.search(o, 1)
	link = search_wiki[0].link
	os.system("open " + link)
	content = urllib.request.urlopen(link).read()
	soup = BeautifulSoup(content, "lxml")

	page = soup.get_text().lower()

	for word in olist:
		if neg:
			points2[word.lower()] = 0 - ((page.count(word.lower()) * 2700))
		# print (optionword + " : " + str((page.count(optionword.lower())*3500) + str((smart_answer(page, optionwords, 7000)))))

		else:
			points2[word.lower()] = 0 + ((page.count(word.lower()) * 2700))
		# print (optionword + " : " + str((page.count(optionword.lower())*3500) + " | smart_answer: " + optionwords + str((smart_answer(page, optionwords, 7000)))))


points = {}
points2 = {}


def search(sim_ques, options, neg):
	words = split_string(sim_ques)
	threads = []

	for i in range(len(options)):
		t = threading.Thread(target=handler, args=[words, options[i], neg])
		t.setDaemon(True)
		threads.append(t)

	t = threading.Thread(target=handler2, args=[words, options, neg])
	t.setDaemon(True)
	threads.append(t)

	for i in threads:
		i.start()

	for i in threads:
		i.join()

	print (points)
	print (points2)

	for key in points:
		points[key] += points2[key]


def bestchoice(d1):
	v = list(d1.values())
	k = list(d1.keys())
	return k[v.index(max(v))]


def formquestion(question):
	sentwords = question.lower().split()

	clean = cleanwords(sentwords)
	temp = ' '.join(clean)

	clean_question = ""

	for ch in temp:
		if ch != "?" or ch != "\"" or ch != "\'":
			clean_question += ch

	return clean_question.lower(), [i for i in sentwords if i in negative_words]


def main():
	loadlists()

	question, options = parse_question()

	try:
		pass#os.system("open https://www.google.com/search?q=" + unidecode.unidecode('+'.join(question.split())))
	except Exception:
		pass

	qsimp, neg = formquestion(question)


	print("\n" + question + "\n")

	search(question, options, neg)

	answer = bestchoice(points)
	print (answer)
	os.system("say i think " + answer)
	print (points)

#TODO: REPLACE ' and with %27
def othermain():
	loadlists()

	question = raw_input("Question: ")
	temp = '+'.join(question.split())

	try:
		pass#os.system("open https://www.google.com/search?q=" + unidecode.unidecode(temp))
	except Exception:
		pass
		

	print ("open https://www.google.com/search?q=" + unidecode.unidecode(temp))

	options = []

	for a in range(3):
		options.append(raw_input("Option " + str(a + 1) + ": "))

	qsimp, neg = formquestion(question)

	#print("\n" + question + "\n")

	search(question, options, neg)

	print points

	answer = bestchoice(points)
	print (answer)
	os.system("say i think \'" + answer +  "\'")


if __name__ == '__main__':
	try:
		if sys.argv[1] == ("live"):
			main()
		else:
			othermain()
	except IndexError:
		othermain()
