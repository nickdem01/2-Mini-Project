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
             sys.exit()
        elif command.lower() == "output=full":
            output = "full"
        elif command.lower() == "output=brief":
            output = "brief"

        command = re.sub(r"(\w)([:<>]|>=|<=)(\w)", r"\1 \2 \3", command)
        command = re.sub(r"(\w)([:<>]|>=|<=)(\s)", r"\1 \2 \3", command)
        command = re.sub(r"(\s)([:<>]|>=|<=)(\w)", r"\1 \2 \3", command)

        query_list = command.split(" ")
        query_list = list(filter(str.strip, query_list))
        
        operators = [":", "<", ">", "<=", ">="]
        # List to add our row ids to.
        id_list = []

        for i in range(len(query_list)):

            if query_list[i] in operators:
                
                if (query_list[i - 1].lower() == "to" or query_list[i -1].lower() == "from" or query_list[i -1].lower() == "bcc" or query_list[i -1].lower() == "cc"):
                    emails_list = query_search_emails(query_list[i - 1], query_list[i + 1])
                    id_list = intersect_lists(id_list, emails_list)
                        
                if (query_list[i - 1].lower() == "date"):
                    dates_list = query_search_dates(query_list[i + 1], query_list[i])
                    id_list = intersect_lists(id_list, dates_list)
                        
                if (query_list[i - 1].lower() == "subj" or query_list[i -1].lower() == "body"):
                    terms_list = query_search_terms(query_list[i - 1], query_list[i + 1])
                    id_list = intersect_lists(id_list, terms_list)

            elif query_list[i] not in operators:
                if (i != 0 and i != len(query_list) - 1):
                    if (query_list[i - 1] not in operators and query_list[i + 1] not in operators):
                        subj_list = query_search_terms("subj", query_list[i])
                        body_list = query_search_terms("body", query_list[i])
                        terms_list = subj_list + body_list
                        id_list = intersect_lists(id_list, terms_list)

                elif i == 0 and i != len(query_list) -1:
                    if query_list[i+1] not in operators:
                        subj_list = query_search_terms("subj", query_list[i])
                        body_list = query_search_terms("body", query_list[i])
                        terms_list = subj_list + body_list
                        id_list = intersect_lists(id_list, terms_list)

                elif i != 0 and i == len(query_list) -1:
                    if query_list[i-1] not in operators:
                        subj_list = query_search_terms("subj", query_list[i])
                        body_list = query_search_terms("body", query_list[i])
                        terms_list = subj_list + body_list
                        id_list = intersect_lists(id_list, terms_list)

                elif i == 0 and i == len(query_list) - 1:
                    subj_list = query_search_terms("subj", query_list[i])
                    body_list = query_search_terms("body", query_list[i])
                    terms_list = subj_list + body_list
                    id_list = intersect_lists(id_list, terms_list)
                
        # Print out info from recs based on gathered row ids
        query_search_recs(output, id_list)


   

# Passes type value of either subj or body and the term key we are searching for.
# Return a list of key row ids that match up with our terms.
def query_search_terms(type, term):
    DB_FILE = "te.idx"
    database = db.DB()
    database.open(DB_FILE, None, db.DB_BTREE, db.DB_RDONLY)
    cur = database.cursor()

    terms_list = []

    if term[-1:] != "%":
        if type.lower() == "subj":
            term = "s-" + term.lower()
        elif type.lower() == "body":
            term = "b-" + term.lower()

        iter = cur.set_range(term.encode("utf-8"))
        while(iter):
            column = iter
            if column[0].decode("utf-8") == term:
                terms_list.append(column[1].decode("utf-8"))
            else:
                break
            
            iter = cur.next()

    elif term[-1:] == "%":
        if type.lower() == "subj":
            term = "s-" + term[:-1].lower()
        elif type.lower() == "body":
            term = "b-" + term[:-1].lower()


        iter = cur.set_range(term.encode("utf-8"))
        while(iter):
            column = iter
            if column[0].decode("utf-8").startswith(term):
                terms_list.append(column[1].decode("utf-8"))
            else: 
                break

            iter = cur.next()
      
    database.close()
    return terms_list


# Takes output_type brief or full and the list of ids to search for in recs and print to output
def query_search_recs(output_type, id_list):
    DB_FILE = "re.idx"
    database = db.DB()
    database.open(DB_FILE, None, db.DB_HASH, db.DB_RDONLY)

    if output_type == "brief":
        subject = ""

        for id in id_list:
            result = database.get(id.encode("utf-8"))
            info = result.decode("utf-8")
            info = re.split("[<>]+", info)
            for i in range(len(info)):
                if info[i - 1] == "subj" and info[i + 1] == "/subj":
                    subject = info[i]

            print("Row id:", id, "Subject:", subject, "\n")
            subject = ""

    elif output_type == "full":
        for id in id_list:
            term_list = ["", "", "", "", "", "", ""]

            result = database.get(id.encode("utf-8"))
            info = result.decode("utf-8")
            info = re.split("[<>]+", info)
            for i in range(len(info)):
                if info[i - 1] == "date" and info[i + 1] == "/date":
                    term_list[0] = info[i]
                elif info[i - 1] == "subj" and info[i + 1] == "/subj":
                    term_list[1] = info[i]
                elif info[i - 1] == "from" and info[i + 1] == "/from":
                    term_list[2] = info[i]
                elif info[i - 1] == "to" and info[i + 1] == "/to":
                    term_list[3] = info[i]
                elif info[i - 1] == "body" and info[i + 1] == "/body":
                    term_list[4] = info[i]
                elif info[i - 1] == "cc" and info[i + 1] == "/cc":
                    term_list[5] = info[i]
                elif info[i - 1] == "bcc" and info[i + 1] == "/bcc":
                    term_list[6] = info[i]

            print("Row id:", id, "Date:", term_list[0], "From:", term_list[2], "To:", term_list[3], 
            "Subject:", term_list[1], "Body:", term_list[4], "cc:", term_list[5], "bcc:", term_list[6], "\n")

            term_list = ["", "", "", "", "", "", ""]

    database.close()
    return

def query_search_emails(type, email):
    
    DB_FILE = "em.idx"
    database = db.DB()
    database.open(DB_FILE, None, db.DB_BTREE, db.DB_RDONLY)
    cur = database.cursor()

    emails_list = []
    
    if type.lower() == "cc":
        email = "cc-" + email.lower()
        
    elif type.lower() == "to":
        email = "to-" + email.lower() 
    
    elif type.lower() == "bcc":
        email = "bcc-" + email.lower() 
    
    elif type.lower() == "from":
        email = "from-" + email.lower()     
            
    iter = cur.set_range(email.encode("utf-8"))
    while(iter):
        column = iter
        if column[0].decode("utf-8") == email:
            emails_list.append(column[1].decode("utf-8"))
        else:
            break
        
        iter = cur.next()
    
    database.close()
    return emails_list


def query_search_dates(date, opr):
        
    DB_FILE = "da.idx"
    database = db.DB()
    database.open(DB_FILE, None, db.DB_BTREE, db.DB_RDONLY)
    cur = database.cursor()
    
    dates_list = []
    
                
    iter = cur.set_range(date.encode("utf-8"))
    while(iter):
        column = iter
        if opr == '>':
            
            if column[0].decode("utf-8") > date:
                dates_list.append(column[1].decode("utf-8"))
            elif column[0].decode("utf-8") != date and column[0].decode("utf-8") < date:
                break

            iter = cur.next()
                
        if opr == '<':
                    
            if column[0].decode("utf-8") < date:
                dates_list.append(column[1].decode("utf-8"))
            elif column[0].decode("utf-8") != date and column[0].decode("utf-8") > date:
                break

            iter = cur.prev()

        if opr == '>=':
                    
            if column[0].decode("utf-8") >= date:
                dates_list.append(column[1].decode("utf-8"))
            else:
                break

            iter = cur.next()         
            
        if opr == '<=':
                    
            if column[0].decode("utf-8") == date:
                dates_list.append(column[1].decode("utf-8"))
                iter = cur.next()
            elif column[0].decode("utf-8") > date:
                iter = cur.set_range(date.encode("utf-8"))
                iter = cur.prev()
            elif column[0].decode("utf-8") < date:
                dates_list.append(column[1].decode("utf-8"))
                iter = cur.prev()           

        if opr == ':':
                    
            if column[0].decode("utf-8") == date:
                dates_list.append(column[1].decode("utf-8"))
            else:
                break

            iter = cur.next()
                
        
    database.close()
    return dates_list

def intersect_lists(current_id_list, compare_id_list):
    if len(current_id_list) == 0:
        id_list = current_id_list + compare_id_list
    else:
        id_list = list(set(current_id_list).intersection(compare_id_list))
    
    return id_list

if __name__ == "__main__":
    main()
