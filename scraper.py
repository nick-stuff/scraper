from tkinter import *
from tkinter import ttk

from datetime import datetime
import requests
from bs4 import BeautifulSoup


root = Tk()
root.title('Indeed Scraper')
root.geometry("1000x500")
style = ttk.Style()
style.theme_use('default')
style.configure("Treeview", background = "#D3D3D3", foreground = "black", rowheight= 25, fieldbackground = '#D3D3D3')
style.map('Treeview', background = [('selected', "#347083")])

tree_frame = Frame(root)
tree_frame.pack(pady=10)
tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT, fill=Y)
my_tree = ttk.Treeview(tree_frame, yscrollcommand = tree_scroll.set, selectmode = "extended")
my_tree.pack()

textBox = Text(root, height = 5, width= 60)
textBox.pack()

f = open("query.txt","r")
queries = []
LocQuery = ""
JobQuery = ""

for i in f:
	queries.append(i)
if len(queries) ==2:
	LocQuery= queries[0]
	JobQuery= queries[1]	
f.close()

whitelist = "abcdefghijklmnopqrstuvwxyz1234567890-.,:?"
rowCount = 0

tree_scroll.config(command=my_tree.yview)
my_tree['columns'] = ("Title", "Company Name", "Company Location", "Description", "Pay", "Date Queried", "Post Date")
my_tree.column("#0", width = 0, stretch = NO)
my_tree.column("Title", anchor =W, width=140)
my_tree.column("Company Name", anchor =W, width=140)
my_tree.column("Company Location", anchor =CENTER, width=140)
my_tree.column("Description", anchor =CENTER, width=140)
my_tree.column("Pay", anchor =CENTER, width=140)
my_tree.column("Date Queried", anchor =CENTER, width=140)
my_tree.column("Post Date", anchor =CENTER, width=140)
my_tree.heading("#0", text="", anchor = W)
my_tree.heading("Title", text="Title", anchor = W)
my_tree.heading("Company Name", text="Company Name", anchor = W)
my_tree.heading("Company Location", text="Company Location", anchor = CENTER)
my_tree.heading("Description", text="Description", anchor = CENTER)
my_tree.heading("Pay", text="Pay", anchor = CENTER)
my_tree.heading("Date Queried", text="Date Queried", anchor = CENTER)
my_tree.heading("Post Date", text="Post Date", anchor = CENTER)


def getUrl(pos, loc):
	template = 'https://ca.indeed.com/jobs?q={}&l={}'
	pos = pos.replace(' ', '+')
	loc = loc.replace(' ', '+')
	url = template.format(pos, loc)
	return url
def queryInfo():
	queryPopup = Toplevel()
	queryPopup.wm_title("Query Info")
	location = StringVar(queryPopup)
	job = StringVar(queryPopup)

	Label(queryPopup, text= "Location").pack(side="top", fill="x", pady=10,padx=10)
	entryHost = Entry(queryPopup, textvariable = location, bd= 5,width=35).pack(side="top",fill="x")

	Label(queryPopup, text= "Job Title").pack(side="top", fill="x", pady=10,padx=10)
	entryUser = Entry(queryPopup, textvariable = job, bd= 5,width=35).pack(side="top",fill="x")

	doneButton = Button(queryPopup, text = "Done", command= lambda: destroyQueryPopup(queryPopup, location.get(), job.get()))
	
	doneButton.pack(side="bottom")
def destroyQueryPopup(popup,l,j):
	global LocQuery
	global JobQuery
	LocQuery = l
	JobQuery = j
	f = open("query.txt","w")
	f.write(LocQuery)
	f.write("\n")
	f.write(JobQuery)
	f.close()
	popup.destroy()


def query():
	url = getUrl(JobQuery, LocQuery)
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	cards = soup.find_all('div','job_seen_beacon')
	
	for card in cards:
		title = card.table.tbody.tr.td.div.h2
		title = title.find_all("span")[-1].get_text()
		companyName = card.find('span', 'companyName').text.strip()
		companyLoc = card.find('div', 'companyLocation').text.strip()
		description = card.find('div', 'job-snippet').text.strip()
		date = card.find('span','date').text.strip()
		today = datetime.today().strftime('%Y-%m-%d')
		try:
			pay = card.find('div', 'salary-snippet').text.strip()
		except AttributeError:
			pay = "N/A"


		entry = (title,companyName,companyLoc,description,pay, today, date)
		fromStart = False
		addToFile(entry)

def main():
	
	my_tree.bind('<ButtonRelease-1>', clickHandle)
	queryButton= Button(root,width= 8, height=2, text="Query", command= query)
	fromStart = True
	queryInfoButton= Button(root,width= 15, height=2, text="Input Query Info", command= queryInfo)
	printtablebutton =  Button(root,width= 15, height=2, text="Print Table", command= printFile)
	resetButton =  Button(root,width= 15, height=2, text="Reset", command= resetTable)

	queryButton.place(x=100,y=310)
	queryInfoButton.place(x=800,y=360)
	printtablebutton.place(x=100,y=360)
	resetButton.place(x=100, y= 410)
	root.mainloop()
	

def printFile():
	entryFile = open("jobs.txt", "r")
	global rowCount

	rowCount = 0
	my_tree.delete(*my_tree.get_children())

	for j in entryFile:
		i = eval(j)
		my_tree.insert(parent = '', index = 'end', iid= rowCount, text='', values= (i[0],i[1],i[2],i[3],i[4],i[5],i[6]))
		rowCount+=1
	entryFile.close()
	

def guiHandle():
	my_tree.bind('<ButtonRelease-1>', clickHandle)
	root.mainloop()

def addToFile(entry):
	entryFile = open("jobs.txt", "r+", errors='ignore')
	add = True
	entryStr = str(entry)
	global rowCount
	for l in entryFile:
		l = l.rstrip('\n')
	
		equal = False
		if  str(entry) == l:
			equal = True

		
		entryStr= "".join(filter(lambda c: c in whitelist, entryStr))
		l = "".join(filter(lambda c: c in whitelist, l))

		if entryStr == l:
			add = False
			break;
	if add:

		entryFile.write(str(entry))
		entryFile.write("\n")
		my_tree.insert(parent = '', index = 'end', iid= rowCount, text='', values= (entry[0],entry[1],entry[2],entry[3],entry[4],entry[5],entry[6]))
		rowCount+=1
	entryFile.close()

def resetTable ():
	open("jobs.txt", 'w').close()

def clickHandle(event):

	item = my_tree.item(my_tree.focus())
	col = my_tree.identify_column(event.x)
	textBox.delete('1.0',END)
	item_count = len(my_tree.get_children())
	try:
		if col == "#1":
			textBox.insert(END,item['values'][0])
		elif col == "#2":
			textBox.insert(END,item['values'][1])
		elif col == "#3":
			textBox.insert(END,item['values'][2])
		elif col == "#4":
			textBox.insert(END,item['values'][3])
		elif col == "#5":
			textBox.insert(END,item['values'][4])
		elif col == "#6":
			textBox.insert(END,item['values'][5])
		elif col == "#7":
			textBox.insert(END,item['values'][6])
	except IndexError:
		textBox.insert(END,"")
if __name__ == "__main__":
    main()
