from PySide6.QtCore import (QRunnable,
                            QThreadPool,
                            QTimer,
                            QObject,
                            Signal,
                            Slot)
import sys
import traceback

class RequestWorkerSignals(QObject):
    finished = Signal(int)  # 1 if finished 0 otherwise
    error = Signal(tuple)
    result = Signal(object)

class RequestWorker(QRunnable):
    """
    Only runs GET requests. No payload. Data passed as parameters in URL.
    """
    def __init__(self, req_fn, *args):
        super().__init__()
        self.fn = req_fn
        self.args = args
        self.signals = RequestWorkerSignals()

    @Slot()
    def run(self):
        try:
            data = self.fn(*self.args)
        except Exception as e:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(data) # return the data
        finally:
            self.signals.finished.emit(1)


