import Backup as B

BM = B.BackupManager(r"E:\Backup")
BM.newBackup("Laptop_FL_Projects", r"C:\Users\Thomacdebabo\Documents\Image-Line\Data\FL Studio\Projects")
BM.newBackup("ETH_Documents", r"C:\Users\Thomacdebabo\Documents\ETH Documents")
BM.newBackup("Laptop_Bilder", r"C:\Users\Thomacdebabo\Pictures")

BM.print()

BM.backupALL()