#!/usr/bin/python
import vultr
import threading
from tkinter import *

#Set
Location = "25";
API_Key = ""



#Func
def use_proxy(port):
	CMD = "export ALL_PROXY=socks5://127.0.0.1:"+port;
	os.system(CMD)

class Application():
	app = None
	widgets = {}

	def __init__(self,title):
		self.app = Tk(className=title)
	def set_size(self,widget,width,height):
		widget['height'] = height;
		widget['width'] = width;
		return widget

	def set_widget(self,widget,row,column,sticky):
		widget.grid(column = column, row = row, sticky = sticky)
		return widget

	def get_button(self,title,command,w_id):
		app_button = Button(self.app)
		app_button['text'] = title;
		app_button['command'] = command;
		self.widgets[w_id] = app_button;
		return app_button;
	def get_entry(self,w_id):
		app_entry = Entry(self.app)
		self.widgets[w_id] = app_entry;
		return app_entry
	def get_entry_long(self,w_id):
		app_entry = Entry(self.app)
		app_entry['width'] = 50;
		self.widgets[w_id] = app_entry;
		return app_entry
	def get_label(self,text,w_id):
		app_label = Label(self.app)
		app_label['text'] = text
		self.widgets[w_id] = app_label;
		return app_label
	def get_text(self,w_id):
		app_text = Text(self.app)
		self.widgets[w_id] = app_text;
		return app_text
	def get_menubtn(self,w_id):
		app_menubtn = Menubutton(self.app)
		self.widgets[w_id] = app_menubtn;
		return app_menubtn
	def set_munubtn(self,widget,text,items):
		widget['text'] = text;
		widget.menu = Menu(widget)
		for item in items:
			widget.menu.add_command(label=item) 
		widget['menu'] = widget.menu
		return widget

	def refresh_text(self,widget,w_id):
		info_text.delete('1.0', END)

	def get_widget(self,w_id):
		return self.widgets[w_id]


class Display(Application):
	display = None
	info = {}
	def __init__(self,title):
		self.display = Toplevel()
		info['decision'] = False
	def click_yes(self,func):
		info['decision'] = True
		func();
	def click_no(self,func):
		info['decision'] = False
		func();



account = vultr.account()
app = Application("vultr manager")
app.get_label("API_Key: ",'key_label')
app.set_widget(app.widgets['key_label'],0,0,W)

key_entry = app.get_entry_long('key_entry')
app.set_widget(app.get_widget('key_entry'),1,0,W)

app.get_text('info_text')
app.set_size(app.get_widget('info_text'),65,20)
app.set_widget(app.get_widget('info_text'),4,0,W)


app.set_widget(app.get_label("SUBID: ",'sid_label'),6,0,E)
app.get_entry('sid_entry')
app.set_widget(app.get_widget('sid_entry'),6,1,E)

app.set_widget(app.get_label('Status:','tstatus_label'),5,0,W)
app.set_widget(app.get_label('','status_label'),5,1,W)

religions = ["Los Angeles","Tokyo","London","Sydney","Singapore"]

app.set_widget(app.set_munubtn(app.get_menubtn('religion_mbtn'),"religion",religions),4,2,W)
app.set_widget(app.get_menubtn('plan_mbtn'),4,3,W)

def Refresh_Info():
	app.get_widget('info_text').delete('1.0', END)
	app.get_widget('info_text').insert(INSERT,"Account Info\n")
	Balance = "Balance: "+str(account.balance)+"\n"
	app.get_widget('info_text').insert(INSERT,Balance)
	data = account.get_server_info()
	for item in data:
		server_data = data[item]
		app.get_widget('info_text').insert(INSERT,"==========================\n")
		app.get_widget('info_text').insert(INSERT,"Server "+server_data['SUBID']+"\n")
		app.get_widget('info_text').insert(INSERT,"IP: "+server_data["main_ip"]+"\n")
		app.get_widget('info_text').insert(INSERT,"Location: "+server_data["location"]+"\n")
		app.get_widget('info_text').insert(INSERT,"OS: "+server_data["os"]+"\n")
		app.get_widget('info_text').insert(INSERT,"Location: "+server_data["location"]+"\n")
		app.get_widget('info_text').insert(INSERT,"Status: "+server_data["status"]+"\n")
		try:
			server_data["ssr_installation"]
		except KeyError:
			app.get_widget('info_text').insert(INSERT,"SSR: "+"None"+"\n")
		else:
			app.get_widget('info_text').insert(INSERT,"SSR: "+server_data["ssr_installation"]+"\n")
			
		
		app.get_widget('info_text').insert(END," \n")

def Set_Api_Key():
	API_Key = key_entry.get()
	account.set_account(API_Key)
	(back, stdout) = account.get_account()
	if (back == "DONE"):
		Refresh_Info()
	else:
		app.get_widget('info_text').delete('1.0', END)
		app.get_widget('info_text').insert(INSERT,stdout);

		

def Add_Server():
	if (account.CMD_Head != ""):
		account.create_server('201','193','5');
		Refresh_Info();

def Thread_ISSR(server_data):
	pass
	

def Install_SSR():

	SUBID = app.get_widget('sid_entry').get()
	server_data = account.servers[SUBID]
	vultr.connect_ssh(server_data)
	app.get_widget('status_label').config(text = SUBID+" Installing UFW and SSR");
	server_data['ssr_installation'] = "Installing"
	#threading.Thread(target = Thread_ISSR,args = (server_data))

	vultr.install_ssr(server_data)
	app.get_widget('info_text').delete(END)
	app.get_widget('status_label').insert(END,SUBID+" Installation Done.");
	app.get_widget('status_label').config(text = SUBID+" UFW and SSR Installed");
	Refresh_Info();


def Destroy_Server():
	#display = Display("Display")
	#account.destroy_server(sid_text.get())
	SUBID = app.get_widget('sid_entry').get()
	account.destroy_server(SUBID)
	Refresh_Info()

app.set_size(app.set_widget(app.get_button("Connect",Set_Api_Key,'connect_button'),1,5,W),10,1)
app.set_size(app.set_widget(app.get_button("Add a Server",Add_Server,'add_button'),4,5,W),10,1)
app.set_size(app.set_widget(app.get_button("Refresh",Refresh_Info,'refresh_button'),2,5,W),10,1)
app.set_size(app.set_widget(app.get_button("Install SSR",Install_SSR,'install_button'),5,5,W),10,1)
app.set_size(app.set_widget(app.get_button("Destroy Server",Destroy_Server,'destroy_button'),6,5,W),10,1)


app.app.mainloop()

	