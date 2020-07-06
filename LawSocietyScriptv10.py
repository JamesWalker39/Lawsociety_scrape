#imports URL requester and BS
import requests
from urllib.request import urlopen
from time import sleep
from time import time
import sys
from bs4 import BeautifulSoup as soup
from IPython.core.display import clear_output

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
filename = "SolicitorsDetails.csv"
f = open(filename , "w")
headers = "Company_Name,Address,Telephone,Num_Offices,Num_Solicitors,Num_Accreditations,COFA\n" 
f.write(headers)

# get page count
my_url = "https://solicitors.lawsociety.org.uk/search/results?Location="+ location + "&Pro=False&Page=1"
page_data = urlreader_to_soup(my_url)

#find number of results
noResults = page_data.findAll("strong")
count = noResults[0].text
pages = (int(count)//20) + 2
print("total companies pages:" + str(pages))

start_time = time()
requests = 0

#Loop through pages of companies 
for pagenumber in range (1,pages):
    myurl_2 = "https://solicitors.lawsociety.org.uk/search/results?Location="+ location + "&Pro=False&Page=" + str(pagenumber)
    page_data2 = urlreader_to_soup(myurl_2) # file name and html parse
    
    #define each product,grabs each product
    containers = page_data2.findAll("section",
                                   {"class":"solicitor solicitor-type-firm"})
    print("company page of results:" + str(pagenumber))

    # loop through details for each company
    for container in containers: 
         requests += 1
         #monitor requests
         elapsed_time = time () - start_time
         print('Request:{}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
         clear_output(wait = True)
        
         name = container.h2.text
         address = container.find("dd").text
         tel = container.find("dd", attrs = {"class":"hidden-phone"})
         officeno = container.find("p", {"class":"hidden-phone"}).a.text
         solicno = container.find("p", {"class":"hidden-phone"}).span.a.strong.text
         try:
             noAccreds = container.find("div", {"class":"accreditations hidden-phone"}).strong.text
         except:
             noAccreds = "no accreditations given"
             
             
        # solicitor pages numbers count
         solic_linkpage = "https://solicitors.lawsociety.org.uk"+container.findAll('a')[2].get('href')
         print(solic_linkpage)
         solic_data2page = urlreader_to_soup(solic_linkpage)
         
         page_nos = int(solic_data2page.find("div", {"class":"row-fluid"}).h1.strong.text)//20 + 2
         print("total solicitor pages: " + str(page_nos - 1))
         
             #open and parse each page containing multiple solicitors 
         COFA_found = False
         for solic_page_nos in range(1,page_nos):
             if COFA_found == True:
                 break
             else:
                 solic_link = "https://solicitors.lawsociety.org.uk" + container.findAll('a')[2].get('href') + "&Page=" + str(solic_page_nos)
                 print("solicitor page: " + str(solic_page_nos))
                 solic_data2 = urlreader_to_soup(solic_link)    
                 
                 #solicitors containers for each name to run through
                 solic_containers = solic_data2.findAll("section")
    
                 #find each solicotor links
                 for s_cont in solic_containers:
                     indiv_link = "https://solicitors.lawsociety.org.uk"+s_cont.header.h2.a.get("href")
                     #print(indiv_link)
                     
                     #Open each solicitor link showing roles
                     cofa_data2 = urlreader_to_soup(indiv_link)
        
                     
                     #define role table and iterate through roles to find COFA
                     role_list = cofa_data2.findAll("li")
                     for role in role_list:
                          if role.text == "Compliance Officer for Finance and Administration":
                              COFA = (cofa_data2.find("h1")).text
                              COFA_found = True
                          else:
                              pass
                 
                                                    
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
        
         
    # write to csv
         f.write("'"+ name + "," + address.replace(",",".") + "," + "'" + print_tel + "," + officeno.strip() + "," + solicno.strip() + "," + noAccreds.strip() + "," + COFA + "\n")
         sleep(1)
         COFA = ""
f.close()