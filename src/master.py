from datetime import *
from dateutil.relativedelta import relativedelta
from headache_table import *
from medicine_table import *
import copy
import csv

sys.path.insert(0, "../utils")
from time_util import *

def get_meds_in_period(start_time, end_time):
    global conn
    day_count = (end_time-start_time).days
    med_count = {}
    for day in range(day_count):
        day_start = (start_time+timedelta(days=day)).replace(hour=8, minute=0,second=0)
        day_end = start_time+timedelta(days=day+1)
        day_start_str = str(int(day_start.timestamp()))
        day_end_str = str(int(day_end.timestamp()))
        wellnesses = list(conn.execute("select * from MEDICINE where TIME>=%s and TIME<=%s"%(day_start_str, day_end_str)))
        for entry in wellnesses:
            if entry[2] not in med_count:
                med_count[entry[2]] = 0
            med_count[entry[2]] += 1
    return med_count

def get_month_pct(conn, start_time, end_time):
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

def add_medicine_entries(conn, medicine_csv_handle):
    medicine_table = MedicineTable()
    medicine_table.drop_table(conn)
    medicine_table.create_table(conn)

    # get all lines but first one, which is a header
    csv_reader = list(csv.reader(medicine_csv_handle, delimiter=','))[1:]

    for i in range(len(csv_reader)):
        row = csv_reader[i]
        entry = (i,) + (int(row[0]),) + (row[1],)
        medicine_table.add_entry(conn, entry)

def add_headache_entries(conn, headache_csv_handle):
    headache_table = HeadacheTable()
    headache_table.drop_table(conn)
    headache_table.create_table(conn)

    # get all lines but first one, which is a header
    csv_reader = list(csv.reader(headache_csv_handle, delimiter=','))[1:]

    for i in range(len(csv_reader)):
        row = csv_reader[i]
        # print(row)
        entry = (i,) + (int(row[0]),) + (float(row[1]),)
        headache_table.add_entry(conn, entry)

def get_med_data(conn, start_time, end_time):
    meds = list(conn.execute("select * from medicine where TIME>=%d and TIME<=%d"%(start_time.timestamp(), end_time.timestamp())))
    med_dict = {}
    if len(meds) > 0:
        for med in meds:
            name = med[2]
            if name not in med_dict:
                med_dict[name] = 0
            med_dict[name] += 1
    return med_dict


def main():
    global conn
    conn = sqlite3.connect('mydb.db')

    # parse csv entries
    headache_csv = open("data/headache.csv", "r")
    add_headache_entries(conn, headache_csv)

    # parse csv entries
    medicine_csv_handle = open("data/medicine.csv", "r")
    add_medicine_entries(conn, medicine_csv_handle)

    headache_table_entries = list(conn.execute("""SELECT time FROM headache ORDER BY time ASC"""))

    first_entry_time = int(headache_table_entries[0][0])
    last_entry_time  = datetime.now().timestamp()

    first_month_epoch_floor = epoch_month_floor(first_entry_time)
    last_month_epoch_ceil = epoch_month_floor(last_entry_time)
    month_delta = datetime_month_delta(first_month_epoch_floor, last_month_epoch_ceil)

    start_time = datetime.fromtimestamp(first_month_epoch_floor)

    for i in range(1,month_delta+1):
        month_start_time = start_time + relativedelta(months=i)
        month_end_time = month_start_time + relativedelta(months=1)
        print("%2.2f | "%(get_month_pct(conn, month_start_time, month_end_time)), end=" ")
        print("%s to %s" % (epoch_to_yyyy_mm_dd(month_start_time.timestamp()),epoch_to_yyyy_mm_dd(month_end_time.timestamp())))
        med_data = get_med_data(conn, month_start_time, month_end_time)
        # print(("%02s " + "#" * med_data["maxalt"])%(med_data["maxalt"]))
        print(med_data)
        print("")
    conn.close()

if __name__ == "__main__":
    main()
