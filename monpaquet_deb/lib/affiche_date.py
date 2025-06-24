#!/usr/bin/env python3
import datetime
import zoneinfo

def main():
    now_local = datetime.datetime.now()
    now_gmt = datetime.datetime.now(datetime.timezone.utc)
    tz_tuvalu = zoneinfo.ZoneInfo("Pacific/Funafuti")
    now_tuvalu = datetime.datetime.now(tz=tz_tuvalu)

    print("Fuseau local :", now_local.strftime("%Y-%m-%d %H:%M:%S"))
    print("GMT :", now_gmt.strftime("%Y-%m-%d %H:%M:%S"))
    print("Tuvalu :", now_tuvalu.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()