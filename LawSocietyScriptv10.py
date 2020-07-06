#imports URL requester and BS
import requests
from urllib.request import urlopen
from time import sleep
from time import time
import sys
from bs4 import BeautifulSoup as soup
from IPython.core.display import clear_output

#location = sys.argv[1]
location = "bristol"

# Creating CSV for docs
filename = "SolicitorsDetails.csv"
f = open(filename , "w")
headers = "Company_Name,Address,Telephone,Num_Offices,Num_Solicitors,Num_Accreditations,COFA\n" 
f.write(headers)

# get page count
my_url = "https://solicitors.lawsociety.org.uk/search/results?Location="+ location + "&Pro=False&Page=1"
website = urlopen(my_url) # calling urlopen to request site
page_html = website.read() # connection grabbing the page
website.close() # close the client
page_data = soup(page_html,"html.parser") # file name and html parse

#find number of results
noResults = page_data.findAll("strong")
count = noResults[0].text
pages = (int(count)//20) + 2
print("total companies pages:" + str(pages))

start_time = time()
requests = 0

#Loop through pages of compfanies 
for pagenumber in range (1,pages):
    myurl_2 = "https://solicitors.lawsociety.org.uk/search/results?Location="+ location + "&Pro=False&Page=" + str(pagenumber)
    website = urlopen(myurl_2)
    page_html2 = website.read()
    website.close()
    page_data2 = soup(page_html2,"html.parser") # file name and html parse
    
    #define each productgrabs each product
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
         #print(solic_linkpage)
         
         solic_webpage = urlopen(solic_linkpage)
         solic_datapage = solic_webpage.read()
         solic_webpage.close()
         solic_data2page = soup(solic_datapage, "html.parser")
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
                 
                 solic_web = urlopen(solic_link)
                 solic_data = solic_web.read()
                 solic_web.close()
                 solic_data2 = soup(solic_data, "html.parser")       
                 
                 #solicitors containers for each name to run through
                 solic_containers = solic_data2.findAll("section")
    
                 #find each solicotor links
                 for s_cont in solic_containers:
                     indiv_link = "https://solicitors.lawsociety.org.uk"+s_cont.header.h2.a.get("href")
                     #print(indiv_link)
                     
                     #Open each solicitor link showing roles
                     cofa_web = urlopen(indiv_link)
                     cofa_data = cofa_web.read()
                     cofa_web.close()
                     cofa_data2 = soup(cofa_data,"html.parser")
        
                     
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