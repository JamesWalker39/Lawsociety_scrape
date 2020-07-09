#imports URL requester and BS
import requests
from urllib.request import urlopen
from time import sleep
from time import time
import sys
from bs4 import BeautifulSoup as soup

# Funtion to open page and soup parse
def urlreader_to_soup(url):
    webpage = urlopen(url)
    webpagedata = webpage.read()
    webpage.close()
    pagedata_name = soup(webpagedata, "html.parser")
    return pagedata_name
    
#location = sys.argv[1]
location = "bristol"

# Creating CSV for details to be written too 
filename = "Solicitors_Details_"+location+".csv"
f = open(filename , "w")
headers = "Company_Name,Address,Telephone,Num_Offices,Num_Solicitors,Num_Accreditations,COFA\n" 
f.write("Solicitors: " + location + "\n")
f.write(headers)

# get page count
my_url = "https://solicitors.lawsociety.org.uk/search/results?Location="+ location + "&Pro=False&Page=1"
page_data = urlreader_to_soup(my_url)

#find number of results
noResults = page_data.findAll("strong")
count = noResults[0].text
pages = (int(count)//20) + 2
print("total companies pages:" + str(pages)+ "\n")

start_time = time()
request_no = 0

#Loop through pages of companies 
for pagenumber in range (1,pages):
    myurl_2 = "https://solicitors.lawsociety.org.uk/search/results?Location="+ location + "&Pro=False&Page=" + str(pagenumber)
    page_data2 = urlreader_to_soup(myurl_2) # file name and html parse
    
    #define each product,grabs each product
    containers = page_data2.findAll("section",
                                   {"class":"solicitor solicitor-type-firm"})
    print("company page of results:" + str(pagenumber) +"\n")

    # loop through details for each company
    for container in containers: 
        request_no += 1
         #monitor requests
        elapsed_time = time () - start_time
        print('Request:{}; Frequency: {} requests/s \n'.format(request_no, request_no/elapsed_time))
        
        name = container.h2.text
        address = container.find("dd").text
        tel = container.find("dd", attrs = {"class":"hidden-phone"})
        officeno = container.find("p", {"class":"hidden-phone"}).a.text
        solicno = container.find("p", {"class":"hidden-phone"}).span.a.strong.text
        try:
            noAccreds = container.find("div", {"class":"accreditations hidden-phone"}).strong.text
        except:
            noAccreds = "no accreditations given"

        #get + open company webpage
        co_page = "https://solicitors.lawsociety.org.uk"+ container.findAll('a')[0].get('href')
        print("opened: " + co_page + "\n")
        co_page_data = urlreader_to_soup(co_page)
        table_rows = co_page_data.findAll("div", {"class":"panel-third"})
        try:
            SRA_link = "https://solicitors.lawsociety.org.uk"+ table_rows[1].findAll("a")[2].get('href')
        except:
            break
                    
        #open SRA page 
        SRA_page_data = urlreader_to_soup(SRA_link)
        print("opened: " + SRA_link + "\n")
        No_SRA = SRA_page_data.find("h1").strong.text
        SRA_pages = (int(No_SRA)//20) + 2
        COFA = ""
        
        for SRApagenumber in range (1,SRA_pages):
            SRA_page_data_loop = "https://solicitors.lawsociety.org.uk"+ table_rows[1].findAll("a")[2].get('href')+"&Page="+ str(SRApagenumber)
            print("opened: " + SRA_page_data_loop + "\n")
            SRA_currentpage = urlreader_to_soup(SRA_page_data_loop)
        
        #find SRA data, loop, open page and check COFA - requests used as bytes
            for SRA in SRA_currentpage.findAll("h2"):
                COFA_page_link = "https://solicitors.lawsociety.org.uk"+ SRA.a.get("href")
                print(COFA_page_link)
                COFA_page = requests.get(str(COFA_page_link)).text
                COFA_page_data = soup(COFA_page,"html.parser")
                try:
                    COFA_table = COFA_page_data.findAll("div", {"class":"panel-half"})[1].dd.ul.findAll("li")
                    COFA_found = False
                    for i in COFA_table:
                        if i.text == "Compliance Officer for Finance and Administration":
                            COFA_found = True
                            COFA = COFA_page_data.h1.text
                            break
                except:
                    print("Non conforming page layout")
                print("Checking COFA: "+ COFA_page_data.h1.text + "\n")

                                                    
        # prints to check  
        print("Firm Name: " + name)
        print("Address: " + address)
         
        try:
           print ("Telephone: " + str(tel.text))
           print_tel= tel.text
        except:
           print ("No telephone number")
           print_tel = ("No telephone number")
            
        try:
           print ("Number of offices: " + officeno.strip())
            
        except:
           print ("No office data given")
           officeno = ("No office data given")
        try:
           print ("Number of solicitors: " + solicno.strip())
        except:
           print ("No solictor numbers given")
           solicno = ("No solictor numbers given")
            
        try:
           print ("Number of accreditations: " + noAccreds.strip())
        except:
           print("number of accreditations not given")
           
        if COFA == "":
           print("No COFA")
           COFA = "No COFA"
        else:        
            try:
               print("The Compliance Officer for Finance and Administration is: " + COFA )
            except:
               print("There is no COFA")
               
        
        print("\n\n" + "--------------NEW COMPANY------------" + "\n\n")
    # write to csv
        f.write("'"+ name + "," + address.replace(",",".") + "," + "'" + print_tel + "," + officeno.strip() + "," + solicno.strip() + "," + noAccreds.strip() + "," + COFA + "\n")
        sleep(1)
f.close()