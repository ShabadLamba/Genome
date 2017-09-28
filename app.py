from flask import Flask, render_template, request
# from flask.ext.sqlalchemy import SQLAlchemy

# from flask.ext.heroku import Heroku

import requests
import simplejson as sjson


from bs4 import BeautifulSoup
import re
import urllib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import utility

# import datetime

# from firebase.firebase import FirebaseApplication, FirebaseAuthentication

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/pre-registration'

# heroku = Heroku(app)

# db = SQLAlchemy(app)

# # Create our database model
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True)

#     def __init__(self, email):
#         self.email = email

#     def __repr__(self):
#         return '<E-mail %r>' % self.email

def addDataToFirebase(obj):
    # dict = {"dna": "asjdnaksjd", "feature1": 1241}
    r=requests.put("https://genome-3db7f.firebaseio.com/dna_features/" + obj["phage_name"] + ".json", data=sjson.dumps(obj["data"]))
    return r.content

def getDataFromFirebase():
    r=requests.get("https://genome-3db7f.firebaseio.com/dna_features.json")
    return r.json()

# Set "homepage" to index.html
@app.route('/')
def index():
    return render_template('index.html')

def getListOfPhages():
    print ("Getting list of phages")
    try:
        r = urllib.urlopen('https://www.ncbi.nlm.nih.gov/genomes/GenomesGroup.cgi?taxid=10239').read()
        print ("Got list of phages")
        soup = BeautifulSoup(r,'html.parser')
        phage = soup.find_all('a')
        return phage
    except Exception as e:
        print (e)
        return False

def extractPhageData(phage):
    ListOfVirusesInfo2 = []
    for i in range(0,len(phage)):
        try:
            VirusesDict2 = {}
            if "dsDNA viruses, no RNA stage; Species:" in phage[i]['title']:
                VirusesDict2['Name'] = phage[i+1].get_text()
                VirusesDict2['phage_name'] = phage[i].get_text()
                VirusesDict2['link'] = "https://www.ncbi.nlm.nih.gov" + phage[i+1]['href']
                ListOfVirusesInfo2.append(VirusesDict2)
        except Exception as e:
            # print (e)
            continue

    return ListOfVirusesInfo2

def getDNAFromLink(link):
    try:
        # print ("Loading PhantomJS")
        driver = webdriver.PhantomJS(executable_path="bin/phantomjs")
        driver.set_window_size(1120, 550)
        # driver.get(ListOfVirusesInfo2[0]['link'])
        driver.get(link)
        ### element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "sequence")))
        # elem = driver.find_element_by_class_name("sequence")
        elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ff_line")))
        sourceCode = ''
        for element in elements:
            sourceCode = sourceCode + element.get_attribute('innerHTML')
            sourceCode = sourceCode.replace(" ", "")
        
        # print (sourceCode)
        driver.close()


        # In[33]:

        # stringSC = str(sourceCode[sourceCode.find("ORIGIN"):sourceCode.find("//")])
        # print(stringSC)


        # In[40]:

        # Sequence = ''
        # listOfSequence = (''.join([i for i in re.sub('\<.*?\>','', stringSC) if i not in str(range(0,10))])).split('\n')
        # for i in range(1,len(listOfSequence)-1):
            # Sequence += listOfSequence[i]
        # print(Sequence)
        return sourceCode
    except Exception as e:
        print (e)
        return False

@app.route('/crawl')
def crawl():
    phage = getListOfPhages()
    print("Getting List of Viruses")
    if(phage):
        ListOfVirusesInfo2 = extractPhageData(phage)
        print("Got List of Viruses")
    else:
        ListOfVirusesInfo2 = []

    for info in ListOfVirusesInfo2:
    # info = ListOfVirusesInfo2[1]
        try:
            print("Getting data for Link: ")
            print(info['link'])
            info['dna'] = getDNAFromLink(info['link'])
            print ("Got DNA")
            # print (info['dna'])
            if(info['dna']):
                print ("Getting Features for DNA")
                # At this point we have dna and phage_name data.
                features = utility.featureSearch(info['dna'])
                # print (features)
                listOfLocationsOfFeatures = utility.deterministicSearch(features)
                print ("Getting list of locations")
                # print (listOfLocationsOfFeatures)
                sequence = utility.fetchingTheSequences(info['dna'], listOfLocationsOfFeatures)
                print ("Sequence")
                # print (sequence)
                # sequence has promoter and features.
                # Now to add this data to firebase database
                firebaseData = {"dna": info['dna'], "sequenceList": sequence}
                print ("Firebase Data")
                # print (firebaseData)
                r=addDataToFirebase({"phage_name": info['phage_name'].replace(" ", "_"),"data": firebaseData})
        except Exception as e:
            print ("Firebase Exception")
            print (e)
            continue

    return "crawling finished"
    

# Save e-mail to database and send to success page
@app.route('/prereg', methods=['POST'])
def prereg():
    email = None
    if request.method == 'POST':
        email = request.form['email']
        # Check that email does not already exist (not a great query, but works)
        if not db.session.query(User).filter(User.email == email).count():
            reg = User(email)
            db.session.add(reg)
            db.session.commit()
            return render_template('success.html')
    return render_template('index.html')

if __name__ == '__main__':
    app.debug = True
    app.run()