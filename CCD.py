import ctypes
import numpy as np
from PyQt5.QtWidgets import QApplication
from contextlib import contextmanager
from CCDui import MainWindow


class CCD:
    dll = ctypes.WinDLL(r"C:\Program Files\Princeton Instruments\WinSpec\pvcam32.dll")

    def __init__(self, exp_time=1000, number_of_frames=1):
        self.gui = MainWindow()
        self.gui.widget.start_btn.clicked.connect(self.start)
        self.cam_name = ctypes.c_buffer(32)
        self.exp_time = ctypes.c_int(exp_time)
        self.hCam = ctypes.c_int16()
        self.size = ctypes.c_uint32()
        self.status = ctypes.c_int16()
        self.byte_cnt = ctypes.c_uint32()
        self.number_of_frames = number_of_frames

        class Region(ctypes.Structure):
            _fields_ = [('s1', ctypes.c_uint16),
                        ('s2', ctypes.c_uint16),
                        ('sbin', ctypes.c_uint16),
                        ('p1', ctypes.c_uint16),
                        ('p2', ctypes.c_uint16),
                        ('pbin', ctypes.c_uint16)]

        s1 = 0
        s2 = 1339
        p1 = 0
        p2 = 399
        self.region = Region(s1, s2, 1, p1, p2, 400)
        xc = 650
        self.data = self.gr900_1800(xc, 1800)

    def start(self):
        with self.open_camera():
            try:
                self.array = np.zeros(self.size.value, dtype=np.uint16)
                self.frame = self.array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16))
                for i in range(self.number_of_frames):
                    self.dll.pl_exp_start_seq(self.hCam, self.frame)
                    while self.dll.pl_exp_check_status(self.hCam, ctypes.byref(self.status),
                                                       ctypes.byref(self.byte_cnt)) and \
                            (self.status.value == 5 and self.status.value != 4):
                        pass
                    if self.status.value == 4:
                        print('readout failed')
                        break

                    self.data = np.column_stack((self.data, self.frame[0:1340]))
                    self.gui.widget.data_plot.plot(self.data[:, 0], self.frame[0:1340])
                    print('Frame = %i ' % i)
            finally:
                print('Error code:', self.dll.pl_error_code())

    @contextmanager
    def open_camera(self):
        self.dll.pl_pvcam_init()
        self.dll.pl_cam_get_name(0, ctypes.byref(self.cam_name))
        self.dll.pl_cam_open(self.cam_name, ctypes.byref(self.hCam), 0)
        self.dll.pl_exp_init_seq()
        self.dll.pl_exp_setup_seq(self.hCam, 1, 1, ctypes.byref(self.region), 0, self.exp_time, ctypes.byref(self.size))
        yield
        self.dll.pl_exp_finish_seq(self.hCam, self.frame, 0)
        self.dll.pl_exp_uninit_seq()
        self.dll.pl_cam_close(self.hCam)
        self.dll.pl_pvcam_uninit()

    @staticmethod
    def gr900_1800(xc, gratings):
        if gratings == 900:
            dx = 0.027142643764022978
            x_offset = 0.002714712485385462
            return np.linspace(xc - 1343 * dx / 2 - x_offset, xc + 1335 * dx / 2 - x_offset,
                               1340)  # if use central wevelenght
        elif gratings == 1800:
            x_offset = 0.03268222557835543
            dx = 0.010908887229220454
            return np.linspace(xc - 1343 * dx / 2 - x_offset, xc + 1335 * dx / 2 - x_offset, 1340)


if __name__ == '__main__':
    app = QApplication([])
    ccd = CCD()
    app.exec_()
