import Backup as B
import time

BM = B.BackupManager(r"C:\Users\Thomacdebabo\Desktop\Backups\Neue Backups")
# BM.newBackup("Hello", r"C:\Users\Thomacdebabo\Desktop\Backups\babab")
# BM.newBackup("Sachen", r"C:\Users\Thomacdebabo\Desktop\Backups\Sachen")
# BM.newBackup("Shiet", r"C:\Users\Thomacdebabo\Desktop\Backups\shit")
# BM.newBackup("Shiet", r"C:\Users\Thomacdebabo\Desktop\Backups\shit - Kopie")
BM.moveBackup(r"C:\Users\Thomacdebabo\Desktop\new")
BM.open_in_explorer("Hello")
BM.backupALL()
BM.deletePrevious()
BM.print()

BM.close()