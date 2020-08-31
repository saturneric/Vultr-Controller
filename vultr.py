import os
import json
import subprocess
import paramiko
import time

class account:
	API_Key = None;
	balance = 0;
	last_pay_date = None;
	last_pay_amount = 0;
	servers_subid = [];
	servers = [];

	CMD_CMD = None
	CMD_INFO = None
	CMD_OPTION = None
	CMD_Head = None

	def __init__(self):
		pass
		
	def set_account(self,API_Key):
		self.API_Key = API_Key;
		self.CMD_CMD = "curl"
		self.CMD_OPTION = " -s"
		self.CMD_INFO = " -H 'API-Key:"+API_Key+"' "
		self.CMD_Head = self.CMD_CMD+self.CMD_OPTION+self.CMD_INFO

	def do_command(self,CMD):
		child = subprocess.Popen([CMD],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);
		child.wait();
		(stdout,error) = child.communicate()
		str_out = stdout.decode()
		str_err = error.decode()
		if (str_err != ''): print("Error: "+error)
		return str_out;

	def get_account(self):
		CMD_HTML = "https://api.vultr.com/v1/account/info"
		CMD = self.CMD_Head+CMD_HTML;
		stdout = self.do_command(CMD);
		try:
			data = json.loads(stdout);
		except json.decoder.JSONDecodeError:
			print("Ask account information failed.")
			print(stdout)
			return "ERROR",stdout;
		else:
			self.balance = data["balance"];
			self.last_pay_date = data["last_payment_date"];
			self.last_pay_amount = data["last_payment_amount"];
		return "DONE","NONE";

	def create_server(self, plan, os, religion):
		CMD_HTML = "https://api.vultr.com/v1/server/create"
		CMD_DATA = " --data 'DCID="+religion+"' --data 'VPSPLANID="+plan+"' --data 'OSID="+os+"'"
		CMD = self.CMD_Head+CMD_HTML+CMD_DATA;
		stdout = self.do_command(CMD);
		data = json.loads(stdout);
		self.servers_subid.append(data["SUBID"]);
		self.servers_subid  =[]
		self.get_server_info()
		
		return data["SUBID"];

	def create_ipv4(self,SUBID):
		CMD_HTML = "https://api.vultr.com/v1/server/create_ipv4";
		CMD_DATA = " --data 'SUBID="+SUBID+"'"
		CMD = self.CMD_Head + CMD_HTML + CMD_DATA;
		self.do_command(CMD)
		
	def destroy_server(self,SUBID):
		CMD_HTML = "https://api.vultr.com/v1/server/destroy";
		CMD_DATA = " --data 'SUBID="+SUBID+"'"
		CMD = self.CMD_Head + CMD_HTML + CMD_DATA;
		stdout = self.do_command(CMD)
		
	def destroy_ipv4(self,SUBID):
		CMD_HTML = "https://api.vultr.com/v1/server/destroy_ipv4";
		CMD_DATA = " --data 'SUBID="+SUBID+"'"
		CMD = self.CMD_Head + CMD_HTML + CMD_DATA;
		self.do_command(CMD)
		

	def server_reboot(self,SUBSID):
		CMD_HTML = "https://api.vultr.com/v1/server/reboot";
		CMD_DATA = " --data 'SUBID="+SUBID+"'"
		CMD = self.CMD_Head + CMD_HTML + CMD_DATA;
		stdout = self.do_command(CMD)
		
	def get_server_info(self):
		CMD_HTML = "https://api.vultr.com/v1/server/list";
		CMD = self.CMD_Head + CMD_HTML;
		stdout = self.do_command(CMD);
		data = json.loads(stdout);
		self.servers = data
		#print(data)
		self.servers_subid = []
		for item in data:
			self.servers_subid.append(item)
		return data;
	def get_sever_ipv4(self):
		CMD_HTML = "https://api.vultr.com/v1/server/list_ipv4";
		CMD_DATA = "?SUBID="+SUBID
		CMD = self.CMD_Head + CMD_HTML + CMD_DATA;
		stdout = self.do_command(CMD)

def connect_ssh(server_data):
	if (server_data["status"] == "active"):
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(server_data["main_ip"],22,"root",server_data["default_password"],timeout=8)
		server_data['ssh_connection'] = ssh;

		return server_data

def install_ssr(server_data):
	ssh = server_data['ssh_connection']
	if(server_data["status"] == "active"):
		print("Waiting for installation...")

		print("Installing Ufw...")
		stdin,stdout,stderr = ssh.exec_command("apt-get install ufw")
		stdin.write("Y\n");
		print(stdout.read())
		print("Ufw installed.")
		server_data['ufw_installation'] = "Installed";

		time.sleep(3)

		print("Setting Ufw...")
		stdin,stdout,stderr = ssh.exec_command("ufw enable")
		stdin.write("Y\n")
		stdin,stdout,stderr = ssh.exec_command("ufw allow 9048")
		stdin,stdout,stderr = ssh.exec_command("ufw allow 22")
		stdin,stdout,stderr = ssh.exec_command("ufw default deny")
		print(stdout.read())
		print("Ufw have been set");
		server_data['ufw_setting_allow'] = [22,9048];
		
		time.sleep(3)

		print("Setting SSR...")
		stdin,stdout,stderr = ssh.exec_command("wget --no-check-certificate https://raw.githubusercontent.com/teddysun/shadowsocks_install/master/shadowsocksR.sh")
		stdin,stdout,stderr = ssh.exec_command("chmod +x shadowsocksR.sh");
		stdin,stdout,stderr = ssh.exec_command("./shadowsocksR.sh 2>&1 | tee shadowsocksR.log")
		stdin.write("#a9b9fa3456\n");
		stdin.write("9048\n2\n7\n7\n\n");
		print(stdout.read())
		stdin,stdout,stderr = ssh.exec_command("systemctl start shadowsocks")
		print("SSR have been set and now is running.")
		print("Server IP :"+server_data["main_ip"])
		server_data['ssr_installation'] = "Installed";
		return "DONE"

def print_server(server_data):
	print(server_data["SUBID"])
	print(server_data["main_ip"])
	print(server_data["location"])
	print(server_data["os"])
	print(server_data["status"])
	print(server_data["default_password"])