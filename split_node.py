import MeCab
import sys

def ParseNode(text,neologd = False):
    """Text,Hinshi,Yomi,Lengthをキーにする辞書のリストのリストを返す
    
    """
    if neologd:
        p = MeCab.Tagger("-Ochasen -d neologd")
    else :
        p = MeCab.Tagger("-Ochasen")
    p.parse("")#なんか消すとおかしくなるらしい
    node = p.parseToNode(text)
    Result = []
    Sentence = []
    while node:
        word = dict()
        word["Text"] = node.surface
        detail = node.feature.split(",")
        word["Hinshi"] = detail[0]
        word["Katsuyo"] = detail[5]
        if len(detail)>=9:
            word["Yomi"] = detail[8]
            word["Length"] = len(detail[8])
        else:
            word["Yomi"] = "*"
            word["Length"] = 0

        #後処理
        shoji = sum([word["Yomi"].count(t) for t in ("ァィゥェォャュョ")])
        word["Length"] -= shoji


        if detail[0] == "BOS/EOS":
            if Sentence:
                Result.append(Sentence)
        elif word["Yomi"] == "。":
            Result.append(Sentence)
            Sentence = []
        elif word["Hinshi"] == "記号":
            word["Length"]
        else:
            Sentence.append(word)
            
        node = node.next
    return Result

if __name__ == "__main__":
    t = "".join(sys.stdin.readlines())
    result = ParseNode(t,neologd=True)
    for sentence in result:
        print("\n".join([str(d) for d in sentence]))
        print("------------------------------")