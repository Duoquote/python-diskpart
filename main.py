import os, re
from pprint import pprint
tempFile = os.environ["TEMP"].replace("\\", "/")+"/python-diskpart.txt"

class diskpart:
	def __init__(self):
		self.mainC = "diskpart /s "+tempFile
		self.parts = {
		"disk": {
			0: "disk_num",
			1: "status",
			2: "size",
			3: "free",
			4: "dyn",
			5: "gpt"
		},
		"volume": {
			0: "volume_num",
			1: "letter",
			2: "name",
			3: "format",
			4: "type",
			5: "size",
			6: "status",
			7: "info"
		}}
		self.listDisk()
		self.listVolume()
	def write(self, cmd):
		with open(tempFile, "w") as f:
			f.write(cmd)
	def exec(self, cmd):
		test = os.popen(cmd).read()
		return test
	def listDisk(self):
		cmd = "list disk"
		self.write(cmd)
		command = self.mainC+' | findstr /r "Disk.*Online ----"'
		result = self.exec(command)
		template = result.split("\n")[0]
		temp = result.split("\n")[1:-1]
		disks = {}
		parts = self.lister(template, temp)
		ind=0
		for text in temp:
			for part in parts:
				p = text[parts[part]["begin"]:parts[part]["end"]].replace(" ", "")
				if part == 0:
					disks[ind] = {}
					disks[ind][self.parts["disk"][part]] = int(p.replace("Disk", ""))
				elif part == 4 or part == 5:
					if p == "*":
						disks[ind][self.parts["disk"][part]] = True
					else:
						disks[ind][self.parts["disk"][part]] = False
				else:
					disks[ind][self.parts["disk"][part]] = p
			ind += 1
		self.disks = disks
	def listVolume(self):
		cmd = "list volume"
		self.write(cmd)
		command = self.mainC+' | findstr /r "Volume.* ----"'
		result = self.exec(command)
		template = result.split("\n")[1]
		temp = result.split("\n")[2:-1]
		volumes = {}
		parts = self.lister(template, temp)
		ind=0
		for text in temp:
			for part in parts:
				p = text[parts[part]["begin"]:parts[part]["end"]].replace(" ", "")
				if part == 0:
					volumes[ind] = {}
					volumes[ind][self.parts["volume"][part]] = int(p.replace("Volume", ""))
				elif part == 1 or part == 2 or part == 7:
					if p == "":
						volumes[ind][self.parts["volume"][part]] = False
					else:
						volumes[ind][self.parts["volume"][part]] = p
				else:
					volumes[ind][self.parts["volume"][part]] = p
			ind += 1
		self.volumes = volumes
	def lister(self, template, data):
		lastVal = 0
		totalLen = 0
		partNum = 0
		parts = {}
		for i in template:
			if i == "-":
				if lastVal == 0:
					parts[partNum] = {"begin": totalLen}
				lastVal = 1
			else:
				if lastVal == 1:
					parts[partNum]["end"] = totalLen
					partNum += 1
				lastVal = 0
			totalLen +=1
		parts[len(parts)-1]["end"] = totalLen
		return parts
		#self.disks = disks


test = diskpart()
pprint(test.disks)
pprint(test.volumes)
