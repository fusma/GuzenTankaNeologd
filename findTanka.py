from split_node import ParseNode
from getAozora import aozora
from getWikipedia import wikipedia
import MeCab
import itertools
import sys
import numpy as np
import re

def readlines():
    return " ".join(sys.stdin.readlines())

JIRITSUGO = (
"動詞","形容詞","接続詞",
"名詞","副詞","連体詞","感動詞","記号")#自立後のリスト
FUZOKUGO = ("助詞","助動詞")

def FindTanka(text,neologd=False):
    """
    テキストをぶちこむと短歌のリストを返してくれる風流な関数。
    """
    text =  re.sub("　"," ",re.sub(r"\r"," ",text))
    Nodes = ParseNode(text,neologd=neologd)
    Tankalist = (5,7,5,7,7)#ここのタプルをいじると自由に検出が変更可能
    TankaPoint = np.cumsum(Tankalist+(1,))
    Tankas = []
    for sentence in Nodes:
        l = len(sentence)
        for n,StartWord in enumerate(sentence):
            if StartWord["Yomi"] in("*","、") or StartWord["Hinshi"] in FUZOKUGO:
                continue
            sound = 0
            curpos = n
            tanka = ""
            tankalen = 0
            while sound<=TankaPoint[-1] and curpos<l:
                w = sentence[curpos]
                if w["Hinshi"]=="記号":
                    tanka += w["Text"]
                    curpos += 1
                    continue
                #句(57577)の始まりが助詞や助動詞でないかどうか
                if sound in TankaPoint and tankalen<=4:
                    if w["Hinshi"] in FUZOKUGO:
                        break    
                if w["Yomi"]!="*":
                    tanka += w["Text"]
                    sound += w["Length"]
                    if sound ==TankaPoint[tankalen]:
                        tankalen+=1
                    if tankalen == len(TankaPoint)-1:#短歌が完成した場合
                        if (w["Hinshi"] in JIRITSUGO and "連用" not in w["Katsuyo"])  or (curpos<l-1 and sentence[curpos+1]["Hinshi"] in JIRITSUGO):
                            Tankas.append(tanka)
                            break
                    if tankalen == len(TankaPoint):#31文字でうまく終わらなかった場合の安全策
                        Tankas.append(tanka)
                        break
                curpos+=1
                
    return(Tankas)

if __name__ == "__main__":
    print(FindTanka(wikipedia(input("url:")),neologd = True))
    #print(FindTanka(readlines()))