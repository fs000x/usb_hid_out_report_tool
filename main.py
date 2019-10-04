#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import pywinusb.hid as hid
from ui.usbHidTool import Ui_MainWindow
import pyperclip as clip

output_reports_index = 0

class usbHidToolWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(usbHidToolWindow, self).__init__(parent)
        self.setupUi(self)
        self.current_dev = 0
        self.hid_dev = None
        self.all_hids = None
        self.report_id = None
        self.output_report_len = 0
        self.target_usage = 0
        self.usage_id = 0
        self.pushButton_send.setEnabled(False)
        self.pushButton_refresh.setEnabled(True)
        self._refresh_hid_dev()

    def _decode_data(self, data):
        return chr(data)

    def _show_err(self, err_str):
        errwin = QMessageBox()
        errwin.setText(err_str)
        errwin.exec_()

    def _set_hid_dev_info(self):
        assert(self.hid_dev is not None)
        self.lineEdit_vid.setText("0x%04x" % self.hid_dev.vendor_id)
        self.lineEdit_vname.setText(self.hid_dev.vendor_name)
        self.lineEdit_pid.setText("0x%04x" % self.hid_dev.product_id)
        self.lineEdit_pname.setText(self.hid_dev.product_name)
        self.lineEdit_sn.setText(self.hid_dev.serial_number)

    def _set_hid_dev_report_info(self):
        #assert(self.hid_dev.is_opened())
        try:
            report = self.hid_dev.find_output_reports()[output_reports_index]
            self.report_id = report.report_id
            self.lineEdit_report_id.setText(hex(self.report_id))
            self.output_report_len = self.hid_dev.hid_caps.output_report_byte_length
            self.usage_id = list(report.keys())[output_reports_index]
        except Exception as err:
            print(err)

    def _clear_hid_dev_report_info(self):
        self.report_id = None
        self.lineEdit_report_id.clear()
        self.output_report_len = 0
        self.usage_id = 0

    def _refresh_hid_dev(self):
        #self.all_hids = hid.find_all_hid_devices()
        self.all_hids = hid.HidDeviceFilter().get_devices()
        self.comboBox_hid_devices.clear()
        self.comboBox_hid_devices.addItems([ dev.device_path for dev in self.all_hids])
        self.current_dev = self.comboBox_hid_devices.currentIndex()
        self.hid_dev = self.all_hids[self.current_dev]
        self.target_usage = hid.get_full_usage_id(0xff00, 0x02)
        self._set_hid_dev_info()

    def hid_dev_refresh(self):
        self._refresh_hid_dev()

    def copy_dev_path_pressed(self):
        clip.copy(self.comboBox_hid_devices.currentText())
        self.pushButton_copy_path.setText("Device Path Copyed")

    def copy_dev_path_released(self):
        self.pushButton_copy_path.setText("Copy Device Path")

    def hex_send_toggle(self, isHexSend):
        print(isHexSend)

    def timer_send_toggle(self, timerStart):
        print(timerStart)

    def hid_devices_actived(self, item):
        #print(item)
        self.current_dev = self.comboBox_hid_devices.currentIndex()
        self.hid_dev = self.all_hids[self.current_dev]
        self._set_hid_dev_info()

    def hid_dev_open(self):
        if self.hid_dev.is_opened():
            self.hid_dev.close()
            self.pushButton_Open.setText("Open")
            self.pushButton_send.setEnabled(False)
            self.comboBox_hid_devices.setEnabled(True)
            self.pushButton_refresh.setEnabled(True)
            self._clear_hid_dev_report_info()
        else:
            self.hid_dev.open()
            self.hid_dev.set_raw_data_handler(self.report_recv_handler)
            self.pushButton_Open.setText("Close")
            self.pushButton_send.setEnabled(True)
            self.comboBox_hid_devices.setEnabled(False)
            self.pushButton_refresh.setEnabled(False)
            self._set_hid_dev_report_info()

    def data_send(self):
        data_str = self.lineEdit_input.text()
        #print(data_str)
        data = [0x00] * self.output_report_len
        if not self.checkBox_hex.isChecked():
            data_list = [int(ord(d)) for d in list(data_str)]
        else:
            try:
                data_list = list(bytearray.fromhex(data_str))
            except Exception as err:
                self._show_err(str(err))
                return
        #print(data_list)
        data[0] = self.report_id
        for i, d in enumerate(data_list):
            data[i+1] = d
        self.hid_dev.send_output_report(data)
        time_str = time.strftime("%H:%M:%S", time.localtime())
        data_send_str = ''.join(map(self._decode_data, data[:len(data_list)+1]))
        tmp_str = "{} Send: {}".format(time_str, data_send_str[1:])
        tmp_hex_str = "{} Send: {}".format(time_str, ' '.join(map(lambda x: "%02x" % x, data)))
        self.textEdit_output_hex.append(tmp_hex_str)
        self.textEdit_output_str.append(tmp_str)

    def report_recv_handler(self, data):
        time_str = time.strftime("%H:%M:%S", time.localtime())
        data_str = "{} Recv: {}".format(time_str, ''.join(map(self._decode_data, data[1:])))
        data_hex_str = "{} Recv: {}".format(time_str, ' '.join(map(lambda x: "%02x" % x, data)))
        self.textEdit_output_str.append(data_str)
        self.textEdit_output_hex.append(data_hex_str)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    usbHidWin = usbHidToolWindow()
    usbHidWin.show()
    sys.exit(app.exec_())
