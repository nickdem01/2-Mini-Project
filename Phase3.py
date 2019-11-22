import sys
from bsddb3 import db
import re


def main():

    exit_command = False
    output = "brief"

    while exit_command != True:
        print("Welcome to Query Selection\nType Exit to quit program\nType output=full for full record or output=brief for id and title only\n")
        command = input("Please enter a query: ")
        if command.lower() == "exit":
            exit_command = True
        elif command.lower() == "output=full":
            output = "full"
        elif command.lower() == "output=brief":
            output = "breif"

        command = re.sub(r"(\w)([:<>]|>=|<=)(\w)", r"\1 \2 \3", command)
        command = re.sub(r"(\w)([:<>]|>=|<=)(\s)", r"\1 \2 \3", command)
        command = re.sub(r"(\s)([:<>]|>=|<=)(\w)", r"\1 \2 \3", command)

        query_list = command.split(" ")
        query_list = list(filter(str.strip, query_list))
        
        operators = [":", "<", ">", "<=", ">="]

        for i in range(len(query_list)):

            if query_list[i] in operators:
                if query_list[i - 1] == "subj":
                    query_search_subj(output, query_list[i + 1])
                elif query_list[i -1] == "body":
                    #qurey_search_body()
                    break

            elif query_list[i] not in operators:
                if (i != 0 and i != len(query_list) - 1):
                    if (query_list[i - 1] not in operators and query_list[i + 1] not in operators):
                        #qurey_search_body() and query_search_subj()
                        break
                elif i == 0 and i != len(query_list) -1:
                    if query_list[i+1] not in operators:
                        break
                elif i != 0 and i == len(query_list) -1:
                    if query_list[i-1] not in operators:
                        break
                else:
                    break


    sys.exit()


def query_search_subj(output, term):
    return




if __name__ == "__main__":
    main()