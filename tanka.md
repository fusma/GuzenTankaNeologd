## 偶然短歌botをぼくもやりたいので、PythonにてMeCabと格闘する
---
[偶然短歌bot](https://twitter.com/g57577)というのがある。Wikipediaの記事の中から57577になっている部分を取り出し投稿するbotだ。
たとえば[こういうの](https://twitter.com/g57577/status/550141727835967488?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E550141727835967488&ref_url=https%3A%2F%2Fwww.huffingtonpost.jp%2F2015%2F01%2F18%2Fwikipedia-tanka_n_6497840.html)。良い。
あるいは[こういうの](https://twitter.com/g57577/status/1148140241531875329)。もしくは[こういうの](https://twitter.com/g57577/status/1142054780019335168)。良すぎる。
[こういうの](https://twitter.com/g57577/status/1145256221265543169)もあった。デジタル俵万智である。
Wikipediaのもつ無機質な文体が、短歌という形で取り出されることによって、荒涼とした侘び寂びのようなものを生み出していて心惹かれるかんじ、たまらん。

……同じことを、やりたい。任意のテキストから短歌を探すやつを、作りたい。

詳しくはわからないが、おそらく形態素解析を用いて単語の音数を抽出し、57577になる部分を抜き取っているのだろう。  
形態素解析といえば、[こないだの記事](Link)のはてブコメントで存在を知ったやつだ。日本語を品詞単位で分解するやつ。Pythonでも動くライブラリがあるらしい。

Pythonでできるなら、たぶん、いける。やってみよう。  
必要なのはおそらく

* PythonでMeCabをセットアップする
* 単語の文字数を取得してデータ化する
* 57577になってる部分を探す

のらへんだろう。

### MeCabのセットアップ
---
文の分析には形態素解析エンジンの中で一番メジャーっぽいMeCabを使う。   
MeCabの導入までには[この記事](https://qiita.com/osyou-create/items/c7864a5200238d8678aa)をほぼまんま参考にした。

また、MeCab標準の辞書だと新語に対応できていないとの話だったので、追加辞書「mecab-ipadic-NEologd」を導入した。参考にしたのは[このサイト](https://www.pytry3g.com/entry/2018/04/24/143934)。これがかなりしんどかった。このためだけにgitとUbuntuを導入した。泣きそうになった。gitの使い方はこれから勉強します。

とりあえずテストでコードを動かしてみる。
```Python
import MeCab
t = MeCab.Tagger("Ochasen -d neologd")
print(t.parse(input(">>")))

```
こうなった。(testparse:なるほどね)  
なるほど確かに文章が分解できている。この分解の単位を「形態素」と呼ぶらしい。  
あとは、各形態素ごとの文字数が取得できればいいわけだ。書くぞ！！！！！！！！

```Python
import MeCab
import sys

def ParseNode(text):
    p = MeCab.Tagger("-Ochasen -d neologd")
    p.parse("")#なんか消すとおかしくなるらしい
    node = p.parseToNode(text)
    Result = []
    Sentence = []
    while node:
        print(node.feature.split(","))
        word = dict()
        word["text"] = node.surface
        detail = node.feature.split(",")
        word["hinshi"] = detail[0]

        if len(detail)>=9:
            word["Yomi"] = detail[8]
            word["Length"] = len(detail[8])
        else:
            word["Yomi"] = "*"
            word["Length"] = 0

        node = node.next

        if detail[0] == "BOS/EOS":
            if Sentence:
                Result.append(Sentence)
        elif word["Yomi"] == "。":
            Result.append(Sentence)
            Sentence = []
        elif word["hinshi"] == "記号":
            pass
        else:
            Sentence.append(word)
        
        if word["Length"] == "*":word["Length"] = 0
    print(type(node))
    return Result

if __name__ == "__main__":
    t = "".join(sys.stdin.readlines())
    result = ParseNode(t)
    for sentence in result:
        print("\n".join([str(d) for d in sentence]))
        print("------------------------------")
```
書いた。parseToNodeメソッドの仕様がよくわからなかったので手探りで書いたが、どうも以下のようになっているらしい。

* 返り値はnodeというものが連結された状態
* node.surfaceには、単語(形態素)の文字列が入っている 
* node.featureには、単語(形態素)の品詞/品詞の細分類(固有名詞など)/さらなる細分類(人名など)/謎の分類(おそらく細分類の備考)/活用形式/活用形/原型/読み仮名/読みの順にカンマ区切りでデータが入っている
* node.nextを代入することで、次の形態素に進める

このnodeデータからとりあえず、文字列/品詞/読み/読みの文字数 の4つを取得してリストにまとめた。こんな感じ。
(pic)
### 57577探し
---
形態素に分解したら、それらが5・7・5・7・7音でつながっている部分を探す。松尾芭蕉もこうやって俳句を作っていたのだろうか。
こういう系のアルゴリズムは色々思いつきそうだが、今回は武力で解決しようと思う。すなわち、あらゆる名詞・動詞・連体詞・副詞から形態素の文字数を数えていき、ちょうどよく57577にマッチしたら短歌とみなす。

<details><summary>コードが汚くて恥ずかしい</summary>

```Python
from split_node import ParseNode
import MeCab
import itertools
import sys

def FindTanka(text,neologd=False):
    """
    テキストをぶちこむと短歌のリストを返してくれる風流な関数。
    """
    Nodes = ParseNode(text,neologd=neologd)
    TankaPoint = (5,12,17,24,31,32)
    Tankas = []
    for sentence in Nodes:
        l = len(sentence)
        for n,StartWord in enumerate(sentence):
            if StartWord["Yomi"] =="*" or\
            StartWord["Hinshi"] not in ("名詞","動詞","連体詞","副詞"):continue
            sound = 0
            curpos = n
            tanka = ""
            tankalen = 0
            while sound<=31 and curpos<l:
                w = sentence[curpos]
                #句の始まりが助詞や助動詞でないかどうか
                if sound in TankaPoint:
                    if w["Hinshi"] not in ("名詞","動詞","連体詞","副詞"):
                        break       
                if w["Yomi"]!="*":
                    tanka += w["Text"]
                    sound += w["Length"]
                    if sound ==TankaPoint[tankalen]:
                        tankalen+=1
                    if tankalen == 5:
                        Tankas.append(tanka)
                        break
                curpos+=1
    return(Tankas)

if __name__ == "__main__":
    print(FindTanka(wikipedia(input("url:")),neologd = True))
```
</details>

コードは長いが、要するに単語をひとつずつ数えて短歌になっているかどうか調べている。
これで偶然短歌をぼくも作れるはずだ！
とりあえずこのプログラムに青空文庫から「人間失格」をぶちこんだ結果がこれ。
(pic)
「政党の有名人がこの町に演説に来て自分は下男」
「画家たちは人間という化け物に傷めつけられおびやかされた」あたりは短歌として成り立っていそうだが、その他はどうもしっくりこない。
俳句の終わり際が不自然なので、「体言止め」または「文節の切れ目」で終わっていれば良いはず。

というわけで魔改造した。
<details><summary>明らかに処理に無駄が多い気はするが…</summary>

```Python
from split_node import ParseNode
import MeCab
import itertools
import sys

JIRITSUGO = (
"動詞","形容詞","接続詞",
"名詞","副詞","連体詞","感動詞")#自立後のリスト
FUZOKUGO = ("助詞","助動詞")

def FindTanka(text,neologd=False):
    """
    テキストをぶちこむと短歌のリストを返してくれる風流な関数。
    """
    Nodes = ParseNode(text,neologd=neologd)
    TankaPoint = (5,12,17,24,31,32)
    Tankas = []
    for sentence in Nodes:
        l = len(sentence)
        for n,StartWord in enumerate(sentence):
            if StartWord["Yomi"] =="*" or\
            StartWord["Hinshi"] not in JIRITSUGO:continue
            sound = 0
            curpos = n
            tanka = ""
            tankalen = 0
            while sound<=32 and curpos<l:
                w = sentence[curpos]
                #句(57577)の始まりが助詞や助動詞でないかどうか
                if sound in TankaPoint and tankalen<=4:
                    if w["Hinshi"] not in ("名詞","動詞","連体詞","副詞","形容詞"):
                        break    
                if w["Yomi"]!="*":
                    tanka += w["Text"]
                    sound += w["Length"]
                    if sound ==TankaPoint[tankalen]:
                        tankalen+=1
                    if tankalen == 5:#短歌が完成した場合
                        if (w["Hinshi"] in JIRITSUGO and "連用" not in w["Katsuyo"])  or (curpos<l-1 and sentence[curpos+1]["Hinshi"] in JIRITSUGO):
                            Tankas.append(tanka)
                            break
                    if tankalen == 6:#31文字でうまく終わらなかった場合の安全策
                        Tankas.append(tanka)
                        break
                curpos+=1
                
    return(Tankas)

if __name__ == "__main__":
    print(FindTanka(aozora(input("url:")),neologd = True))
```

</details>

用言の場合は連用形で終わっているものと、直後にまだ助詞/助動詞が続くものを結果から外した。と同時に、字余りの「57578」を許可した。すべての字余りのパターンを許容するとコーディングが地獄すぎるので、違和感が少なそうな最後の字余りだけ対応した。
その結果がこちら。
