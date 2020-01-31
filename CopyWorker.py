from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal
class WorkerSignal(QObject):
    finished = pyqtSignal()

class CopyWorker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(CopyWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignal()

    @pyqtSlot()
    def run(self):
        print("start thread")
        self.fn(*self.args)
        self.signals.finished.emit()
        print("thread done")
