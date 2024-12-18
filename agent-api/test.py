import datetime
import time

if __name__ == '__main__':
    time2 = 1729154100
    time2 = 1729154100 + 8 * 3600

    start_timestamp = datetime.datetime.utcfromtimestamp(time2 - 30 * 60)
    end_timestamp = datetime.datetime.utcfromtimestamp(time2)

    start_date = start_timestamp.strftime('%Y-%m-%d')
    start_time = start_timestamp.strftime('%H:%M:%S')

    end_date = end_timestamp.strftime('%Y-%m-%d')
    end_time = end_timestamp.strftime('%H:%M:%S')

    print(start_date, start_time)
    print(end_date, end_time)
