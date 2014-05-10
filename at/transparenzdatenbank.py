
import requests
from pyquery import PyQuery
import re
import codecs

class Listing(object):
  
  def __init__(self,year=2011,url="http://www.transparenzdatenbank.at/trans/"):
    self.url=url
    self.year=year
    self.hiddenfields=None

  def get_hiddenfields(self):
    params={"bundesland":0,"betrag":"0,0","betrag_jahr":self.year,"numberOfLinesPerPage":"100","name":""}
    r=requests.post("%ssee.through"%self.url,data=params)
    if r.status_code==200:
      pq=PyQuery(r.text)
      self.hiddenfields=pq("form:eq(1) input").val()
      self.max=int(self.hiddenfields.split("|")[1])
      return (self.hiddenfields,self.max)
    else:
      return None
  
  def get_listing(self,number):
    if not self.hiddenfields:
      self.get_hiddenfields()
    params={"hiddenfields":self.hiddenfields, "move":u'\xA0%d\xA0'%number}
    r=requests.post("%sshow.detail"%self.url,data=params)
    pq=PyQuery(r.text)
    def extract_values(form):
      return dict([(x.name,x.value) for x in pq("input",form)])
    
    pages=[Page(self.url,extract_values(form)) for form in 
      pq("table.border > tr > td.center > form")]
    return pages

  def get_all_listings(self):
    if not self.hiddenfields:
      self.get_hiddenfields()
    return reduce(lambda x,y: x+y, 
      map(lambda x: self.get_listing(x),range(1,self.max+1)))

  def save_csv(self,filename):
    pages=self.get_all_listings()
    f=codecs.open(filename,"w","utf-8")
    f.write("%s\n"%",".join(pages[0].order))
    for page in pages:
      f.write(page.csv())
    f.close()  
    
class Page(object):
  order=["unique","ukey","name","ort","program","amount","year"]
  
  def __init__(self,url="http://www.transparenzdatenbank.at/trans/",params=None):
    self.url="%sshow.detail"%url
    self.params=params
    
  def get_html(self):
    r=requests.post(self.url,data=self.params)
    if r.status_code==200:
      self.html=r.text
      return self.html
    else:
      return None
  def get_items(self):
    pq=PyQuery(self.get_html())
    rows=pq("table.border tr")
    rows.pop()
    rows.pop(0) # remove first and last - heading and summary
    def extract_items(row):
      program=pq("td:eq(0)",row).html()
      amount=pq("td:eq(1)",row).html()
      amount=float(re.sub("[^0-9,]","",amount).replace(",","."))
      return {"amount":amount,"program":program}

    items=[extract_items(row) for row in rows]
    return items
 
  def get_records(self):
    m=re.match("(.*?),([^,]+)$",self.params["location"])
    if m:
      name=m.group(1)
      ort=m.group(2)
    else:
      name=self.params["location"]
      ort=name
    name.strip()
    ort.lstrip()
    year=int(re.sub("[^0-9]","",self.params["year"]))
    unique=self.params["unique"]

    def construct_record(item):
      return dict(item.items()+[("name",name),("ort",ort),
      ("year",year),("unique",unique),("ukey",u"%s-%s"%(unique,item["program"]))])

    return [construct_record(i) for i in self.get_items()] 
  
  def csv(self):
    def line(r):
      return u",".join([u"%s"%r[i] for i in self.order])

    return u"%s\n"%"\n".join([line(r) for r in self.get_records()])  
