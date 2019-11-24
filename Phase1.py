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

    emails_file = open("emails.txt", "w")
    emails_file.close()

    terms_file = open("terms.txt", "w")
    terms_file.close()
    
    
    for line in fp:
        line_list = re.split("[<>]+", line)
        for i in range(len(line_list)):
            if (line_list[i] == "row" and line_list[i + 2] == "/row"):
                row_num = line_list[i + 1]
            if (line_list[i] == "date" and line_list[i + 2] == "/date"):
                write_dates(line_list[i + 1],row_num, dates_file)
            
            if ((line_list[i] == "from" and line_list[i + 2] == "/from") or (line_list[i] == "to" and line_list[i + 2] == "/to") or (line_list[i] == "cc" and line_list[i + 2] == "/cc") or (line_list[i] == "bcc" and line_list[i + 2] == "/bcc")  ):
                write_emails(line_list[i + 1],row_num, emails_file, line_list[i])

            if ((line_list[i] == "body" and line_list[i + 2] == "/body") or (line_list[i] == "subj"  and line_list[i + 2] == "/subj")):
                write_terms(line_list[i + 1],row_num, terms_file, line_list[i])        
        
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

def write_emails(email, row_num, emails_file, context):

    emails_file = open("emails.txt", "a")
    emails_file.write(context + "-" + email.lower() + ":" + row_num + "\n")

    emails_file.close()

def write_terms(text, row_num, terms_file, context):

    terms_file = open("terms.txt", "a")
    
    body = re.split('[\s|; |, |: |( |) |\ |/ |? |! |\" |\' |{ |} |\[ |\] |* |\.]', text)

    for i in range(len(body)):
  
        term = body[i].lower()
        if(len(body[i]) > 2 and body[i][0] != '&'):
            
            if(body[i].isalnum() == False):
                 
                temp = body[i].split("&")
                body[i] = temp[0]	
                valid = 0
                for b in range(len(body[i])):

                    if((body[i][b] != '-' or body[i][b] != '_') and len(body[i]) <= 2):
       
                        valid = 1
                        
                if(valid == 0):
                   term = body[i].lower()                
                   terms_file.write(context[0] + '-' + term + ':' + row_num +  "\n")
            else:
                terms_file.write(context[0] + '-' + term + ':' + row_num  + "\n")
    

    terms_file.close()


if __name__ == "__main__":
    main()
