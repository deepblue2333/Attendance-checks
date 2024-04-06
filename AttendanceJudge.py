# -*- coding: utf-8 -*-
import sys
from datetime import datetime

import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QPushButton
from PyQt5.QtGui import QIcon
from ui_loader import load_ui_file

import Employee


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()

        # 使用 ui_loader 模块加载 Qt Designer 创建的 UI 文件
        self.ui = load_ui_file()
        self.ui.setupUi(self)

        # 设置应用程序图标
        self.setWindowIcon(QIcon("resources/images/icon.png"))  # 替换为你的图标文件路径

        # 连接按钮点击事件到文件选择逻辑
        self.ui.pushButton.clicked.connect(self.show_file_dialog)

        # 连接LineEdit的textChanged信号到处理函数
        self.ui.lineEdit.textChanged.connect(self.update_file_path)

        # 连接按钮点击事件到文件选择逻辑
        self.ui.pushButton_2.clicked.connect(self.attendtanceJudge)

    def show_message_box(self):
        # 模拟程序执行完成后弹出消息框
        QMessageBox.information(self, "任务完成", "程序执行完成！", QMessageBox.Ok)

    def show_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        # 显示文件对话框
        self.ui.file_path, _ = QFileDialog.getOpenFileName(None, "选择文件", "", "All Files (*)", options=options)

        if self.ui.file_path:
            # 在LineEdit中显示所选文件的路径
            self.ui.lineEdit.setText(self.ui.file_path)

    def update_file_path(self):
        self.ui.file_path = self.ui.lineEdit.text()

    def attendtanceJudge(self):
        input_df = pd.read_excel(self.ui.file_path)
        # print(input_df)

        employees = {}

        for record in input_df.iterrows():
            row_index = record[0]
            records = []  # 存储打卡记录
            for index, value in record[1].items():
                if index == "姓名":
                    employees[row_index] = Employee.Employee(row_index, value)

                elif value == '休':
                    datestr = str(datetime.now().year) + index
                    index = datetime.strptime(datestr, "%Y%m月%d日")
                    employees[row_index].rest_day.append(index)
                    continue

                else:
                    if type(value) != "str":
                        value = str(value)

                    if value == 'nan':
                        continue

                    for time_record in value.strip('\n').strip(' ').split("\n"):
                        datestr = str(datetime.now().year) + index + time_record
                        date = datetime.strptime(datestr, "%Y%m月%d日%H:%M")
                        records.append(date)

            employees[row_index].create_attendance_record(records)

        result_list = []

        for employee in employees.values():

            for date in list(input_df.columns)[1:]:

                result = {}

                datestr = str(datetime.now().year) + date
                date = datetime.strptime(datestr, "%Y%m月%d日")

                if date.weekday() >= 5:
                    # str(date.date())

                    attendance_situation = Employee.weekend_regulate(str(date.date()),
                                                                     employee.get_attendance_record(str(date.date())),
                                                                     employee.rest_day)
                else:
                    attendance_situation = Employee.workday_regulate(str(date.date()),
                                                                     employee.get_attendance_record(str(date.date())),
                                                                     employee.rest_day)

                result["姓名"] = employee.name
                result["日期"] = date.date()

                result["日期类型"] = attendance_situation['day_type']
                result["上午考勤"] = attendance_situation['morningRecord']
                result["下午考勤"] = attendance_situation['afternoonRecord']
                result["晚上考勤"] = attendance_situation['nightRecord']
                result["迟到扣款"] = attendance_situation['total_penalty']

                result_list.append(result)

        result_df = pd.DataFrame(result_list)
        print(result_df)

        result_df.to_excel('打卡情况.xlsx', index=False)

        self.show_message_box()


def main():
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    app.exec()


if __name__ == "__main__":
    main()
