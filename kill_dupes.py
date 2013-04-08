import sys

date_prev = None
for line in sys.stdin:
    date, checksum, url = line.strip().split()
    if date_prev == date:
        continue
    else:
        print checksum
        date_prev = date
