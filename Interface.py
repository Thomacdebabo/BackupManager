from PyQt5.QtWidgets import QMessageBox, QListWidget, QApplication, QFileDialog, QFormLayout, QLabel, QGroupBox, QComboBox, QSpinBox,QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QLineEdit, QStatusBar, QSizePolicy, QMainWindow, QSlider, QDialogButtonBox, QDialog
import sys
import Backup
from PyQt5.QtCore import QThreadPool


class myListWidget(QWidget):
    def __init__(self):
        self.dict = {}
        super(myListWidget, self).__init__()
        self.list = QListWidget()
        self.sublist = QListWidget()
        self.listlayout = QHBoxLayout(self)

        self.listlayout.addWidget(self.list)
        self.listlayout.addWidget(self.sublist)
        self.list.itemClicked.connect(self.Clicked)

        self.list.setFixedWidth(200)
        self.sublist.setFixedWidth(1000)
        self.setLayout(self.listlayout)
    def Clicked(self, item):
        self.sublist.clear()
        for i in self.dict[item.text()]:
            self.sublist.addItem(i)
    def addBU(self, i, info):
        self.list.addItem(i)
        self.dict[i] = info
    def clear(self):
        self.list.clear()
        self.sublist.clear()
    def current(self):
        try:
            return self.list.currentItem().text()
        except:
            return None
    def getsub(self):
        try:
            return self.sublist.currentItem().text()
        except:
            return None


class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.BM = None
        self.layout = QVBoxLayout(self)
        self.Buttons()
        self.list = myListWidget()
        self.list.list.itemDoubleClicked.connect(self.doubleClicked)
        self.box = QLineEdit()
        self.addBUI = QPushButton('Add Backup Instance', self)
        self.buttonSave = QPushButton('Save backup.txt', self)

        self.box.hide()
        self.addBUI.hide()
        self.buttonSave.hide()

        self.addBUI.clicked.connect(self.addInstance)
        self.buttonSave.clicked.connect(self.savetxt)



        self.layout.addWidget(self.list)

        self.layout.addLayout(self.buttonLayout)

        self.layout.addWidget(self.box)
        self.layout.addWidget(self.addBUI)
        self.layout.addWidget(self.buttonSave)


        self.setLayout(self.layout)

    def Buttons(self):
        self.buttonLayout = QHBoxLayout(self)
        self.button = QPushButton('Open Backup Manager', self)
        self.Addbutton = QPushButton('Add Backup', self)
        self.Delbutton = QPushButton('Delete Backup', self)
        self.BUbutton = QPushButton('Back Up All', self)
        self.BUCbutton = QPushButton('Back Up', self)
        self.removeButton = QPushButton('Remove Previous', self)

        self.buttonLayout.addWidget(self.button)
        self.buttonLayout.addWidget(self.Addbutton)
        self.buttonLayout.addWidget(self.Delbutton)
        self.buttonLayout.addWidget(self.BUbutton)
        self.buttonLayout.addWidget(self.BUCbutton)
        self.buttonLayout.addWidget(self.removeButton)


        self.button.clicked.connect(self.OpenBackupManager)
        self.Addbutton.clicked.connect(self.AddBackup)
        self.Delbutton.clicked.connect(self.DelBackup)
        self.removeButton.clicked.connect(self.removePrevious)
        self.BUbutton.clicked.connect(self.BackupALL)
        self.BUCbutton.clicked.connect(self.Backup)

        self.BUbutton.hide()
        self.Addbutton.hide()
        self.Delbutton.hide()
        self.BUCbutton.hide()
        self.removeButton.hide()
    def OpenBackupManager(self):
        if self.BM is not None:
            self.BM.close()
            self.list.clear()
        dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if dir:
            self.BM = Backup.BackupManager(dir)
            self.BackupList()

            self.BUbutton.show()
            self.BUCbutton.show()
            self.removeButton.show()
            self.Addbutton.show()
            self.Delbutton.show()
            self.box.show()
            self.box.setText("")
            self.addBUI.show()
            self.buttonSave.show()

    def AddBackup(self):
        dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if dir and self.list.current():
            self.BM.newBackup(self.list.current(), dir)
            self.list.clear()
            self.BackupList()
        else:
            print("Adding Backup failed")
    def DelBackup(self):
        b = self.list.current()
        str = self.list.getsub()
        if b and str:
            self.BM.deleteSpecific(b, str)
        self.list.clear()
        self.BackupList()
    def doubleClicked(self, item):
        key = item.text()
        self.BM.open_Backup_in_explorer(key)
    def BackupALL(self):
        self.BM.backupALL()
        self.list.clear()
        self.BackupList()
    def Backup(self):
        b = self.list.current()
        if b  is not None:
            self.BM.back_up_threaded(b)
            self.list.clear()
            self.BackupList()
        else:
            msg = QMessageBox()
            msg.setText("No backup selected")
            msg.exec()
            print("no backup selected")
    def removePrevious(self):
        self.BM.deletePrevious()
        self.list.clear()
        self.BackupList()

    def BackupList(self):
        for i in self.BM.getAll():
            self.list.addBU(i,self.BM.getinfo(i))
    def addInstance(self):
        dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print(dir)
        print(self.box.text())
        if dir and self.box.text() != "":
            self.BM.newBackup(self.box.text(), dir)
        else:
            print("Adding Backup failed")
        self.list.clear()
        self.BackupList()
    def getThreads(self):
        try: return self.BM.getAmountOfThreads()
        except: return None
    def savetxt(self):
        try: self.BM.save_to_txt()
        except: print("no BM detected")
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.wid = Widget()
        self.setCentralWidget(self.wid)
        self.sb = QStatusBar()
        self.setStatusBar(self.sb)
    def update(self):
        self.sb.showMessage("Threads: " + str(self.wid.getThreads()))
    def closeEvent(self, event):
        if self.wid.BM is None:
            print("No Backup Manager loaded")
        else:
            self.wid.BM.close()
            print("Closing Backup Manager")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    win.update()
    sys.exit(app.exec_())