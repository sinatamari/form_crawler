import requests
from bs4 import BeautifulSoup
import time,sys,threading
from urllib.parse import urlparse, urljoin
W = '\033[0m'
R = '\033[31m'
G = '\033[32m'
O = '\033[33m'
B = '\033[34m'
P = '\033[35m'
BOLD = '\033[1m'
ITALIC = '\033[3m'
THIN = '\033[2m'
BLINK = '\033[5m'
NORMAL = '\033[0m'
class FormCrawler:
    def __init__(self,number_of_threads=5,verbose=False):
        self.__verbose = verbose
        self.__window_size = number_of_threads
        self.__window = []
        self.__window_is_writing = False
        self.__links = {}
        self.__forms = {}
        self.__basic_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:73.0) Gecko/20100101 Firefox/73.0','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Language': 'en-US,en;q=0.5','Accept-Encoding': 'gzip, deflate','DNT': '1','Connection': 'close','Upgrade-Insecure-Requests': '1'}
    def __print(self,message,type="n",bar=False):
        """message:        => string message
        
        mtype:      "n" => normal
                    "e" => error
                    "w" => warning  
        some_stuff: 
                    can be anyting, like object, string, number etc ... 
        """
        if self.__verbose:
            if type == "n":
                if bar:
                    print(BOLD+P+'[ '+G+'+'+P+' ] '+O+message+THIN+W,end='\r',flush=True)
                else:
                    print(BOLD+P+'[ '+G+'+'+P+' ] '+O+message+THIN+W)
            elif type == "w":
                if bar:
                    print(BOLD+P+'[ '+O+'!'+P+' ] '+O+message+THIN+W,end='\r',flush=True)
                else:
                    print(BOLD+P+'[ '+O+'!'+P+' ] '+O+message+THIN+W)
            elif type == "e":
                if bar:
                    print(BOLD+P+'[ '+R+'-'+P+' ] '+O+message+THIN+W,end='\r',flush=True)
                else:
                    print(BOLD+P+'[ '+R+'-'+P+' ] '+O+message+THIN+W)
    def __show_banner(self):
        message = BOLD+'\n\n\t'
        message += G+'* '*25 +'\n\t'+'*'+'\t\t\t\t\t\t*\n\t'+'*\t'
        message += O+'\t  FORM CRAWLER'+G+'\t\t\t*\n\t*'
        message += '\t\t\t\t\t\t*\n\t'+'*\t'
        message += O+'\t '+ITALIC+THIN+'by Sina Tamari'+NORMAL+G+BOLD+'\t\t\t*'
        message += '\n\t*\t\t\t\t\t\t*\n\t'+'* '*25+THIN+W+'\n\n'
        if self.__verbose:
            print(message)
    def __show_crawler_prcess(self):
        self.__show_crawler_prcess_ended = False
        while True:
            time.sleep(0.5)
            message = str(self.__number_of_sent_requests)+" requests sent and "+str(self.__number_of_founded_forms)+" forms found"
            self.__print(message,type='w',bar=True)
            sys.stdout.flush()
            if self.__all_links_checked():
                break
        self.__show_crawler_prcess_ended = True
    def __check_link(self,url):
        try:
            x = requests.get(url,headers=self.__basic_headers,timeout=5).content.decode('utf-8','ignore')
            self.__number_of_sent_requests += 1
            obj = BeautifulSoup(x,features="lxml")
            for i in obj.find_all('a'):
                href = str(i.get('href'))
                if href != None and href != '' and href != '/' and href != '#' and href != './' and (not '../' in href or not '/..' in href):
                    domain_name = urlparse(url).netloc
                    ptr = urljoin(url,href)
                    parsed_href = urlparse(ptr)
                    href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
                    if self.__is_url_valid(href):
                        if domain_name in href:
                            if not href in list(self.__links):
                                self.__links.update({href:False})
            for i in obj.find_all('form'):
                if i != None:
                    self.__forms.update({self.__number_of_founded_forms:[url,i,False]})
                    self.__number_of_founded_forms += 1
            self.__links.update({url:True})
            while self.__window_is_writing:
                time.sleep(0.1)
            self.__window_is_writing = True
            self.__window.remove(url)
            self.__window_is_writing = False
        except:
            self.__links.update({url:True})
            while self.__window_is_writing:
                time.sleep(0.1)
            self.__window_is_writing = True
            self.__window.remove(url)
            self.__window_is_writing = False
    def __all_links_checked(self): 
        for i in list(self.__links):
            if not self.__links[i]:
                return False
        return True           
    def __crawl_website(self,website):
        self.__print('Crawling target ...')
        self.__links.update({website:False})
        self.__number_of_sent_requests = 0
        self.__number_of_founded_forms = 0
        t = threading.Thread(target=self.__show_crawler_prcess,args=[])
        t.start()
        while True:
            if self.__all_links_checked():
                break
            for i in list(self.__links):
                if not i in self.__window and not self.__links[i]:
                    while len(self.__window) >= self.__window_size:
                        time.sleep(1)
                    while self.__window_is_writing:
                        time.sleep(0.1)
                    self.__window_is_writing = True
                    self.__window.append(i)
                    self.__window_is_writing = False
                    t = threading.Thread(target=self.__check_link,args=[i])
                    t.start()
            time.sleep(0.1)
        while len(self.__window) > 0:
            time.sleep(1)
        while not self.__show_crawler_prcess_ended:
            time.sleep(1)
        self.__print(str(self.__number_of_sent_requests)+" requests sent and "+str(self.__number_of_founded_forms)+" forms found",'w')
    def __is_url_valid(self,url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    def __prepare_founded_forms(self):
        results = []
        for i in list(self.__forms):
            details = self.__get_form_details(self.__forms[i][0],self.__forms[i][1])
            results.append(details)
        return results
    def __get_form_details(self,url,form):
        details = {}
        form_name = form.attrs.get("name")
        if form_name != None:
            form_name = form_name.lower()
        form_id = form.attrs.get("id")
        if form_id != None:
            form_id = form_id.lower()
        action = form.attrs.get("action")
        if action != None:
            action = action.lower()
        method = form.attrs.get("method", "get")
        if method != None:
            method = method.lower()
        inputs = []
        for input_tag in form.find_all("input"):
            input_type = input_tag.attrs.get("type", "text")
            input_name = input_tag.attrs.get("name")
            input_value =input_tag.attrs.get("value", "")
            inputs.append({"type": input_type, "name": input_name, "value": input_value})
        details['form_name'] = form_name
        details['form_id'] = form_id
        details["action"] = action
        details["method"] = method
        details["inputs"] = inputs
        return details
    def RUN(self,website="http://example.com"):
        website += '/'
        if not self.__is_url_valid(website):
            self.__print('Invalid URL, Exiting ...','e')
            sys.exit(0)
        self.__show_banner()
        self.__print("Checking "+website+' ...')
        self.__crawl_website(website)
        if len(self.__forms.keys()) <= 0:
            self.__print('No forms found, Exiting ...',type='e')
            sys.exit(0)
        self.__print('Preparing founded forms')
        return self.__prepare_founded_forms()

obj = FormCrawler(verbose=True)
obj.RUN(website='https://service2.diplo.de')