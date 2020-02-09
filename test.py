import Backup as B
import time

BM = B.BackupManager(r"D:/BackupManager")
# BM.newBackup("Hello", r"C:\Users\Thomacdebabo\Desktop\Backups\babab")
# BM.newBackup("Sachen", r"C:\Users\Thomacdebabo\Desktop\Backups\Sachen")
# BM.newBackup("Shiet", r"C:\Users\Thomacdebabo\Desktop\Backups\shit")
# BM.newBackup("Shiet", r"C:\Users\Thomacdebabo\Desktop\Backups\shit - Kopie")
BM.moveBackupManager(r"E:\Old_Baackups")
BM.print()

input("waiting for key pressed")
BM.close()