from dateutil.relativedelta import relativedelta
import copy
import csv
from headache_table import *
sys.path.insert(0, "../utils")
from time_util import *
from datetime import *
mydb = sqlite3.connect('mydb.db')
# daylio_parser.parse_daylio(mydb, biometrics_context)
headache_table = HeadacheTable()
headache_table.create_table(mydb)
# parse csv entries
headache_csv = open("data/headache.csv", "r")
csv_reader = list(csv.reader(headache_csv, delimiter=','))[1:]
for i in range(len(csv_reader)):
    row = csv_reader[i]
    entry = (i,) + (int(row[0]),) + (int(float(row[1])),)
    headache_table.add_entry(mydb, entry)
def get_month_pct(start_time, end_time):
    start_time_str = str(int(start_time.timestamp()))
    day_count = (end_time-start_time).days
    day_count_final = day_count
    wellness_month = []
    days_under_80 = 0
    for day in range(day_count):
        day_start = (start_time+timedelta(days=day)).replace(hour=8, minute=0,second=0)
        day_end = start_time+timedelta(days=day+1)
        day_start_str = str(int(day_start.timestamp()))
        day_end_str = str(int(day_end.timestamp()))
        wellnesses = list(mydb.execute("select * from HEADACHE where TIME>=%s and TIME<=%s"%(day_start_str, day_end_str)))
        if len(wellnesses) is 0:
            day_count_final -= 1
            continue
        first_entry_time = datetime.fromtimestamp(wellnesses[0][1])
        day_record_duration = day_end - first_entry_time
        wellness_day_sum = 0
        work_str = ""
        under_80 = False
        for i in range(len(wellnesses)):
            entry = wellnesses[i]
            wellness_pct = float(entry[2])
            if wellness_pct < 80:
                under_80 = True
            duration = 0
            if i == len(wellnesses)-1:
                duration = day_end-datetime.fromtimestamp(wellnesses[i][1])
            else:
                duration = datetime.fromtimestamp(wellnesses[i+1][1])-\
                           datetime.fromtimestamp(wellnesses[i][1])
            wellness_adj_pct = duration/day_record_duration*wellness_pct
            work_str += "%2.2f/%2.2f*%2.2f(=>%2.2f)+ "%(duration.seconds/60/60,day_record_duration.seconds/60/60,wellness_pct, wellness_adj_pct)
            # print(wellness_pct)
            wellness_day_sum += wellness_adj_pct
        if under_80:
            days_under_80 += 1
        work_str+="=%2.2f"%(wellness_day_sum)
        # print(work_str)
        wellness_month += [wellness_day_sum]
    if len(wellness_month) is 0:
        return 0
    print(days_under_80)
    return sum(wellness_month)/len(wellness_month)
# for i in range(0,11):
#     v = i+1
#     start_time = datetime(year=2019,month=v,day=1)
#     end_time = start_time+relativedelta(months=1)
#     print(v, get_month_pct(start_time, end_time))
# for i in range(15,30):
#     start_time = datetime(year=2019,month=11,day=i)
#     end_time = start_time+relativedelta(days=1)
#     # print("day " + str(i))
#     print(get_month_pct(start_time, end_time))
#     print("")
for i in range(1,12):
    start_time = datetime(year=2019,month=i,day=1)
    end_time = start_time+relativedelta(months=1)
    print("month " + str(i))
    print(get_month_pct(start_time, end_time))
    print("")
# start_time = datetime(year=2019,month=11,day=15)
# end_time = start_time+relativedelta(days=12)
# # print("day " + str(i))
# print(get_month_pct(start_time, end_time))
# print("")

mydb.close()
