from getAozora import aozora
from split_node import ParseNode
from collections import Counter

with open("yaminoemaki.txt",encoding = "utf-8") as f:
    x = "".join([row for row in f])
l=[]
for s in ParseNode(x):
    for w in s:
        if w["Hinshi"]=="名詞":
            l.append(w["Text"])
C = Counter(l)
