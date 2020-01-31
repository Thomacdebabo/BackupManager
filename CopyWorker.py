from PyQt5.QtCore import QRunnable, pyqtSlot

class CopyWorker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(CopyWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        print("start thread")
        self.fn(*self.args)
        print("thread done")