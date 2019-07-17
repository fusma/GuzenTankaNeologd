
"""
Wikipedia の dump ファイルから、 page を切り出して title と text を抽出
https://dumps.wikimedia.org/jawiki/ にある
https://dumps.wikimedia.org/jawiki/YYYYMMDD/jawiki-YYYYMMDD-pages-articles.xml.bz2 がデータソース
$ bzcat < jawiki-YYYYMMDD-pages-articles.xml.bz2 | ./ja_wikipedia_title_text.py
https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-pages-articles.xml.bz2-rss.xml
から辿れるものと同じ？同じなら、以下でダウンロードから一挙に処理できる
wget -O - https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-pages-articles.xml.bz2-rss.xml |sed -n 's/.*href="\([^"]*\).*/\1/p' | xargs wget -O - | bzcat | ./ja_wikipedia_title_text.py
"""
import sys
import re
from xml.sax.saxutils import unescape

def strip_tag(start_tag, end_tag, page):
    start = page.find(start_tag)
    if start < 0:
        return ''
    start += len(start_tag)
    end = page[start:].find(end_tag)
    # unescape and trim comment
    s = re.sub('<!--(.+?)-->', '', unescape(page[start:start + end]))
    return s


def read_page(infile):
    while True:
        s = infile.readline()
        if s == '' or s.strip() == '<page>':
            break
    page = ''
    while True:
        s = infile.readline()
        if s == '' or s.strip() == '</page>':
            break
        page += s
    title = strip_tag('<title>', '</title>', page)
    text = strip_tag('<text xml:space="preserve">', '</text>', page)
    return title, text, page


if __name__ == "__main__":
    while True:
        title, text, page = read_page(sys.stdin)
        if not page:
            break
        print(title)