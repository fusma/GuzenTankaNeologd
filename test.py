import MeCab
t = MeCab.Tagger("Ochasen")
print(t.parse(input(">>")))
