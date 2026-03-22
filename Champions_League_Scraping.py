import urllib
from urllib import request
from urllib import error
import time
import os

if not os.path.exists('Champions_League'):
    os.mkdir("Champions_League")


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Cache-Control": "max-age=0"
}
     


for i in range(1990, 2025):
    
    try:
        link_tmp = "https://fbref.com/en/comps/8/" + str(i) + "-" + str(i+1) + "/schedule/" + str(i) + "-" + str(i+1) + "-Champions-League-Scores-and-Fixtures"
        name = link_tmp.split('/')[-3]
        request = urllib.request.Request( link_tmp, None, headers )
        response = urllib.request.urlopen(request)
        
        with open('Champions_League/' + name+".html", 'w',encoding="utf-8") as f:
            f.write(str(response.read().decode('utf-8')))
            print("Season", i, "-", i+1, "scraped")
        time.sleep(5)
        
    except urllib.error.HTTPError as e:
        print(e)