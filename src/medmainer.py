from dateutil.relativedelta import relativedelta
import copy
import csv
from medicine_table import *
sys.path.insert(0, "../utils")
from time_util import *
from datetime import *
mydb = sqlite3.connect('mydb.db')
# daylio_parser.parse_daylio(mydb, biometrics_context)
headache_table = MedicineTable()
headache_table.create_table(mydb)
# parse csv entries
headache_csv = open("data/medicine.csv", "r")
csv_reader = list(csv.reader(headache_csv, delimiter=','))[1:]
for i in range(len(csv_reader)):
    row = csv_reader[i]
    entry = (i,) + (int(row[0]),) + (row[1],)
    headache_table.add_entry(mydb, entry)
def get_month_pct(monthnum):
    start_time = datetime(year=2019,month=monthnum,day=1)
    start_time_str = str(int(start_time.timestamp()))
    end_time = start_time+relativedelta(months=1)
    # print(len(wellnesses))
    # for entry in wellnesses:
    #     print(entry[2], epoch_to_ymd_hms(entry[1]))
    day_count = (end_time-start_time).days
    # print(day_count)
    wellness_month = []
    med_count = {}
    for day in range(day_count):
        # daystart = copy.deepcopy(start_time)
        # print(daystart)
        day_start = (start_time+timedelta(days=day)).replace(hour=8, minute=0,second=0)
        day_end = start_time+timedelta(days=day+1)
        day_start_str = str(int(day_start.timestamp()))
        day_end_str = str(int(day_end.timestamp()))
        # print(epoch_to_ymd_hms(day_end.timestamp()))
        wellnesses = list(mydb.execute("select * from MEDICINE where TIME>=%s and TIME<=%s"%(day_start_str, day_end_str)))
        for entry in wellnesses:
            # print(entry[2])
            if entry[2] not in med_count:
                med_count[entry[2]] = 0
            med_count[entry[2]] += 1
        # print(start_time+timedelta(days=day))
    #     if len(wellnesses) is 0:
    #         # print("no entries for this day")
    #         continue
    #     # print(len(wellnesses))
    #     first_entry_time = datetime.fromtimestamp(wellnesses[0][1])
    #     day_record_duration = day_end - first_entry_time
    #     # print(day_record_duration)
    #     wellness_day_sum = 0
    #     for i in range(len(wellnesses)):
    #         entry = wellnesses[i]
    #         # print(entry)
    #         wellness_pct = float(entry[2])
    #         # print("asd", datetime.fromtimestamp(entry[1]))
    #         duration = 0
    #         # print(epoch_to_ymd_hms(wellnesses[i][1]))
    #         if i == len(wellnesses)-1:
    #             duration = day_end-datetime.fromtimestamp(wellnesses[i][1])
    #         else:
    #             duration = datetime.fromtimestamp(wellnesses[i+1][1])-\
    #                     datetime.fromtimestamp(wellnesses[i][1])
    #         wellness_pct = duration/day_record_duration*wellness_pct
    #         # print("%s/%s*%s="%(duration,day_record_duration,wellness_pct))
    #         # print(wellness_pct)
    #         wellness_day_sum += wellness_pct
    #     wellness_month += [wellness_day_sum]
    #     # print(epoch_to_ymd_hms(day_start.timestamp()), wellness_day_sum)
    #         # print("")
    #     # print("sum %s"%(wellness_day_sum))
    # # print(wellness_month)
    return med_count
for i in range(0,11):
    v = i+1
    print(v)
    print(get_month_pct(v))
    print("")
mydb.close()
