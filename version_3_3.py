
# 修改信号选择框为QlineEdit, 并添加自动补全功能。
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from asammdf import MDF
import pandas as pd
import sys
from datetime import datetime
import json
from message import  get_message


class Window_test(QtWidgets.QMainWindow):
    def __init__(self):
        # 初始化
        super(Window_test, self).__init__()
        uic.loadUi("version_3_3_ui.ui", self)
        self.condition_combox.addItems(["step", "range", ">", "<"])
        self.condition_combox.setItemText(0, "step")
        self.condition_combox_2.addItems(["step", "range", ">", "<"])
        self.condition_combox_2.setItemText(0, "step")
        self.condition_combox.activated[str].connect(self.condition_select)
        self.condition_combox_2.activated[str].connect(self.condition_select)
        self.file_open_button.clicked.connect(self.openfiles)
        self.lower_range.setText("0")
        self.upper_range.setText("0")
        self.lower_range_2.setText("0")
        self.upper_range_2.setText("0")
        self.export_csv_button.clicked.connect(self.to_csv)

        self.all_signals.itemDoubleClicked[QtWidgets.QListWidgetItem].connect(self.select_signal)
        self.selected_sig = set()   # 选中的信号，不可重复选
        self.selected_signals.itemDoubleClicked.connect(self.deselect_signal)
        self.all_signals.addItem("hello")
        self.lineEdit.setText("信号")
        self.lineEdit_2.setText("信号")
        # self.add_condition_combox_2.addItem("")
        # self.add_condition_combox_2.setItemText(0, "信号")
        # 等价于 self.add_condition_combox.addItem("信号")
        # self.add_condition_combox.setMaxVisibleItems(20)
        # self.add_condition_combox_2.setMaxVisibleItems(20)

        self.checkbox_1.stateChanged.connect(self.check)
        self.checkbox_2.stateChanged.connect(self.check)
        self.check_flag_1 = 0
        self.check_flag_2 = 0
        self.statusBar().showMessage(get_message())

        self.save_config.clicked.connect(self.save_configs)
        self.load_config.clicked.connect(self.load_configs)
        self.filenames = []

        # self.add_condition_combox.setCompleter(self.completer)
        # self.add_condition_combox_2.setCompleter(self.completer)
        # QCompleter::UnfilteredPopupCompletion	1
        # All possible completions are displayed in a popup window with the most likely suggestion indicated as current.
        # 设置窗口图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("000.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.show()
    def openfiles(self):
        self.statusBar().showMessage('打开多个文件')
        self.all_signals.clear()
        files, filetype = QtWidgets.QFileDialog.getOpenFileNames(self, "选取文件", ".", "MDF Files (*.dat *.mdf *.DAT *.MDF);;All Files (*)")
        if not files:
            self.statusBar().showMessage(get_message())
            return
        for filename in files:
            if filename[-3:] in ["dat", "mdf", "DAT", "MDF"]:
                self.filenames.append(filename)
        # 把第一个文件里面的信号名加入到左下角的导出信号框中
        filename = self.filenames[0]
        self.mdf_file = MDF(filename, memory="minimum")   #
        signalnames = list(self.mdf_file.channels_db.keys())
        signalnames.sort()
        self.all_signals.addItems(signalnames)
        self.statusBar().showMessage(get_message())

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
        # 每次复选框状态变化，就把flag复位，然后根据信号选择是否置位
        if source == self.checkbox_1 and self.check_flag_1 == 1:
            self.check_flag_1 = 0
        if source == self.checkbox_2 and self.check_flag_2 == 1:
            self.check_flag_2 = 0
        if source == self.checkbox_1 and state == QtCore.Qt.Checked:
            # 将信号加入到条件框中
            channel_list = list(self.mdf_file.channels_db.keys())
            channel_list.remove("time")
            channel_list.sort()
            string = channel_list    # 预先设置列表
            completer = QtWidgets.QCompleter(string)
            # completer.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
            completer.setCaseSensitivity(0)
            self.lineEdit.setCompleter(completer)  # 将列表添加到lineEdit中
            self.check_flag_1 = 1

        if source == self.checkbox_2 and state == QtCore.Qt.Checked:
            channel_list = list(self.mdf_file.channels_db.keys())
            channel_list.remove("time")
            channel_list.sort()
            string = channel_list    # 预先设置列表
            completer = QtWidgets.QCompleter(string)
            # completer.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
            completer.setCaseSensitivity(0)
            self.lineEdit_2.setCompleter(completer)
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
            elif item in [">", "=", "<"]:
                self.upper_range.hide()
                self.label_2.hide()
            else:
                pass
        if source == self.condition_combox_2:
            if item in ["step", "range"]:
                self.upper_range_2.show()
                self.label_3.show()
            elif item in [">", "=", "<"]:
                self.upper_range_2.hide()
                self.label_3.hide()
            else:
                pass
        else:
            pass

    def save_configs(self):
        self.statusBar().showMessage("保存配置")
        configs = {"selected_signals":[]}
        # configs = {}
        if self.checkbox_1.checkState() == 2:
            configs["checkbox_1"] = True
            configs["condition_signal"] = self.lineEdit.text()
            configs["condition"] = self.condition_combox.currentText()
            configs["lower_range"] = self.lower_range.text()
            configs["upper_range"] = self.upper_range.text()

        if self.checkbox_2.checkState() == 2:
            configs["checkbox_2"] = True
            configs["condition_signal_2"] = self.lineEdit_2.text()
            configs["condition_2"] = self.condition_combox_2.currentText()
            configs["lower_range_2"] = self.lower_range_2.text()
            configs["upper_range_2"] = self.upper_range_2.text()
        for i in range(self.selected_signals.count()):
            configs["selected_signals"].append(self.selected_signals.item(i).text())

        filename, okpressed = QtWidgets.QInputDialog.getText(self, "保存配置", "请输入文件名:", QtWidgets.QLineEdit.Normal, "")
        if okpressed and filename.strip():
            with open(filename + ".json", "w") as f:
                json.dump(configs, f)
        self.statusBar().showMessage(get_message())

    def load_configs(self):
        self.statusBar().showMessage("导入筛选条件")
        filename, filetype = QtWidgets.QFileDialog().getOpenFileName(self, "选取文件", ".", "Json Files (*.json);;All Files (*)")
        if filename:
            with open(filename, "r") as f:
                configs = json.load(f)
            if "checkbox_1" in configs.keys():
                self.checkbox_1.setCheckState(2)
                self.lineEdit.setText(configs["condition_signal"])
                self.condition_combox.setCurrentText(configs["condition"])
                self.lower_range.setText(configs["lower_range"])
                self.upper_range.setText(configs["upper_range"])
            if "checkbox_2" in configs.keys():
                self.checkbox_2.setCheckState(2)
                self.lineEdit_2.setText(configs["condition_signal_2"])
                self.condition_combox_2.setCurrentText(configs["condition_2"])
                self.lower_range_2.setText(configs["lower_range_2"])
                self.upper_range_2.setText(configs["upper_range_2"])
            self.selected_sig = set(configs["selected_signals"])
            self.selected_signals.addItems(list(self.selected_sig))
        self.statusBar().showMessage(get_message())

    def to_csv(self):
        data_dict = {"timestamps": [], "filename": []}
        if self.check_flag_1 == 1 and self.check_flag_2 == 0:
            data_dict["duration"] = []
        for filename in self.filenames:
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
                    condition_channels.append(self.lineEdit.text())
                    mdf = MDF(filename, "minimum")
                    signal_samples = mdf.select(condition_channels)[0].samples
                    self.statusBar().showMessage("处理第一个筛选条件")
                    for i in range(len(signal_samples)-1):
                        if signal_samples[i] == lower_range and signal_samples[i+1] == upper_range:
                            start_indexes_1.append(i)
                            end_indexes_1.append(i+1)
                    # for i, signal_sample in enumerate(signal_samples):
                    #     if signal_sample == lower_range and start_flag == 0:
                    #         start_indexes_1.append(i)
                    #         start_flag = 1
                    #     if signal_sample == upper_range and start_flag == 1:
                    #         start_flag = 0
                    #         end_flag = 1
                    #     if signal_sample != upper_range and end_flag == 1:
                    #         end_flag = 0
                    #         end_indexes_1.append(i)
                    #     if signal_sample == upper_range and start_flag ==1 and i == len(signal_samples)-1:
                    #         end_indexes_1.append(i+1)

                elif condition == "range":
                    if not (self.lower_range.text().isdigit() and self.upper_range.text().isdigit()):
                        QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                        return
                    lower_range = float(self.lower_range.text())
                    upper_range = float(self.upper_range.text())
                    condition_channels.append(self.lineEdit.text())
                    mdf = MDF(filename, "minimum")
                    signal_samples = mdf.select(condition_channels)[0].samples
                    self.statusBar().showMessage("处理第一个筛选条件")
                    start_flag = 0

                    for i, signal_sample in enumerate(signal_samples):
                        if upper_range >= signal_sample >= lower_range and start_flag == 0:
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
                    condition_channels.append(self.lineEdit.text())
                    mdf = MDF(filename, "minimum")
                    signal_samples = mdf.select(condition_channels)[0].samples
                    self.statusBar().showMessage("处理第一个筛选条件")
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

                elif condition == "<":
                    if not self.upper_range.text().isdigit():
                        QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                        return
                    upper_range = float(self.upper_range.text())
                    condition_channels.append(self.lineEdit.text())
                    mdf = MDF(filename, "minimum")
                    signal_samples = mdf.select(condition_channels)[0].samples
                    self.statusBar().showMessage("处理第一个筛选条件")
                    start_flag = 0

                    for i, signal_sample in enumerate(signal_samples):
                        if signal_sample < upper_range and start_flag == 0:
                            start_indexes_1.append(i)
                            start_flag = 1
                        if signal_sample > upper_range and start_flag == 1:
                            start_flag = 0
                            end_indexes_1.append(i)
                        if signal_sample < upper_range and start_flag == 1 and i == len(signal_samples) - 1:
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
                    condition_channels_2.append(self.lineEdit_2.text())
                    mdf = MDF(filename, "minimum")
                    signal_samples_2 = mdf.select(condition_channels_2)[0].samples
                    self.statusBar().showMessage("处理第二个筛选条件")
                    for i in range(len(signal_samples_2)-1):
                        if signal_samples_2[i] == lower_range_2 and signal_samples_2[i+1] == upper_range_2:
                            start_indexes_2.append(i)
                            end_indexes_2.append(i+1)

                elif condition_2 == "range":
                    if not (self.lower_range_2.text().isdigit() and self.upper_range_2.text().isdigit()):
                        QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                        return
                    lower_range_2 = float(self.lower_range_2.text())
                    upper_range_2 = float(self.upper_range_2.text())
                    condition_channels_2.append(self.lineEdit_2.text())
                    mdf = MDF(filename, "minimum")
                    signal_samples_2 = mdf.select(condition_channels_2)[0].samples
                    self.statusBar().showMessage("处理第二个筛选条件")
                    start_flag = 0

                    for i, signal_sample in enumerate(signal_samples_2):
                        if upper_range_2 >= signal_sample >= lower_range_2 and start_flag == 0:
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
                    condition_channels_2.append(self.lineEdit_2.text())
                    mdf = MDF(filename, "minimum")
                    signal_samples_2 = mdf.select(condition_channels_2)[0].samples
                    self.statusBar().showMessage("处理第二个筛选条件")
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
                elif condition_2 == "<":
                    if not self.upper_range_2.text().isdigit():
                        QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                        return
                    upper_range_2 = float(self.upper_range_2.text())
                    condition_channels_2.append(self.lineEdit_2.text())
                    mdf = MDF(filename, "minimum")
                    signal_samples_2 = mdf.select(condition_channels_2)[0].samples
                    self.statusBar().showMessage("处理第二个筛选条件")
                    start_flag = 0

                    for i, signal_sample in enumerate(signal_samples_2):
                        if signal_sample > upper_range_2 and start_flag == 0:
                            start_indexes_2.append(i)
                            start_flag = 1
                        if signal_sample < upper_range_2 and start_flag == 1:
                            start_flag = 0
                            end_indexes_2.append(i)
                        if signal_sample > upper_range_2 and start_flag == 1 and i == len(signal_samples_2) - 1:
                            end_indexes_2.append(i + 1)

                else:
                    pass
            if self.check_flag_1 == 1 and self.check_flag_2 == 0:
                self.statusBar().showMessage("getting selected signal")
                mdf = MDF(filename, "minimum")
                timestamps = mdf.select(condition_channels)[0].timestamps
                count = self.selected_signals.count()
                for i in range(count):
                    signal_name = self.selected_signals.item(i).text()
                    selected_signal = mdf.select([signal_name])[0]    # mdf的select方法参数必须为list
                    if self.selected_signals.item(i).text() not in data_dict.keys():
                        data_dict[self.selected_signals.item(i).text()] = []
                    for k, j in zip(start_indexes_1, end_indexes_1):
                        try:
                            data_dict[self.selected_signals.item(i).text()] += selected_signal.interp(timestamps[k:j]).samples.tolist()
                        except:
                            self.statusBar().showMessage("error")
                for i, j in zip(start_indexes_1, end_indexes_1):
                    try:
                        data_dict["timestamps"] += timestamps[i:j].tolist()
                        duration = timestamps[j-1].tolist() - timestamps[i].tolist()
                        for _ in range(i, j):
                            data_dict["filename"].append(filename)
                            data_dict["duration"].append(duration)
                    except:
                        self.statusBar().showMessage("error")

            elif self.check_flag_1 == 1 and self.check_flag_2 == 1:
                self.statusBar().showMessage("生成最终索引")
                # 先把两个索引扩展开，把中间的数填上，并把它变成集合，最后取两个集合交集
                index_1 = set()
                index_2 = set()
                for i, j in zip(start_indexes_1, end_indexes_1):
                    for n in range(i, j):
                        index_1.add(n)
                for i, j in zip(start_indexes_2, end_indexes_2):
                    for n in range(i, j):
                        index_2.add(n)
                indexes = index_1 & index_2
                mdf = MDF(filename, "minimum")
                timestamps = mdf.select(condition_channels)[0].timestamps
                # 获取需要导出的信号名
                self.statusBar().showMessage("提取数据中...")
                count = self.selected_signals.count()
                for i in range(count):
                    signal_name = self.selected_signals.item(i).text()
                    selected_signal = mdf.select([signal_name])[0]
                    if self.selected_signals.item(i).text() not in data_dict.keys():
                        data_dict[self.selected_signals.item(i).text()] = []
                # 把相应信号及其采样值做成字典，信号名作为键，采样值的列表作为值
                    for k in indexes:
                        try:
                            # data_dict[self.selected_signals.item(i).text()].append(selected_signal.interp([timestamps[k]]).samples.tolist())
                            data_dict[self.selected_signals.item(i).text()] += selected_signal.interp([timestamps[k]]).samples.tolist()
                        except:
                            # print("k=", k)
                            self.statusBar().showMessage("error？？")
                for i in indexes:
                    try:

                        data_dict["timestamps"].append(timestamps[i])
                        data_dict["filename"].append(filename)
                    except:
                        # print("i=", i)
                        self.statusBar().showMessage("error")
            else:
                QtWidgets.QMessageBox.about(self, "Message", "请按顺序勾选复选框")
                print(self.check_flag_1, self.check_flag_2)
                return
        self.write_csv(data_dict)

    def write_csv(self, data_dict):
        self.statusBar().showMessage("数据写入中...")
        # for key in data_dict.keys():
        #     print(key, len(data_dict[key]))
        try:
            df = pd.DataFrame(data=data_dict)
        except ValueError:
            QtWidgets.QMessageBox.about(self, "Message", "某些信号采样值缺失")
            self.statusBar().showMessage(get_message())
            return
        # 重新排序列，把timestamps排在第一列
        timestamps = df['timestamps']
        df.drop(labels=['timestamps'], axis=1, inplace=True)
        df.insert(0, 'timestamps', timestamps)
        # 保存的文件名
        f_name = str(datetime.now()).split(".")[0].replace(":", "_", 2) + ".csv"
        f = open(f_name, "w")
        f.close()
        df.to_csv(f_name, index=False, encoding="gb2312")
        self.statusBar().showMessage("finished")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window_test()  # 创建窗体对象
    sys.exit(app.exec_())


