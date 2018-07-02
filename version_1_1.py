# -*- coding: utf-8 -*-
# 一次性把所有信号，所有数据读入到变量self.data中，以后不再打开文件

from PyQt5 import QtCore, QtGui, QtWidgets
import os
from asammdf import MDF
import asammdfgui
import pandas as pd

class Ui_Form(QtWidgets.QWidget):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(599, 468)

        self.file_open_button = QtWidgets.QPushButton(Form)
        self.file_open_button.setGeometry(QtCore.QRect(60, 20, 75, 23))
        self.file_open_button.setObjectName("file_open_button")
        self.file_open_button.clicked.connect(self.openfiles)


        self.condition_combox = QtWidgets.QComboBox(Form)
        self.condition_combox.setGeometry(QtCore.QRect(290, 70, 70, 20))
        self.condition_combox.setObjectName("condition_combox")
        self.condition_combox.addItems(["step", "range", ">", "="])
        self.condition_combox.activated[str].connect(self.condition_select)

        self.lower_range = QtWidgets.QLineEdit(Form)
        self.lower_range.setGeometry(QtCore.QRect(372, 70, 61, 20))
        self.lower_range.setObjectName("lower_range")
        self.lower_range.setText("0")

        self.upper_range = QtWidgets.QLineEdit(Form)
        self.upper_range.setGeometry(QtCore.QRect(460, 70, 61, 20))
        self.upper_range.setObjectName("upper_range")
        self.upper_range.setText("0")

        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(440, 70, 16, 16))
        self.label_2.setObjectName("label_2")


        self.add_condition_combox = QtWidgets.QComboBox(Form)
        self.add_condition_combox.setGeometry(QtCore.QRect(50, 70, 200, 23))
        self.add_condition_combox.setObjectName("add_condition_combox")
        self.add_condition_combox.addItem("")

        self.export_csv_button = QtWidgets.QPushButton(Form)
        self.export_csv_button.setGeometry(QtCore.QRect(270, 410, 75, 23))
        self.export_csv_button.setObjectName("export_csv_button")
        # self.export_csv_button.clicked.connect(self.delete_all_signals)
        self.export_csv_button.clicked.connect(self.to_csv)

        self.all_signals = QtWidgets.QListWidget(Form)
        self.all_signals.setGeometry(QtCore.QRect(10, 150, 256, 192))
        self.all_signals.setObjectName("all_signals")
        self.all_signals.itemDoubleClicked[QtWidgets.QListWidgetItem].connect(self.select_signal)
        self.selected_sig = set()   # 选中的信号，不可重复选

        self.selected_signals = QtWidgets.QListWidget(Form)
        self.selected_signals.setGeometry(QtCore.QRect(320, 150, 256, 192))
        self.selected_signals.setObjectName("selected_signals")
        self.selected_signals.itemDoubleClicked.connect(self.deselect_signal)


        self.all_signals.addItem("hello")


        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.file_open_button.setText(_translate("Form", "打开MDF"))
        # self.condition_combox.setItemText(0, _translate("Form", "step"))
        self.add_condition_combox.setItemText(0, _translate("Form", "信号"))
        self.label_2.setText(_translate("Form", "-"))
        self.export_csv_button.setText(_translate("Form", "导出csv"))

    def openfiles(self):
        # 打开单个mdf文件
        self.all_signals.clear()
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName()
        if filename[-3:] not in ["dat", "mdf", "DAT", "MDF"]:
            QtWidgets.QMessageBox.about(self, "Message", "文件类型错误")
            return
        self.mdf_file = MDF(filename, memory="minimum")
        channel_list = list(self.mdf_file.channels_db.keys())
        channel_list.remove("time")
        channel_list.sort()
        self.add_condition_combox.addItems(channel_list)
        self.all_signals.addItems(channel_list)


        # 打开多个mdf文件
        # filenames, filetype= QtWidgets.QFileDialog.getOpenFileNames()
        # for filename in filenames:
        #     file = MDF(filename, memory="minimum")
        #     channel_list = list(file.channels_db.keys())
        #     channel_list.remove("time")                   # 多个文件时间可能不同，因此该程序肯定有问题，不管。
        #     channel_list.sort()
        #     self.data += file.select(channel_list)
        #     for channel in channel_list:
        #         self.all_signals.addItem(channel)

        # 打开一个文件夹下的所有mdf文件。但具体是否可行未知,或者把上面程序多运行几遍
        # dir = os.listdir(QtWidgets.QFileDialog.getExistingDirectory())
        # mdf_files = [mdf_file for mdf_file in dir if mdf_file[-3:] in ["dat", "mdf", "DAT", "MDF"]]
        # mdf = MDF()
        # mdf.stack(mdf_files, memory='minimum')
        # signals = mdf.iter_channels()  # generator that yields a Signal for each non-master channel
        # for signal in signals:
        #     self.all_signals.addItem(signal)

    def select_signal(self, item):
        # print(item.text())  # QtWidgets.QListWidgetItem.text()
        # Adding the same QListWidgetItem multiple times to a QListWidget will result in undefined behavior.
        if item.text() not in self.selected_sig:
            self.selected_signals.addItem(item.text())
            self.selected_sig.add(item.text())

    def deselect_signal(self):
        self.selected_signals.takeItem(self.selected_signals.currentRow())

    def delete_all_signals(self):
        self.selected_signals.clear()

    def condition_select(self, item):
        if item in ["step", "range"]:
            self.upper_range.show()
            self.label_2.show()
        elif item in [">", "="]:
            self.upper_range.hide()
            self.label_2.hide()
        else:
            pass


    def to_csv(self):
        condition = self.condition_combox.currentText()
        channels = []      # 条件信号
        if not (self.lower_range.text().isdigit() and self.upper_range.text().isdigit()):
            QtWidgets.QMessageBox.about(self, "Message", "范围错误")
            return
        lower_range = float(self.lower_range.text())
        upper_range = float(self.upper_range.text())
        if condition == "step":
            signal_samples = self.mdf_file.select(self.add_condition_combox.currentText()).samples
            signal_time = self.mdf_file.select(self.add_condition_combox.currentText()).time
            print(signal_samples)
            print(signal_time)

        elif condition == "range":
            print(self.lower_range.text())
            print(self.upper_range.text())

        elif condition == ">":
            print(">")
            start_time = []
            channels.append(self.add_condition_combox.currentText())
            try:
                signal_samples = self.mdf_file.select(channels)[0].samples
                signal_time = self.mdf_file.select(channels)[0].timestamps
            except:
                print("信号错误")
            for i, signal_sample in enumerate(signal_samples):
                if signal_sample > lower_range:
                    start_time.append(i)
        elif condition == "=":
            print("=")
        else:
            pass
        count = self.selected_signals.count()
        items = []
        data_dict = {}
        for i in range(count):
            items.append(self.selected_signals.item(i).text())
        signals = self.mdf_file.select(items)   # 当存在空数据时，会出错
        try:
            for signal in signals:
                for i in start_time:
                    data_dict.update({signal.name: signal.samples[i]})
            print(data_dict)
            for i in start_time:
                data_dict.update({"timestamps": signals[0].timestamps[i]})
            print(data_dict)
            df = pd.DataFrame(data=data_dict)
            print("-"*20)
            df.to_csv("11.csv", index=False)
        except:
            print("write error")





