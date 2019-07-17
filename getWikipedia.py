from bs4 import BeautifulSoup
import requests
import re

def wikipedia(article,isurl=False):
    if isurl:
        url = article
    else:
        url = "https://ja.wikipedia.org/wiki/"+article
    text = ""
    wikihtml = requests.get(url)
    wikihtml.encoding = wikihtml.apparent_encoding
    soup = BeautifulSoup(wikihtml.text,"html.parser")
    kizi = soup.find_all("p")
    for k in kizi:
        text += k.text
    result = re.sub(r"\[\d\]","",text)
    return result
    

if __name__ == "__main__":
    print(wikipedia(input()))