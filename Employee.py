import pandas as pd
from datetime import datetime, timedelta


class Employee:
    # 员工类，代表每一位员工
    def __init__(self, employee_id, name=""):
        self.employee_id = employee_id  # 因为此表没有员工id作为唯一表示，所以使用行号作为id
        self.name = name
        self.rest_day = []  # 记录休息日期
        self.attendance_record = {}  # 记录出勤记录,格式为{date:[record1,record2...],...} 注意次日4点前打卡属于前一天

    def get_attendance_record(self, date=None):
        # date参数用于返回特定日期的记录,默认返回全部记录
        if date is None:
            return self.attendance_record
        else:
            if date not in self.attendance_record.keys():
                return "无记录"
            else:
                return self.attendance_record[date]

    def update_attendance_record(self, date, attendance_record):
        # date参数接收日期格式的日期,attendance_record接收打卡记录列表
        self.attendance_record[date] = attendance_record

    def create_attendance_record(self, attendance_records):
        # attendance_records是一个格式为[datetime1,datetime2...]的打卡记录列表
        formatted_records = {}

        for record in attendance_records:
            # 获取日期字符串，注意次日4点前打卡算作前一天
            date_str = str((record - timedelta(hours=4)).date())

            # 将记录添加到对应日期的列表中
            formatted_records.setdefault(date_str, []).append(record)

        self.attendance_record.update(formatted_records)


def process_date(theDay):
    # 检查是否为日期类型
    if not isinstance(theDay, datetime):
        try:
            # 尝试将字符串转换为日期类型
            theDay = datetime.strptime(theDay, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please provide a valid date.")
            return None

    # 在这里进行其他处理或返回日期对象
    return theDay


def workday_regulate(theDay, attendance_records, rest_days):
    # theDay是当天日期,  attendance_records是格式为[record1,record2...]的列表

    theDay = process_date(theDay)

    if theDay in rest_days:
        return {'day_type': '休息', 'total_penalty': 0, 'morningRecord': "", 'afternoonRecord': "", 'nightRecord': ""}

    elif attendance_records == "无记录":
        return {'day_type': '无记录', 'total_penalty': 0, 'morningRecord': "", 'afternoonRecord': "", 'nightRecord': ""}

    total_penalty = 0  # 初始扣款
    late_penalty_rate = 1  # 迟到超过20分钟的惩罚率，一分钟一块钱
    penalty_threshold = timedelta(minutes=20)  # 迟到超过20分钟算没打卡的阈值

    # 定义规定的打卡时间
    morning_deadline = datetime(theDay.year, theDay.month, theDay.day, 7, 0)

    afternoon_start = datetime(theDay.year, theDay.month, theDay.day, 13, 0)
    afternoon_deadline = datetime(theDay.year, theDay.month, theDay.day, 16, 0)

    night_start = datetime(theDay.year, theDay.month, theDay.day, 20, 0)

    morningRecord = ""  # 上午考勤状态
    afternoonRecord = ""  # 下午考勤状态
    nightRecord = ""  # 晚上考勤状态

    for record_time in attendance_records:

        if morningRecord == "":
            if record_time <= morning_deadline:
                morningRecord = "出勤"

            elif morning_deadline < record_time <= morning_deadline + penalty_threshold:
                morningRecord = '迟到'

                # 迟到判断
                lateness = record_time - morning_deadline
                # 计算迟到未超过20分钟的罚款
                minutes_late = lateness.total_seconds() // 60
                total_penalty += minutes_late * late_penalty_rate

        if afternoonRecord == "":
            if afternoon_start <= record_time < afternoon_deadline:
                afternoonRecord = "出勤"

            elif afternoon_deadline < record_time <= afternoon_deadline + penalty_threshold:
                afternoonRecord = '迟到'

                # 迟到判断
                lateness = record_time - afternoon_deadline
                # 计算迟到未超过20分钟的罚款
                minutes_late = lateness.total_seconds() // 60
                total_penalty += minutes_late * late_penalty_rate

        if nightRecord == "":
            if record_time >= night_start:
                nightRecord = "出勤"

    if morningRecord == "":
        morningRecord = "未打卡"

    if afternoonRecord == "":
        afternoonRecord = "未打卡"

    if nightRecord == "":
        nightRecord = "未打卡"

    # 返回总罚款
    return {'day_type': '工作日', 'total_penalty': total_penalty, 'morningRecord': morningRecord,
            'afternoonRecord': afternoonRecord,
            'nightRecord': nightRecord}


def weekend_regulate(theDay, attendance_records, rest_days):
    # theDay是当天日期,  attendance_records是格式为[record1,record2...]的列表

    theDay = process_date(theDay)

    if theDay in rest_days:
        return {'day_type': '休息', 'total_penalty': 0, 'morningRecord': "", 'afternoonRecord': "", 'nightRecord': ""}

    elif attendance_records == "无记录":
        return {'day_type': '无记录', 'total_penalty': 0, 'morningRecord': "", 'afternoonRecord': "", 'nightRecord': ""}

    total_penalty = 0  # 初始扣款
    late_penalty_rate = 1  # 迟到超过20分钟的惩罚率，一分钟一块钱
    penalty_threshold = timedelta(minutes=20)  # 迟到超过20分钟算没打卡的阈值

    # 定义规定的打卡时间
    morning_deadline = datetime(theDay.year, theDay.month, theDay.day, 7, 0)
    night_start = datetime(theDay.year, theDay.month, theDay.day, 20, 0)

    morningRecord = ""  # 上午考勤状态
    nightRecord = ""  # 晚上考勤状态

    for record_time in attendance_records:

        if morningRecord == "":
            if record_time <= morning_deadline:
                morningRecord = "出勤"

            elif morning_deadline < record_time <= morning_deadline + penalty_threshold:
                morningRecord = '迟到'

                # 迟到判断
                lateness = record_time - morning_deadline
                # 计算迟到未超过20分钟的罚款
                minutes_late = lateness.total_seconds() // 60
                total_penalty += minutes_late * late_penalty_rate


        if nightRecord == "":
            if record_time >= night_start:
                nightRecord = "出勤"

    if morningRecord == "":
        morningRecord = "未打卡"

    if nightRecord == "":
        nightRecord = "未打卡"

    # 返回总罚款
    return {'day_type': '周末', 'total_penalty': total_penalty, 'morningRecord': morningRecord,
            'afternoonRecord': "",
            'nightRecord': nightRecord}


