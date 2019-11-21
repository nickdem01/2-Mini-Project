import sys
from bsddb3 import db
import re

def main():

    create_files()

    return



def create_files():
    fp = open("test1.xml", "r")

    dates_file = open("dates.txt", "w")
    dates_file.close()

    recs_file = open("recs.txt", "w")
    recs_file.close()

    for line in fp:
        line_list = re.split("[<>]+", line)
        for i in range(len(line_list)):
            if (line_list[i] == "row" and line_list[i + 2] == "/row"):
                row_num = line_list[i + 1]
            if (line_list[i] == "date" and line_list[i + 2] == "/date"):
                write_dates(line_list[i + 1],row_num, dates_file)
        
        if (line_list[1] == "mail"):
            write_recs(line, row_num, recs_file)

    fp.close()
    
    return

def write_dates(date, row_num, dates_file):

    dates_file = open("dates.txt", "a")
    dates_file.write(date + ":" + row_num + "\n")

    dates_file.close()
    return

def write_recs(line, row_num, recs_file):

    recs_file = open("recs.txt", "a")
    recs_file.write(row_num + ":" + line + "\n")

    recs_file.close()



    return


if __name__ == "__main__":
    main()
