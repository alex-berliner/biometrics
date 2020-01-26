from datetime import *
from dateutil.relativedelta import relativedelta
from headache_table import *
import copy
import csv

sys.path.insert(0, "../utils")
from time_util import *

def get_month_pct(start_time, end_time):
    global conn
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
        wellnesses = list(conn.execute("select * from HEADACHE where TIME>=%s and TIME<=%s"%(day_start_str, day_end_str)))
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
            wellness_day_sum += wellness_adj_pct
        if under_80:
            days_under_80 += 1
        work_str+="=%2.2f"%(wellness_day_sum)
        wellness_month += [wellness_day_sum]
    if len(wellness_month) is 0:
        return 0
    return sum(wellness_month)/len(wellness_month)

def add_headache_entries(conn, headache_csv_handle):
    headache_table = HeadacheTable()
    headache_table.drop_table(conn)
    headache_table.create_table(conn)

    # get all lines but first one, which is a header
    csv_reader = list(csv.reader(headache_csv_handle, delimiter=','))[1:]

    for i in range(len(csv_reader)):
        row = csv_reader[i]
        print(row)
        entry = (i,) + (int(row[0]),) + (float(row[1]),)
        headache_table.add_entry(conn, entry)

def main():
    global conn
    conn = sqlite3.connect('mydb.db')

    # parse csv entries
    headache_csv = open("data/headache.csv", "r")

    add_headache_entries(conn, headache_csv)

    headache_table_entries = list(conn.execute("""SELECT time FROM headache ORDER BY time ASC"""))

    first_entry_time = int(headache_table_entries[0][0])
    last_entry_time  = int(headache_table_entries[-1][0])

    first_month_epoch_floor = epoch_month_floor(first_entry_time)
    last_month_epoch_ceil = epoch_month_floor(last_entry_time)
    month_delta = datetime_month_delta(first_month_epoch_floor, last_month_epoch_ceil)
    start_time = datetime.fromtimestamp(first_month_epoch_floor)
    for i in range(1,month_delta+1):
        month_start_time = start_time + relativedelta(months=i)
        month_end_time = month_start_time + relativedelta(months=1)
        print("%s to %s" % (month_start_time,month_end_time))
        print("%2.2f"%(get_month_pct(month_start_time, month_end_time)))
        print("")

    conn.close()

if __name__ == "__main__":
    main()
