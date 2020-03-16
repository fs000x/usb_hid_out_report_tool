#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import QtCore, QtGui
import pywinusb.hid as hid
from ui.usbHidTool import Ui_MainWindow
import pyperclip as clip
import configparser as cfgpar

config_file = "tool.conf"
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
        self.timer_thread = None
        self.cfg = None
        self.cfg_file = None
        self._config_init()
        self.pushButton_send.setEnabled(False)
        self.pushButton_refresh.setEnabled(True)
        self.checkBox_timer.setEnabled(False)
        self._pushButton_ex_init(self.cfg)
        self._pushButton_ex_disable()
        time_regex = QtCore.QRegExp("[0-9]*")
        time_validator = QtGui.QRegExpValidator(time_regex, self.lineEdit_time)
        self.lineEdit_time.setValidator(time_validator)
        self.lineEdit_time.setMaxLength(9)
        self._refresh_hid_dev()

    def __del__(self):
        if self.hid_dev.is_opened():
            self.checkBox_timer.setChecked(False)
            self.hid_dev.close()
        self._config_write()

    def _config_init(self):
        self.cfg = cfgpar.ConfigParser()
        try:
            self.cfg.read(config_file)
            if not self.cfg.has_section("more_commands"):
                self.cfg.add_section("more_commands")
        except Exception as err:
            print(err)

        self.cfg_file = open(config_file, 'w')

    def _config_get(self, section, key):
        try:
            return self.cfg.get(section, key)
        except Exception as err:
            print(err)
            return ""

    def _config_write(self):
        if self.cfg:
            for i in range(1, 17):
                exec("self.tmp_cmd = self.lineEdit_ex_{}.text()".format(i))
                self.cfg.set("more_commands", "cmd_ex_{}".format(i), self.tmp_cmd)
            if self.cfg_file:
                self.cfg.write(self.cfg_file)
                self.cfg_file.close()


    def _pushButton_ex_init(self, cfg):
        try:
            for i in range(1, 17):
                cmd_str = self._config_get("more_commands", "cmd_ex_{}".format(i))
                exec("self.lineEdit_ex_{}.setText(cmd_str)".format(i))
        except Exception as err:
            print(err)

        for i in range(1, 17):
            exec("self.pushButton_ex_{}.pressed.connect(self.button_pressed_ex_{})".format(i, i))


    def _pushButton_ex_disable(self):
        for i in range(1, 17):
            exec("self.pushButton_ex_{}.setEnabled(False)".format(i))

    def _pushButton_ex_enable(self):
        for i in range(1, 17):
            exec("self.pushButton_ex_{}.setEnabled(True)".format(i))

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
            self.lineEdit_report_id.setText("0x%02x" % self.report_id)
            self.output_report_len = self.hid_dev.hid_caps.output_report_byte_length
            self.usage_id = list(report.keys())[output_reports_index]
        except IndexError:
            self.pushButton_Open.click()
            self._show_err("Device Not Have Output Report")
        except Exception as err:
            self._show_err(str(err))

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

    def _report_data_send(self, data_list):
        #print(data_list)
        if len(data_list) > self.output_report_len-1:
            self._show_err("Command Len Too Long, report Len is %s" % self.output_report_len)
            return

        data = [0x00] * self.output_report_len
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

    def hid_dev_refresh(self):
        self._refresh_hid_dev()

    def copy_dev_path_pressed(self):
        clip.copy(self.comboBox_hid_devices.currentText())
        self.pushButton_copy_path.setText("Device Path Copy")

    def copy_dev_path_released(self):
        self.pushButton_copy_path.setText("Copy Device Path")

    def hex_send_toggle(self, isHexSend):
        data_str = self.lineEdit_input.text()
        if isHexSend:
            data_list = [int(ord(d)) for d in list(data_str)]
            self.lineEdit_input.setText(' '.join(map(lambda x: "%02x" % x, data_list)))
            hex_regex = QtCore.QRegExp("[a-fA-F0-9 ]*")
            hex_validator = QtGui.QRegExpValidator(hex_regex, self.lineEdit_input)
            self.lineEdit_input.setValidator(hex_validator)
        else:
            cmd_regex = QtCore.QRegExp(".*")
            cmd_validator = QtGui.QRegExpValidator(cmd_regex, self.lineEdit_input)
            self.lineEdit_input.setValidator(cmd_validator)
            try:
                data_list = list(bytearray.fromhex(data_str))
                self.lineEdit_input.setText(''.join(map(self._decode_data, data_list)))
            except Exception:
                self._show_err("Command Format Error")
                #self.checkBox_hex.setCheckState(2)
                self.checkBox_hex.setChecked(False)
                return

    def _timer_run(self, timeInterval):
        while self.checkBox_timer.isChecked():
            #print(timeInterval/1000)
            self.data_send()
            time.sleep(timeInterval/1000)

    def timer_send_toggle(self, timerStart):
        #print("timerStart"+str(timerStart))
        #print(self.timer_thread)
        #print(threading.enumerate())
        #print(threading.activeCount())
        if timerStart:
            if len(self.lineEdit_time.text()) == 0:
                self._show_err("Time(ms) must be set")
                self.checkBox_timer.setChecked(False)
                return
            timeInterval = int(self.lineEdit_time.text())
            self.timer_thread = threading.Thread(target=self._timer_run, name="timer_loop", args=(timeInterval,))
            self.timer_thread.start()
        elif self.timer_thread and self.timer_thread.isAlive:
            #print("stop thread")
            self.timer_thread = None



    def hid_devices_actived(self, item):
        self.current_dev = self.comboBox_hid_devices.currentIndex()
        self.hid_dev = self.all_hids[self.current_dev]
        self._set_hid_dev_info()

    def hid_dev_open(self):
        if self.hid_dev.is_opened():
            self.checkBox_timer.setChecked(False)
            self.hid_dev.close()
            self.pushButton_Open.setText("Open")
            self.pushButton_send.setEnabled(False)
            self.checkBox_timer.setEnabled(False)
            self.comboBox_hid_devices.setEnabled(True)
            self.pushButton_refresh.setEnabled(True)
            self._pushButton_ex_disable()
            self._clear_hid_dev_report_info()
        else:
            self.hid_dev.open()
            self.hid_dev.set_raw_data_handler(self.report_recv_handler)
            self.pushButton_Open.setText("Close")
            self.pushButton_send.setEnabled(True)
            self.checkBox_timer.setEnabled(True)
            self.comboBox_hid_devices.setEnabled(False)
            self.pushButton_refresh.setEnabled(False)
            self._pushButton_ex_enable()
            self._set_hid_dev_report_info()

    def data_send(self):
        data_str = self.lineEdit_input.text()
        if len(data_str) == 0:
            return
        #print(data_str)
        if not self.checkBox_hex.isChecked():
            data_list = [int(ord(d)) for d in list(data_str)]
        else:
            try:
                data_list = list(bytearray.fromhex(data_str))
            except Exception:
                self._show_err("Command Format Error")
                return
        self._report_data_send(data_list)

    def more_command_send(self, text):
        if len(text) == 0:
            return
        data_str = text
        if not self.checkBox_hex.isChecked():
            data_list = [int(ord(d)) for d in list(data_str)]
        else:
            try:
                data_list = list(bytearray.fromhex(data_str))
            except Exception:
                self._show_err("Command Format Error")
                return
        self._report_data_send(data_list)

    def button_pressed_ex_1(self):
        self.more_command_send(self.lineEdit_ex_1.text())
    def button_pressed_ex_2(self):
        self.more_command_send(self.lineEdit_ex_2.text())
    def button_pressed_ex_3(self):
        self.more_command_send(self.lineEdit_ex_3.text())
    def button_pressed_ex_4(self):
        self.more_command_send(self.lineEdit_ex_4.text())
    def button_pressed_ex_5(self):
        self.more_command_send(self.lineEdit_ex_5.text())
    def button_pressed_ex_6(self):
        self.more_command_send(self.lineEdit_ex_6.text())
    def button_pressed_ex_7(self):
        self.more_command_send(self.lineEdit_ex_7.text())
    def button_pressed_ex_8(self):
        self.more_command_send(self.lineEdit_ex_8.text())
    def button_pressed_ex_9(self):
        self.more_command_send(self.lineEdit_ex_9.text())
    def button_pressed_ex_10(self):
        self.more_command_send(self.lineEdit_ex_10.text())
    def button_pressed_ex_11(self):
        self.more_command_send(self.lineEdit_ex_11.text())
    def button_pressed_ex_12(self):
        self.more_command_send(self.lineEdit_ex_12.text())
    def button_pressed_ex_13(self):
        self.more_command_send(self.lineEdit_ex_13.text())
    def button_pressed_ex_14(self):
        self.more_command_send(self.lineEdit_ex_14.text())
    def button_pressed_ex_15(self):
        self.more_command_send(self.lineEdit_ex_15.text())
    def button_pressed_ex_16(self):
        self.more_command_send(self.lineEdit_ex_16.text())

    def report_recv_handler(self, data):
        time_str = time.strftime("%H:%M:%S", time.localtime())
        data_str = "{} Recv: {}".format(time_str, ''.join(map(self._decode_data, data[1:])))
        data_hex_str = "{} Recv: {}".format(time_str, ' '.join(map(lambda x: "%02x" % x, data)))
        self.textEdit_output_str.append(data_str)
        self.textEdit_output_str.moveCursor(self.textEdit_output_str.textCursor().End)
        self.textEdit_output_hex.append(data_hex_str)
        self.textEdit_output_hex.moveCursor(self.textEdit_output_hex.textCursor().End)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    usbHidWin = usbHidToolWindow()
    usbHidWin.show()
    sys.exit(app.exec_())
