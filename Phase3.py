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
        # List to add our row ids to.
        id_list = []

        for i in range(len(query_list)):

            if query_list[i] in operators:
                
                if (query_list[i - 1].lower() == "to" or query_list[i -1].lower() == "from" or query_list[i -1].lower() == "bcc" or query_list[i -1].lower() == "cc"):
                    terms_list = query_search_terms(query_list[i - 1], query_list[i + 1])
                    if len(id_list) == 0:
                        id_list = id_list + terms_list 
                    else:
                        id_list = list(set(id_list).intersection(terms_list))
                        
                if (query_list[i - 1].lower() == "subj" or query_list[i -1].lower() == "body"):
                    terms_list = query_search_terms(query_list[i - 1], query_list[i + 1])
                    if len(id_list) == 0:
                        id_list = id_list + terms_list # if list is empty we add our first values to it
                    else:
                        id_list = list(set(id_list).intersection(terms_list)) # We use intersect on the lists to get the shared row ids

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
                
        # Print out info from recs based on gathered row ids
        query_search_recs(output, id_list)


    sys.exit()

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
            term = "d-" + term.lower()

        iter = cur.first()
        while(iter):
            column = iter
            if column[0].decode("utf-8") == term:
                terms_list.append(column[1].decode("utf-8"))
            
                dup = cur.next_dup()
                while(dup!=None):
                    terms_list.append(column[1].decode("utf-8"))
                    dup = cur.next_dup()

            iter = cur.next()

    elif term[-1:] == "%":
        if type.lower() == "subj":
            term = "s-" + term[:-1].lower()
        elif type.lower() == "body":
            term = "d-" + term[:-1].lower()

        iter = cur.first()
        while(iter):
            column = iter
            if term.startswith(column[0].decode("utf-8")):
                terms_list.append(column[1].decode("utf-8"))
            
                dup = cur.next_dup()
                while(dup!=None):
                    terms_list.append(column[1].decode("utf-8"))
                    dup = cur.next_dup()

            iter = cur.next()
    
    
    database.close()
    return terms_list

# Takes output_type brief or full and the list of ids to search for in recs and print to output
def query_search_recs(output_type, id_list):
    DB_FILE = "re.idx"
    database = db.DB()
    database.open(DB_FILE, None, db.DB_BTREE, db.DB_RDONLY)
    cur = database.cursor()

    if output_type == "brief":
        for id in id_list:
            result = cur.set(id.encode("utf-8"))
            info = result[1].decode("utf-8")
            info = re.split("[<>]+", info)
            for i in range(len(info)):
                if info[i - 1] == "subj" and info[i + 1] == "/subj":
                    print("Row id: ", id, "Subject: ", info[i])

    elif output_type == "full":
        for id in id_list:
            date = ""
            subject = ""
            from_email = ""
            to_email = ""
            body = ""
            cc = ""
            bcc =""

            result = cur.set(id.encode("utf-8"))
            info = result[1].decode("utf-8")
            info = re.split("[<>]+", info)
            for i in range(len(info)):
                if info[i - 1] == "subj" and info[i + 1] == "/subj":
                    subject = info[i]
                elif info[i - 1] == "date" and info[i + 1] == "/date":
                    date = info[i]
                elif info[i - 1] == "from" and info[i + 1] == "/from":
                    from_email = info[i]
                elif info[i - 1] == "to" and info[i + 1] == "/to":
                    to_email = info[i]
                elif info[i - 1] == "body" and info[i + 1] == "/body":
                    body = info[i]
                elif info[i - 1] == "cc" and info[i + 1] == "/cc":
                    cc = info[i]
                elif info[i - 1] == "bcc" and info[i + 1] == "/bcc":
                    bcc = info[i]
            print("Row id: ", id, "Date: ", date, "From: ", from_email, "To: ", to_email, "Subject: ", subject, "Body: ", body, "cc: ", cc, "bcc: ", bcc)


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
            
    iter = cur.first()
    while(iter):
        column = iter
        if column[0].decode("utf-8") == email:
            emails_list.append(column[1].decode("utf-8"))
            
            dup = cur.next_dup()
            while(dup!=None):
                emails_list.append(column[1].decode("utf-8"))
                dup = cur.next_dup()

        iter = cur.next()
    
    database.close()
    return emails_list

if __name__ == "__main__":
    main()
