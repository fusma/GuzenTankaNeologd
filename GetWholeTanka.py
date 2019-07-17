import findTanka 
import WikipediaIntoText
import sys

with open("D:/Dette/VSCodeData/jawiki-20190701-pages-articles-multistream.xml",encoding="utf-8") as f:
    with open("Result.txt",mode = "w",encoding = "utf-8") as result:
        for i in range(10):
            title, text, page = WikipediaIntoText.read_page(sys.stdin)
            if not page:
                break
            result.write("---------------------------\n")
            result.write(f"記事名:{title}\n")
            result.write(text)

            