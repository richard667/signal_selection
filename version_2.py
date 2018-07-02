from PyQt5 import QtWidgets, uic, QtCore, Qt
from asammdf import MDF
import pandas as pd
import sys
from datetime import datetime


class Window_test(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window_test, self).__init__()
        uic.loadUi("version_2.ui", self)
        self.condition_combox.addItems(["step", "range", ">"])
        self.condition_combox.setItemText(0, "step")
        self.condition_combox_2.addItems(["step", "range", ">"])
        self.condition_combox_2.setItemText(0, "step")


        self.condition_combox.activated[str].connect(self.condition_select)
        self.condition_combox_2.activated[str].connect(self.condition_select)

        self.file_open_button.clicked.connect(self.openfiles)
        self.lower_range.setText("0")
        self.upper_range.setText("0")
        self.lower_range_2.setText("0")
        self.upper_range_2.setText("0")
        # self.export_csv_button.clicked.connect(self.delete_all_signals)
        self.export_csv_button.clicked.connect(self.to_csv)

        self.all_signals.itemDoubleClicked[QtWidgets.QListWidgetItem].connect(self.select_signal)
        self.selected_sig = set()   # 选中的信号，不可重复选
        self.selected_signals.itemDoubleClicked.connect(self.deselect_signal)
        self.all_signals.addItem("hello")

        self.add_condition_combox.addItem("")
        self.add_condition_combox.setItemText(0, "信号")
        self.add_condition_combox_2.addItem("")
        self.add_condition_combox_2.setItemText(0, "信号")
        # 等价于 self.add_condition_combox.addItem("信号")

        self.checkbox_1.stateChanged.connect(self.check)
        self.checkbox_2.stateChanged.connect(self.check)
        self.check_flag_1 = 0
        self.check_flag_2 = 0

        self.show()
    def openfiles(self):
        # 打开单个mdf文件
        self.all_signals.clear()
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName()
        if filename == "":
            return
        elif filename[-3:] not in ["dat", "mdf", "DAT", "MDF"]:
            QtWidgets.QMessageBox.about(self, "Message", "文件类型错误")
            return
        self.mdf_file = MDF(filename, memory="minimum")
        channel_list = list(self.mdf_file.channels_db.keys())
        channel_list.remove("time")
        channel_list.sort()
        self.all_signals.addItems(channel_list)


    def check(self, state):
        # checkbox选中才出现信号选项
        source = self.sender()
        try:
            self.mdf_file
        except:
            if self.checkbox_1.checkState() == 2:  # 0 表示未选中， 2表示选中
                QtWidgets.QMessageBox.about(self, "Message", "请先打开mdf文件")
            self.checkbox_1.setCheckState(0)
            self.checkbox_2.setCheckState(0)
            return
        channel_list = list(self.mdf_file.channels_db.keys())
        channel_list.remove("time")
        channel_list.sort()
        if source == self.checkbox_1 and state == QtCore.Qt.Checked:
            self.add_condition_combox.addItems(channel_list)
            self.check_flag_1 = 1

        if source == self.checkbox_2 and state == QtCore.Qt.Checked:
            self.add_condition_combox_2.addItems(channel_list)
            self.check_flag_2 = 1

    def select_signal(self, item):
        # print(item.text())  # QtWidgets.QListWidgetItem.text()
        # Adding the same QListWidgetItem multiple times to a QListWidget will result in undefined behavior.
        if item.text() not in self.selected_sig:
            self.selected_signals.addItem(item.text())
            self.selected_sig.add(item.text())

    def deselect_signal(self):
        text = self.selected_signals.takeItem(self.selected_signals.currentRow())
        self.selected_sig.remove(text.text())

    def delete_all_signals(self):
        self.selected_signals.clear()

    def condition_select(self, item):
        source = self.sender()
        if source == self.condition_combox:
            if item in ["step", "range"]:
                self.upper_range.show()
                self.label_2.show()
            elif item in [">", "="]:
                self.upper_range.hide()
                self.label_2.hide()
            else:
                pass
        if source == self.condition_combox_2:
            if item in ["step", "range"]:
                self.upper_range_2.show()
                self.label_3.show()
            elif item in [">", "="]:
                self.upper_range_2.hide()
                self.label_3.hide()
            else:
                pass
        else:
            pass

    def to_csv(self):
        condition = self.condition_combox.currentText()
        condition_2 = self.condition_combox_2.currentText()
        condition_channels = []
        condition_channels_2 = []
        end_indexes_1 = []
        start_indexes_1 = []
        end_indexes_2 = []
        start_indexes_2 = []
        if self.check_flag_1 == 1:
            if condition == "step":
                if not (self.lower_range.text().isdigit() and self.upper_range.text().isdigit()):
                    QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                    return
                lower_range = float(self.lower_range.text())
                upper_range = float(self.upper_range.text())
                print("___________")
                condition_channels.append(self.add_condition_combox.currentText())
                signal_samples = self.mdf_file.select(condition_channels)[0].samples
                print("-------------")
                start_flag = 0
                end_flag = 0

                for i, signal_sample in enumerate(signal_samples):
                    if signal_sample == lower_range and start_flag == 0:
                        start_indexes_1.append(i)
                        start_flag = 1
                    if signal_sample == upper_range and start_flag == 1:
                        start_flag = 0
                        end_flag = 1
                    if signal_sample != upper_range and end_flag == 1:
                        end_flag = 0
                        end_indexes_1.append(i)
                    if signal_sample == upper_range and start_flag ==1 and i == len(signal_samples)-1:
                        end_indexes_1.append(i+1)

            elif condition == "range":
                if not (self.lower_range.text().isdigit() and self.upper_range.text().isdigit()):
                    QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                    return
                lower_range = float(self.lower_range.text())
                upper_range = float(self.upper_range.text())
                print("___________")
                condition_channels.append(self.add_condition_combox.currentText())
                signal_samples = self.mdf_file.select(condition_channels)[0].samples
                print("-------------")
                start_flag = 0

                for i, signal_sample in enumerate(signal_samples):
                    if upper_range > signal_sample > lower_range and start_flag == 0:
                        start_indexes_1.append(i)
                        start_flag = 1
                    if (signal_sample > upper_range or signal_sample < lower_range) and start_flag == 1:
                        start_flag = 0
                        end_indexes_1.append(i)
                    if upper_range > signal_sample > lower_range and start_flag == 1 and i == len(signal_samples) - 1:
                        end_indexes_1.append(i+1)

            elif condition == ">":
                if not self.lower_range.text().isdigit():
                    QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                    return
                lower_range = float(self.lower_range.text())
                condition_channels.append(self.add_condition_combox.currentText())
                signal_samples = self.mdf_file.select(condition_channels)[0].samples
                print("-------------")
                start_flag = 0

                for i, signal_sample in enumerate(signal_samples):
                    if signal_sample > lower_range and start_flag == 0:
                        start_indexes_1.append(i)
                        start_flag = 1
                    if signal_sample < lower_range and start_flag == 1:
                        start_flag = 0
                        end_indexes_1.append(i)
                    if signal_sample > lower_range and start_flag == 1 and i == len(signal_samples) - 1:
                        end_indexes_1.append(i + 1)

            else:
                pass
        if self.check_flag_2 == 1:
            if condition_2 == "step":
                if not (self.lower_range_2.text().isdigit() and self.upper_range_2.text().isdigit()):
                    QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                    return
                lower_range_2 = float(self.lower_range_2.text())
                upper_range_2 = float(self.upper_range_2.text())
                print("___________")
                condition_channels_2.append(self.add_condition_combox_2.currentText())
                signal_samples_2 = self.mdf_file.select(condition_channels_2)[0].samples
                print("-------------")
                start_flag = 0
                end_flag = 0

                for i, signal_sample in enumerate(signal_samples_2):
                    if signal_sample == lower_range_2 and start_flag == 0:
                        start_indexes_2.append(i)
                        start_flag = 1
                    if signal_sample == upper_range_2 and start_flag == 1:
                        start_flag = 0
                        end_flag = 1
                    if signal_sample != upper_range_2 and end_flag == 1:
                        end_flag = 0
                        end_indexes_2.append(i)
                    if signal_sample == upper_range_2 and start_flag == 1 and i == len(signal_samples_2) - 1:
                        end_indexes_2.append(i + 1)

            elif condition_2 == "range":
                if not (self.lower_range_2.text().isdigit() and self.upper_range_2.text().isdigit()):
                    QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                    return
                lower_range_2 = float(self.lower_range_2.text())
                upper_range_2 = float(self.upper_range_2.text())
                print("___________")
                condition_channels_2.append(self.add_condition_combox_2.currentText())
                signal_samples_2 = self.mdf_file.select(condition_channels_2)[0].samples
                print("-------------")
                start_flag = 0

                for i, signal_sample in enumerate(signal_samples_2):
                    if upper_range_2 > signal_sample > lower_range_2 and start_flag == 0:
                        start_indexes_2.append(i)
                        start_flag = 1
                    if (signal_sample > upper_range_2 or signal_sample < lower_range_2) and start_flag == 1:
                        start_flag = 0
                        end_indexes_2.append(i)
                    if upper_range_2 > signal_sample > lower_range_2 and start_flag == 1 and i == len(signal_samples_2) - 1:
                        end_indexes_2.append(i + 1)


            elif condition_2 == ">":
                if not self.lower_range_2.text().isdigit():
                    QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                    return
                lower_range_2 = float(self.lower_range_2.text())
                condition_channels_2.append(self.add_condition_combox_2.currentText())
                signal_samples_2 = self.mdf_file.select(condition_channels_2)[0].samples
                print("-------------")
                start_flag = 0

                for i, signal_sample in enumerate(signal_samples_2):
                    if signal_sample > lower_range_2 and start_flag == 0:
                        start_indexes_2.append(i)
                        start_flag = 1
                    if signal_sample < lower_range_2 and start_flag == 1:
                        start_flag = 0
                        end_indexes_2.append(i)
                    if signal_sample > lower_range_2 and start_flag == 1 and i == len(signal_samples_2) - 1:
                        end_indexes_2.append(i + 1)
            else:
                pass

        print(start_indexes_1, start_indexes_2, sep="\n")
        print(end_indexes_1, end_indexes_2, sep="\n")
        if self.check_flag_1 == 1 and self.check_flag_2 == 0:
            count = self.selected_signals.count()
            items = []
            data_dict = {"timestamps": []}
            for i in range(count):
                items.append(self.selected_signals.item(i).text())
            selected_signals = self.mdf_file.select(items)
            timestamps = self.mdf_file.select(condition_channels)[0].timestamps
            for idx, signal in enumerate(selected_signals):
                data_dict[signal.name] = []
                for i, j in zip(start_indexes_1, end_indexes_1):
                    try:
                        data_dict[signal.name] += signal.interp(timestamps[i:j]).samples.tolist()
                        if idx == 0:
                            data_dict["timestamps"] += timestamps[i:j].tolist()
                    except:
                        print("error")
            print(data_dict)
            self.write_csv(data_dict)

        elif self.check_flag_1 == 1 and self.check_flag_2 == 1:
            # 先把两个索引扩展开，把中间的数填上，并把它变成集合，最后取两个集合交集
            index_1  = set()
            index_2 = set()
            for i, j in zip(start_indexes_1, end_indexes_1):
                for n in range(i, j+1):
                    index_1.add(n)
            for i, j in zip(start_indexes_2, end_indexes_2):
                for n in range(i, j+1):
                    index_2.add(n)
            indexes = index_1 and index_2
            # 获取需要导出的信号名
            count = self.selected_signals.count()
            items = []
            data_dict = {"timestamps": []}
            for i in range(count):
                items.append(self.selected_signals.item(i).text())
            selected_signals = self.mdf_file.select(items)
            timestamps = self.mdf_file.select(condition_channels)[0].timestamps
            # 把相应信号及其采样值做成字典，信号名作为键，采样值的列表作为值
            for idx, signal in enumerate(selected_signals):
                data_dict[signal.name] = []
                for i in indexes:
                    # data_dict.update({signal.name: signal.samples[i:j]})
                    try:
                        data_dict[signal.name].append(signal.interp(timestamps[i]).samples)
                        if idx == 0:
                            data_dict["timestamps"].append(timestamps[i])
                    except:
                        print("error")
            print(data_dict)
            self.write_csv(data_dict)
        else:
            QtWidgets.QMessageBox.about(self, "Message", "请按顺序勾选复选框")
            return

    def write_csv(self, data_dict):
        print("writing to csv..\n")
        df = pd.DataFrame(data=data_dict)
        timestamps = df['timestamps']
        df.drop(labels=['timestamps'], axis=1, inplace=True)
        df.insert(0, 'timestamps', timestamps)
        f_name = str(datetime.now()).split(".")[0].replace(":", "_", 2) + ".csv"
        f = open(f_name, "w")
        f.close()
        df.to_csv(f_name, index=False)
        print("finished")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window_test() #创建窗体对象
    sys.exit(app.exec_())


