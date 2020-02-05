from datetime import *
from dateutil.relativedelta import relativedelta
from headache_table import *
from medicine_table import *
import copy
import statistics
import csv

sys.path.insert(0, "../utils")
from time_util import *

# manages the key value pairs that most data is stored in in the sql database
class StdField():
    def __init__(self, val_tuple):
        self.time = val_tuple[1]
        self.val = val_tuple[2]

def medicine_add_entries(conn, medicine_csv_handle):
    medicine_table = MedicineTable()
    medicine_table.drop_table(conn)
    medicine_table.create_table(conn)

    # get all lines but first one, which is a header
    csv_reader = list(csv.reader(medicine_csv_handle, delimiter=','))[1:]

    for i in range(len(csv_reader)):
        row = csv_reader[i]
        entry = (i,) + (int(row[0]),) + (row[1],)
        medicine_table.add_entry(conn, entry)

def medicine_get_data(conn, start_time, end_time):
    meds = list(conn.execute("select * from medicine where TIME>=%d and TIME<=%d"%(start_time.timestamp(), end_time.timestamp())))
    med_dict = {}
    if len(meds) > 0:
        for med in meds:
            name = med[2]
            if name not in med_dict:
                med_dict[name] = 0
            med_dict[name] += 1
    return med_dict

# calculate average of percentages in period
def headache_get_period_pct(conn, start:timedelta, stop:timedelta):
    # always calculate period percent based on daily percents
    day_delta = relativedelta(days=1)

    # the number of day entries in the given period
    wellness_days_in_period = []
    elapsed_runner = start
    days_recd = 0
    while elapsed_runner < stop and elapsed_runner < datetime.now():
        elapsed_end = elapsed_runner + day_delta
        start_str = str(int(start.timestamp()))
        end_str = str(int(elapsed_end.timestamp()))
        wellnesses = list(conn.execute("select * from HEADACHE where TIME>=%s and TIME<=%s"%(start_str, end_str)))
        if len(wellnesses) > 0:
            # get the time of the day's first entry
            first_entry_time = datetime.fromtimestamp(wellnesses[0][1])
            # start percent calculation from time of first entry for that day
            day_record_duration = elapsed_end - first_entry_time

            # record the number of days with valid entries
            wellness_day_sum = 0
            for i in range(len(wellnesses)):
                cur_entry = StdField(wellnesses[i])
                duration =  elapsed_end if (i == len(wellnesses)-1) else \
                            datetime.fromtimestamp(StdField(wellnesses[i+1]).time)
                duration -= datetime.fromtimestamp(cur_entry.time)

                wellness_adj_pct = duration / day_record_duration * float(cur_entry.val)
                wellness_day_sum += wellness_adj_pct
            wellness_days_in_period += [wellness_day_sum]
            days_recd += 1

        elapsed_runner += day_delta

    if len(wellness_days_in_period) < 1:
        return None

    return statistics.mean(wellness_days_in_period)

def headache_std_dev_calc(conn, start, stop):
    # always calculate period percent based on daily percents
    day_delta = relativedelta(days=1)
    elapsed_runner = start
    pcts = []
    while elapsed_runner < stop and elapsed_runner < datetime.now():
        elapsed_end = elapsed_runner + day_delta
        period_pct = headache_get_period_pct(conn, elapsed_runner, elapsed_end)
        if period_pct:
            pcts += [period_pct]
        elapsed_runner += day_delta

    return statistics.mean(pcts), statistics.stdev(pcts)

def headache_add_entries(conn, headache_csv_handle):
    headache_table = HeadacheTable()
    headache_table.drop_table(conn)
    headache_table.create_table(conn)

    # get all lines but first one, which is a header
    csv_reader = list(csv.reader(headache_csv_handle, delimiter=','))[1:]

    for i in range(len(csv_reader)):
        row = csv_reader[i]
        entry = (i,) + (int(row[0]),) + (float(row[1]),)
        headache_table.add_entry(conn, entry)

def all_get_stats(conn, start, stop, period):
    elapsed_runner = start
    elapsed_arr = []
    while elapsed_runner < min(datetime.now(), stop):
        elapsed_arr += [elapsed_runner]
        elapsed_runner += period

    retstr = ""
    for elapsed in reversed(elapsed_arr):
        elapsed_end = elapsed + period
        mean, stdev = headache_std_dev_calc(conn, elapsed, elapsed_end)
        med_data = medicine_get_data(conn, elapsed, elapsed_end)
        retstr += "%s --- %s"%(str(epoch_to_yyyy_mm_dd(elapsed.timestamp())), str(epoch_to_yyyy_mm_dd(elapsed_end.timestamp()))) + "\n"
        retstr += "mean: %2.2f; stdev: %2.2f"%(mean, stdev) + "\n"
        retstr += "med data: %s"%(str(med_data)) + "\n"
        retstr += "\n"

    return retstr

def main():
    conn = sqlite3.connect('mydb.db')

    # parse headache csv entries
    headache_csv = open("data/headache.csv", "r")
    headache_add_entries(conn, headache_csv)

    # parse medicine csv entries
    medicine_csv_handle = open("data/medicine.csv", "r")
    medicine_add_entries(conn, medicine_csv_handle)

    headache_table_entries = list(conn.execute("""SELECT time FROM headache ORDER BY time ASC"""))

    # time of first entry
    first_entry_time = int(headache_table_entries[0][0])

    # time of last entry
    last_entry_time  = datetime.now().timestamp()

    start_time = datetime.fromtimestamp(epoch_month_floor(first_entry_time))
    end_time   = datetime.fromtimestamp(epoch_month_ceil(last_entry_time))

    print(all_get_stats(conn, start_time, end_time, relativedelta(months=1)).strip())
    conn.close()

if __name__ == "__main__":
    main()
