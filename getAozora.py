from bs4 import BeautifulSoup
import requests

def aozora(url):
    text = ""
    aozorahtml = requests.get(url)
    aozorahtml.encoding = aozorahtml.apparent_encoding
    soup = BeautifulSoup(aozorahtml.text,"html.parser")
    honbun = soup.find("div",class_="main_text")
    ruby1 = honbun.find_all("rp")
    if ruby1:
        for r1 in ruby1:
            r1.extract()
    ruby2 = honbun.find_all("rt")
    if ruby2:
        for r2 in ruby2:
            r2.extract()
    return(honbun.text)
if __name__ == "__main__":
    print(aozora(input()))