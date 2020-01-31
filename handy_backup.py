import Backup as B
import os
BM = B.BackupManager(r"C:\Users\Thomacdebabo\Desktop\Backups\SamsungA6")
BM.newBackup("SamsungA6Bilder", r"Dieser PC\Galaxy A6+\Phone\DCIM")
BM.backupALL()
BM.close()