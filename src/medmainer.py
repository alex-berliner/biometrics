from dateutil.relativedelta import relativedelta
from medicine_table import *
from datetime import *
import copy
import csv

sys.path.insert(0, "../utils")
from time_util import *

def get_meds_in_period(start_time, end_time):
    global med_conn
    day_count = (end_time-start_time).days
    med_count = {}
    for day in range(day_count):
        day_start = (start_time+timedelta(days=day)).replace(hour=8, minute=0,second=0)
        day_end = start_time+timedelta(days=day+1)
        day_start_str = str(int(day_start.timestamp()))
        day_end_str = str(int(day_end.timestamp()))
        wellnesses = list(med_conn.execute("select * from MEDICINE where TIME>=%s and TIME<=%s"%(day_start_str, day_end_str)))
        for entry in wellnesses:
            if entry[2] not in med_count:
                med_count[entry[2]] = 0
            med_count[entry[2]] += 1
    return med_count

def main():
    global med_conn
    med_conn = sqlite3.connect('mydb.db')

    medicine_table = MedicineTable()
    medicine_table.create_table(med_conn)

    # parse csv entries
    medicine_csv = open("data/medicine.csv", "r")

    # get all lines but first one, which is a header
    csv_reader = list(csv.reader(medicine_csv, delimiter=','))[1:]

    first_entry_time = csv_reader[0][0]
    last_entry_time  = csv_reader[-1][0]
    for i in range(len(csv_reader)):
        row = csv_reader[i]
        entry = (i,) + (int(row[0]),) + (row[1],)
        medicine_table.add_entry(med_conn, entry)

    first_month_floor_epoch = epoch_month_floor(first_entry_time)
    last_month_ceil_epoch = epoch_month_floor(last_entry_time)
    month_delta = datetime_month_delta(first_month_floor_epoch, last_month_ceil_epoch)
    # e1 = datetime.fromtimestamp(e1)
    start_time = datetime.fromtimestamp(first_month_floor_epoch)

    for i in range(1,month_delta+1):
        month_start_time = start_time + relativedelta(months=i)
        month_end_time = month_start_time + relativedelta(months=1)
        print("%s to %s" % (month_start_time,month_end_time))
        print(get_meds_in_period(month_start_time, month_end_time))
        print("")

    med_conn.close()

if __name__ == "__main__":
    main()
