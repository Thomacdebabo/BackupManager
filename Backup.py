from datetime import datetime
import os
import shutil
from distutils.dir_util import copy_tree
import re
import json
import sys
from CopyWorker import CopyWorker
from PyQt5.QtCore import QThreadPool
#from EfficientCopy import copytree
import subprocess


class BackupManager(): #A hub to manage all Backups
    def __init__(self, dir):
        self.threadpool = QThreadPool()
        self.subthreadpool = QThreadPool()
        self.threads = 0
        self.BackupDirectory = dir
        self.BackupStorage = {}
        self.load_from_txt()
        self.load_prev_from_json()
        print("Backup Manager initiated: " + dir)
        self.print()
    def getAmountOfThreads(self):
        return self.threadpool.activeThreadCount()
    def close(self):
        try:
            self.save_prev_to_json()
            self.save_to_txt()
            self.cleanup()
        except: print("closing failed")
    def addBackup(self, b):
        assert isinstance(b, Backup), 'Not a Backup!'
        name = b.getName()
        if name not in self.BackupStorage:
            self.BackupStorage[name] = [b]
            print("New Backup Entry Created: " + name)
            return True
        else:
            temp = self.BackupStorage[name]
            for i in temp:
                if (b.getDirectory() == i.getDirectory()):
                    return False
            temp.append(b)
            self.BackupStorage[name] = temp
            print("Added Entry to existing Backup: " + name)
            return True
    def newBackup(self, name, dir, date = datetime.now(). strftime("%d_%m_%Y-%H_%M_%S")):
        try:
            b = Backup(name, dir, date)
        except(AssertionError):
            print("Backup initiation failed due to invalid inputs")
            return False
        self.addBackup(b)
        return True
    def moveBackupManager(self, newdir):
        tempbdir = self.BackupDirectory
        self.BackupDirectory = newdir
        self.threads += 1
        print(tempbdir)
        print(newdir)


    def backupALL(self):
        for b in self.BackupStorage.keys():
            self.back_up_threaded(b)
    def back_up_threaded(self, b):
        self.threads += 1
        worker = CopyWorker(self.back_up, b, self.BackupDirectory)
        worker.signals.finished.connect(self.thread_complete)
        self.threadpool.start(worker)
    def back_up(self, b, bdir):
        self.link_Backup(b, datetime.now(). strftime("%d_%m_%Y-%H_%M_%S"))
        self.save_Backup(b, bdir)
    def link_Backup(self, key, date, mode=0):
        dir = key + r'/'
        if (self.BackupStorage[key].__len__() == 1 or mode==1):
            for b in self.BackupStorage[key]:
                b.setDate(date)
                folder = os.path.basename(b.getDirectory())
                name = folder + "_" + date
                b.setBackupLocation(dir+name)
        else:
            i = 0
            for b in self.BackupStorage[key]:
                b.setDate(date)
                folder = os.path.basename(b.getDirectory())
                i+=1
                name = folder + "_" + date
                b.setBackupLocation(dir+ str(i) + "_" +name)
    def save_Backup(self, key, bdir):
        for b in self.BackupStorage[key]:
            b.savetoBackupLocation (bdir)
    def getAll(self):
        return self.BackupStorage.keys()
    def getinfo(self, key):
        l = []
        for i in self.BackupStorage[key]:
            for p in i.returnData():
                l.append(p)
        return l
    def thread_complete(self):
        self.threads -=1
        print(self.threads)
        if self.threads == 0:
            print("All Done")
    def print(self):
        for b in self.BackupStorage.keys():
            print("-----" + b + "-----")
            for i in self.BackupStorage[b]:
                i.printData()
    def save_prev_to_json(self):
        for b in self.BackupStorage.keys():
            c = 0
            for i in self.BackupStorage[b]:
                c+=1
                try:
                    f = open(self.BackupDirectory + "//" + b +"_"+  str(c) + "_prev.json", 'w')
                    f.write(json.dumps(i.getPrevious()))
                    f.close()
                except: print("couldn't save previous for: " + b+ "_" + str(i))
    def load_prev_from_json(self):
        for b in self.BackupStorage.keys():
            c = 0
            for i in self.BackupStorage[b]:
                c += 1
                try:
                    with open(self.BackupDirectory + "\\" + b +"_"+ str(c) + "_prev.json", 'r') as json_file:
                        data = json.load(json_file)
                        i.setPrevious(data)
                except: print("couldn't load json file: " + self.BackupDirectory + "\\" + b +"_"+  str(c) + "_prev.json")
    def save_to_txt(self, dir = ""):
        f = open(self.BackupDirectory + r"/backup.txt", 'w')
        for b in self.BackupStorage.keys():
            f.write("Name: " + b )
            for i in self.BackupStorage[b]:
                f.write("Date: " + i.getDate())
                f.write("Directory: " + i.getDirectory())
                f.write("Backupdirectory: " + i.getBackupLocation())
            f.write("\n")
        f.close()
    def load_from_txt(self):
        try:
            f = open(self.BackupDirectory + "\\backup.txt", 'r')
            for l in f.readlines():
                temp = re.split('Name: |Date: |Directory: |Backupdirectory: ', l.strip("\n"))
                temp.pop(0)
                self.load_entry(temp)
            f.close()
            print("Successfully loaded backup.txt")
        except: print("Couldn't load backup.txt")
    def load_entry(self, l):
        name = l.pop(0)
        while(l!=[]):
            date = l.pop(0)
            dir = l.pop(0)
            bdir = l.pop(0)
            b = Backup(name, dir, date = date)
            b.setBackupLocation(bdir)
            self.addBackup(b)
    def clear_all(self):
        self.BackupStorage = {}
    def cleanup(self): #deletes empty directories in Backup Folder
        print("-Cleanup-")
        count = 0
        for i in os.listdir(self.BackupDirectory):
            try:
                os.rmdir(os.path.join(self.BackupDirectory, i))
                count+=1
            except: print("Didn't delete: " + i)
        print("Deleted " + str(count) + " folders")
    def deletePrevious(self):
        for b in self.BackupStorage.keys():
            for i in self.BackupStorage[b]:
                self.threads +=1
                worker = CopyWorker(i.deletePrevious, self.BackupDirectory)
                worker.signals.finished.connect(self.thread_complete)
                self.threadpool.start(worker)
    def deleteCurrent(self):
        for b in self.BackupStorage.keys():
            for i in self.BackupStorage[b]:
                i.deleteCurrent(self.BackupDirectory)
    def open_in_explorer(self, key):
        for b in self.BackupStorage[key]:
            b.open_in_explorer()
    def open_Backup_in_explorer(self, key):
        for b in self.BackupStorage[key]:
            try: b.open_Backup_in_explorer(self.BackupDirectory)
            except(AssertionError): print("Directory not valid")
    def deleteSpecific(self, b, str):
        print(self.BackupStorage[b])
        for i in self.BackupStorage[b]:
            if i.deleteFromString(str, self.BackupDirectory):
                self.BackupStorage[b].remove(i)
        if self.BackupStorage[b]== []:
            del self.BackupStorage[b]
    def setEF(self, key, eFlag, str = ""):
        if str=="":
            for i in self.BackupStorage[key]:
                i.setEnabledFlag(eFlag)
        else:
            for i in self.BackupStorage[key]:
                if i.checkifstringiscurrent(str):
                    i.setEnabledFlag(eFlag)



class Backup(): # an object which contains directory information of my backups
    def __init__(self, name, dir, date= datetime.now(). strftime("%d_%m_%Y-%H_%M_%S"), enabledFlag = True):
        assert isinstance(name, str), 'Name should be string!'
        assert isinstance(dir, str), 'Directory should be string!'
        assert isinstance(date, str), 'Date should be string!'
        assert os.path.exists(dir), 'Directory not valid'
        self.enabledFlag = enabledFlag
        self.current = {"Name": name, "Directory": dir, "Date": date, "Backupdir": " "}
        self.previous = [] #old backups
    def getName(self):
        try:
            return self.current["Name"]
        except:
            return None
    def getDirectory(self):
        try:
            return self.current["Directory"]
        except:
            return None
    def getDate(self):
        return self.current["Date"]
    def setDate(self, date):
        self.current["Date"] = date
    def getEnabledFlag(self):
        return self.enabledFlag
    def setEnabledFlag(self, enabledFlag):
        self.enabledFlag = enabledFlag
    def getBackupLocation(self):
        try:
            return self.current["Backupdir"]
        except:
            return None
    def setBackupLocation(self, dir):
        if(self.getBackupLocation()!= " "):
           self.previous.append(self.current.copy())
        self.current["Backupdir"] = dir
    def savetoBackupLocation(self, bmdir):
        dir = os.path.join(bmdir, self.getBackupLocation())
        try: os.mkdir(dir)
        except(WindowsError): print("Directory already in place")
        try:
            print(self.getDirectory())
            print(self.getBackupLocation())
            if not dir.startswith(self.getDirectory()):
                copy_tree(self.getDirectory(), dir)
            else: print("WARNING: Backup directory is contained in source directory -> Cancelled Backup for: " + self.getDirectory())
        except:
            print(sys.exc_info())
            print("failed to do Backup for " +self.current["Name"])
    def open_in_explorer(self):
        assert os.path.exists(self.current["Directory"]), 'Directory not valid:' + self.current["Directory"]
        try:
            os.startfile(self.current["Directory"])
        except:
            subprocess.Popen(r'explorer /open,"' + self.current["Directory"] + '\\"')
    def open_Backup_in_explorer(self,bdir):
        dir = os.path.join(bdir, self.current["Backupdir"])
        assert os.path.exists(dir), 'Directory not valid: '
        try:
            os.startfile(dir)
        except:
            subprocess.Popen(r'explorer /open,"' + dir + r'\\"')
    def printData(self):
        print("-Current-")
        self.printdict(self.current)
        self.printPrevious()
    def returnData(self):
        list = []
        list.append("---Current---")
        list.append(self.returndict(self.current))
        for i in self.returnPrevious():
            list.append(i)
        return list
    def printPrevious(self):
        if(self.previous !=[]):
            print("-Previous-")
            for p in self.getPrevious():
                self.printdict(p)
    def returnPrevious(self):
        l = []
        if(self.previous !=[]):
            l.append("---Previous---")
            for p in self.getPrevious():
               l.append(self.returndict(p))
        return l
    def printdict(self, dict):
        print(self.returndict(dict))
    def returndict(self, dict):
        return str(dict["Date"] + " / " +  dict["Directory"] + " -> " + dict["Backupdir"])
    def getPrevious(self):
        return self.previous
    def setPrevious(self, pr):
        self.previous = pr.copy()
    def deletePrevious(self,bdir):
        for b in self.previous:
            dir = os.path.join(bdir, b["Backupdir"])
            print("deleting:" + dir)
            self.deleteDirectory(dir)
        self.previous = []
    def deleteCurrent(self, bdir):
        try:
            dir = os.path.join(bdir, self.current["Backupdir"])
            self.deleteDirectory(dir)
        except: print("oopsie")
    def deleteDirectory(self,dir):
        if(os.path.exists(dir)):
            shutil.rmtree(dir)
        else:
            print(dir + " doesn't exist")
    def deleteFromString(self, str, bdir):
        print(str)
        print(self.returndict(self.current))
        if str == self.returndict(self.current):
            try:
                self.deleteCurrent(bdir)
                print("deleted current: " + str)
            except: print("doesnt exist")
            return True
        else:
            for p in self.previous:
                print(p)
                if str == self.returndict(p):
                    dir = os.path.join(bdir, p["Backupdir"])
                    self.previous.pop(p)
                    self.deleteDirectory(dir)
                    print("deleted previous: " +  str)
                return False
        return False
    def checkifstringiscurrent(self, str):
        if str == self.returndict(self.current):
            return True
        else:
            return False

