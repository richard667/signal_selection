from PyQt5 import QtWidgets, uic
from asammdf import MDF
import pandas as pd
import sys
from datetime import datetime


class Window_test(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window_test, self).__init__()
        uic.loadUi("version_1.ui", self)
        self.condition_combox.addItems(["step", "range", ">", "="])
        self.condition_combox.setItemText(0, "step")
        self.condition_combox.activated[str].connect(self.condition_select) # 当改变筛选方式时，调用condition_select函数

        self.file_open_button.clicked.connect(self.openfiles)  # 打开mdf

        self.lower_range.setText("0")
        self.upper_range.setText("0")
        # self.export_csv_button.clicked.connect(self.delete_all_signals)
        self.export_csv_button.clicked.connect(self.to_csv) # 导出到csv

        self.all_signals.itemDoubleClicked[QtWidgets.QListWidgetItem].connect(self.select_signal)  # 双击选要导出的信号
        self.all_signals.addItem("hello")

        self.selected_sig = set()   # 导出的信号，不可重复选
        self.selected_signals.itemDoubleClicked.connect(self.deselect_signal) # 双击删除导出的信号

        self.add_condition_combox.addItem("")
        self.add_condition_combox.setItemText(0, "信号")
        # 等价于 self.add_condition_combox.addItem("信号")

        self.show() # 显示窗口

    def openfiles(self):
        # 打开单个mdf文件
        self.all_signals.clear()     # 先清除上一个文件的信号
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName()
        if filename[-3:] not in ["dat", "mdf", "DAT", "MDF"]:
            QtWidgets.QMessageBox.about(self, "Message", "文件类型错误")
            return

        # 把信号显示在左边框中
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
        text = self.selected_signals.takeItem(self.selected_signals.currentRow())
        self.selected_sig.remove(text.text())

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
        condition = self.condition_combox.currentText()  # 筛选方式
        condition_channels = []  # 筛选所用的信号

        if condition == "step":
            if not (self.lower_range.text().isdigit() and self.upper_range.text().isdigit()):
                QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                return
            lower_range = float(self.lower_range.text())
            upper_range = float(self.upper_range.text())
            print("___________")
            # 得到筛选所用信号的samples值
            condition_channels.append(self.add_condition_combox.currentText())
            signal_samples = self.mdf_file.select(condition_channels)[0].samples
            timestamps = self.mdf_file.select(condition_channels)[0].timestamps
            print("-------------")
            # start_indexes 和 end_indexes分别是起始和终止索引
            start_flag = 0
            start_indexes = []
            end_flag = 0
            end_indexes = []

            for i, signal_sample in enumerate(signal_samples):
                if signal_sample == lower_range and start_flag == 0:
                    start_indexes.append(i)
                    start_flag = 1
                if signal_sample == upper_range and start_flag == 1:
                    start_flag = 0
                    end_flag = 1
                if signal_sample != upper_range and end_flag == 1:
                    end_flag = 0
                    end_indexes.append(i)
                if signal_sample == upper_range and start_flag ==1 and i == len(signal_samples)-1:
                    end_indexes.append(i+1)

            # 把所需导出的信号名添加到items中，并从mdf中获得其值，得到selected_signals
            count = self.selected_signals.count()
            items = []
            data_dict = {"timestamps": []}
            for i in range(count):
                items.append(self.selected_signals.item(i).text())
            selected_signals = self.mdf_file.select(items)

            # 将所需信号满足条件的片段筛选出来，加入到data_dict中，并添加时间戳
            for idx, signal in enumerate(selected_signals):
                data_dict[signal.name] = []
                for i, j in zip(start_indexes, end_indexes):
                    # data_dict.update({signal.name: signal.samples[i:j]})
                    try:
                        data_dict[signal.name] += signal.interp(timestamps[i:j]).samples.tolist()
                        if idx == 0:
                            data_dict["timestamps"] += timestamps[i:j].tolist()
                    except:
                        print("error")
            print(data_dict)
            # 写入csv
            self.write_csv(data_dict)

        elif condition == "range":
            if not (self.lower_range.text().isdigit() and self.upper_range.text().isdigit()):
                QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                return
            lower_range = float(self.lower_range.text())
            upper_range = float(self.upper_range.text())
            print("___________")
            condition_channels.append(self.add_condition_combox.currentText())
            signal_samples = self.mdf_file.select(condition_channels)[0].samples
            timestamps = self.mdf_file.select(condition_channels)[0].timestamps
            print("-------------")
            start_flag = 0
            start_indexes = []
            end_indexes = []

            for i, signal_sample in enumerate(signal_samples):
                if upper_range > signal_sample > lower_range and start_flag == 0:
                    start_indexes.append(i)
                    start_flag = 1
                if (signal_sample > upper_range or signal_sample < lower_range) and start_flag == 1:
                    start_flag = 0
                    end_indexes.append(i)
                if upper_range > signal_sample > lower_range and start_flag == 1 and i == len(signal_samples) - 1:
                    end_indexes.append(i+1)
            count = self.selected_signals.count()
            items = []
            data_dict = {"timestamps": []}
            for i in range(count):
                items.append(self.selected_signals.item(i).text())
            selected_signals = self.mdf_file.select(items)

            for idx, signal in enumerate(selected_signals):
                data_dict[signal.name] = []
                for i, j in zip(start_indexes, end_indexes):
                    # data_dict.update({signal.name: signal.samples[i:j]})
                    try:
                        data_dict[signal.name] += signal.interp(timestamps[i:j]).samples.tolist()
                        if idx == 0:
                            data_dict["timestamps"] += timestamps[i:j].tolist()
                    except:
                        print("error")
            print(data_dict)
            self.write_csv(data_dict)

        elif condition == ">":
            if not self.lower_range.text().isdigit():
                QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                return
            lower_range = float(self.lower_range.text())
            condition_channels.append(self.add_condition_combox.currentText())
            signal_samples = self.mdf_file.select(condition_channels)[0].samples
            timestamps = self.mdf_file.select(condition_channels)[0].timestamps
            print("-------------")
            start_flag = 0
            start_indexes = []
            end_indexes = []

            for i, signal_sample in enumerate(signal_samples):
                if signal_sample > lower_range and start_flag == 0:
                    start_indexes.append(i)
                    start_flag = 1
                if signal_sample < lower_range and start_flag == 1:
                    start_flag = 0
                    end_indexes.append(i)
                if signal_sample > lower_range and start_flag == 1 and i == len(signal_samples) - 1:
                    end_indexes.append(i+1)
            count = self.selected_signals.count()
            items = []
            data_dict = {"timestamps": []}
            for i in range(count):
                items.append(self.selected_signals.item(i).text())
            selected_signals = self.mdf_file.select(items)

            for idx, signal in enumerate(selected_signals):
                data_dict[signal.name] = []
                # signal[i].interp(time).samples
                for i, j in zip(start_indexes, end_indexes):
                    try:
                        data_dict[signal.name] += signal.interp(timestamps[i:j]).samples.tolist()
                        if idx == 0:
                            data_dict["timestamps"] += timestamps[i:j].tolist()
                    except:
                        print("error")
            print(data_dict)
            self.write_csv(data_dict)

        elif condition == "=":
            if not self.lower_range.text().isdigit():
                QtWidgets.QMessageBox.about(self, "Message", "范围必须是数字")
                return
            lower_range = float(self.lower_range.text())
            condition_channels.append(self.add_condition_combox.currentText())
            signal_samples = self.mdf_file.select(condition_channels)[0].samples
            timestamps = self.mdf_file.select(condition_channels)[0].timestamps
            print("-------------")
            start_flag = 0
            start_indexes = []
            for i, signal_sample in enumerate(signal_samples):
                if signal_sample == lower_range and start_flag == 0:
                    start_indexes.append(i)
                    start_flag = 1
                if signal_sample != lower_range and start_flag == 1:
                    start_flag = 0
            count = self.selected_signals.count()
            items = []
            data_dict = {"timestamps": []}
            for i in range(count):
                items.append(self.selected_signals.item(i).text())
            selected_signals = self.mdf_file.select(items)

            for idx, signal in enumerate(selected_signals):
                data_dict[signal.name] = []
                for i in start_indexes:
                    # data_dict.update({signal.name: signal.samples[i:j]})
                    try:
                        print(signal.interp([timestamps[i]]).samples)
                        data_dict[signal.name].append(signal.interp(timestamps[i]).samples)
                        if idx == 0:
                            data_dict["timestamps"].append(timestamps[i])
                    except:
                        print("error")
            print(data_dict)
            self.write_csv(data_dict)
        else:
            pass

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

