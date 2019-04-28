import os, re, sys, hashlib
from pprint import pprint

tempFile = os.environ["TEMP"].replace("\\", "/")+"/python-diskpart.txt"

class diskpart:
	def __init__(self, fetch_uid=False):
		self.mainC = "diskpart /s "+tempFile
		self.selected = False
		self.selectedPart = False
		self.opts = {
			"fetch_uid": fetch_uid
			}
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
		},
		"partition": {
			0: "partition",
			1: "type",
			2: "size",
			3: "offset"
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
					disks[ind] = {"partitions": {}}
				elif part == 4 or part == 5:
					if p == "*":
						disks[ind][self.parts["disk"][part]] = True
					else:
						disks[ind][self.parts["disk"][part]] = False
				else:
					disks[ind][self.parts["disk"][part]] = p
			ind += 1
		if self.opts["fetch_uid"]:
			command = self.mainC+' | findstr /r "Disk.ID:"'
			bulkC = ""
			for disk in disks:
				bulkC += "select disk {}\r\nuniqueid disk\r\n".format(disk)
			self.write(bulkC)
			result = self.exec(command).split("\n")[:-1]
			ind = 0
			for uid in result:
				uid = re.subn("(Disk ID: )|[{}]", "", uid)[0]
				disks[ind]["uid"] = uid
				disks[ind]["display_id"] = hashlib.md5(uid.encode("utf-8")).hexdigest()[:6]
				ind += 1
		self.disks = disks
		return self.disks
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
				elif part == 1 or part == 2 or part == 7:
					if p == "":
						volumes[ind][self.parts["volume"][part]] = False
					else:
						volumes[ind][self.parts["volume"][part]] = p
				else:
					volumes[ind][self.parts["volume"][part]] = p
			ind += 1
		self.volumes = volumes
		return self.volumes
	def listPartition(self):
		if type(self.selected) == int:
			cmd = "select disk {}\nlist partition".format(self.selected)
			self.write(cmd)
			command = self.mainC+' | findstr /r "Partition ---"'
			result = self.exec(command)
			template = result.split("\n")[1]
			temp = result.split("\n")[2:-1]
			partitions = {}
			parts = self.lister(template, temp)
			ind=0
			for text in temp:
				for part in parts:
					p = text[parts[part]["begin"]:parts[part]["end"]].replace(" ", "")
					if part == 0:
						partitions[ind] = {}
					elif part == 1:
						if p == "Unknown":
							partitions[ind][self.parts["partition"][part]] = False
						else:
							partitions[ind][self.parts["partition"][part]] = p
					else:
						partitions[ind][self.parts["partition"][part]] = p
				ind += 1
			self.disks[self.selected]["partitions"] = partitions
			return partitions
		else:
			raise Exception("You need to select a disk before using this function.")
	def clean(self):
		if type(self.selected) == int:
			cmd = "select disk {}\r\nclean".format(self.selected)
			self.write(cmd)
			self.exec(self.mainC)
		else:
			raise Exception("You need to select a disk before using this function.")
	def createPartition(self, partition):
		if type(self.selected) == int:
			if partition and type(partition) == str:
				cmd = "select disk {}\r\ncreate partition {}\r\n".format(self.selected, partition)
				self.write(cmd)
				self.exec(self.mainC)
				self.listPartition()
			else:
				raise ValueError("Expected string as input but got '{}' instead.".format(type(partition)))
		else:
			raise Exception("You need to select a disk before using this function.")
	def selectDisk(self, diskNum):
		try:
			int(diskNum)
		except:
			raise ValueError("Expected integer as input but got '{}' instead.".format(diskNum))
		else:
			if int(diskNum) <= len(self.disks):
				self.selected = diskNum
			else:
				raise Exception("Selected '{}' disk is not present.".format(diskNum))
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
