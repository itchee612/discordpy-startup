import discord
import collections
import os

client = discord.Client()
token = os.environ['DISCORD_BOT_TOKEN']

start = False   #これがTrueだと試合中
player = [None,None]
content = ""
speak = False   # これがTrueになったたらBOTがしゃべる
SIDE = [6,6]
FIELD = [[None for j in range(6)] for i in range(2)]
HP = [[65536 for j in range(6)] for i in range(2)]
MAX_HP = [[65536 for j in range(6)] for i in range(2)]
ITEM = [[None for j in range(6)] for i in range(2)]
ENERGY = [[[None for k in range(0)] for j in range(6)] for i in range(2)]
GX = [False, False]
error = False
hp = 65536
energy = 1
change_hp = 0
stadium = "なし"

# エラー関数
def er():
    global error
    global speak
    error = False
    speak = True
    return "エラー発生 もう一度入力してください"

# プレイヤーチェック関数
def pl_checker(aut, supp=2):
    if supp == 0 or supp == 1:
        return supp
    elif aut == player[0]:
        return 0
    elif aut == player[1]:
        return 1
    else:
        return "error"

# サポーターチェック関数
def supp_checker(spl):
    try:
        if spl[1] == "1p" or spl[1] == "1P":
            del spl[1]
            return spl, 0
        elif spl[1] == "2p" or spl[1] == "2P":
            del spl[1]
            return spl, 1
        else:
            return spl, 2
    except:
        return spl, 2

# セット関数 ポケモンを配置するのに使用
def set(player, id, poke, hp):
    global FIELD
    global HP
    FIELD[player][id-1] = poke
    HP[player][id-1] = hp
    MAX_HP[player][id-1] = hp
    return player

# アウト関数 ポケモンの退場に使用
def out(player, id):
    global FIELD
    global HP
    global ITEM
    FIELD[player][id-1] = None
    HP[player][id-1] = 65536
    MAX_HP[player][id-1] = 65536
    ITEM[player][id-1] = None
    ENERGY[player][id-1] = []
    return player

# チェンジ関数 ポケモンの交換に使用
def change(player, id, id2):
    global FIELD
    global HP
    global ITEM
    FIELD[player][id-1],  FIELD[player][id2-1] = FIELD[player][id2-1], FIELD[player][id-1]
    HP[player][id-1], HP[player][id2-1] = HP[player][id2-1], HP[player][id-1]
    MAX_HP[player][id-1], MAX_HP[player][id2-1] = MAX_HP[player][id2-1], MAX_HP[player][id-1]
    ITEM[player][id-1], ITEM[player][id2-1] = ITEM[player][id2-1], ITEM[player][id-1]
    ENERGY[player][id-1], ENERGY[player][id2-1] = ENERGY[player][id2-1], ENERGY[player][id-1]
    return player

# ダメージ関数 ポケモンにダメージを与える関数
def damage(player, id, damecan):
    global HP
    global MAX_HP
    HP[player][id-1] -= damecan
    if HP[player][id-1] > MAX_HP[player][id-1]:
        HP[player][id-1] = MAX_HP[player][id-1]
    if HP[player][id-1] <= 0:
        player = out(player, id)
    return player

# サイド関数 サイドを取る関数
def side(player, get_side):
    global SIDE
    SIDE[player] -= get_side
    return "残りサイドは"+ str(SIDE[player]) +"枚です"

# GX関数 GXワザの使用チェック
def gx(player):
    global GX
    text = "プレイヤー"+ str(player+1) +"はGXワザ"
    if GX[player]:
        GX[player] = False
        text += "がまだ使用可能です。"
    else:
        GX[player] = True
        text += "を使用しました"
    return text

# ポケモンの道具関数 ポケモンの道具を装備させたり剥がしたりする
def item(player, id, dougu, change_hp):
    global ITEM
    global MAX_HP
    global HP
    if dougu == "0":
        ITEM[player][id-1] = None
    else:
        ITEM[player][id-1] = dougu
    MAX_HP[player][id-1] += change_hp
    HP[player][id-1] += change_hp
    return player

# エネルギーセット関数 エネルギーをつける
def set_energy(player, id, energy, num):
    global ENERGY
    for v in range(num):
        ENERGY[player][id-1].append(energy)
    return player

# エネルギートラッシュ関数 エネルギーを外す
def trash_energy(player, id, energy, num):
    global ENERGY
    for v in range(num):
        ENERGY[player][id-1].remove(energy)
    return player

# 場関数 場の状況を読み上げさせる
def ba(player):
    global FIELD
    global HP
    global MAX_HP
    global speak
    text = ""
    speak = True
    for v in range(6):
        if v == 0:
            text += "バトル場:"
        else:
            text += "ベンチ" + str(v) +":"

        if FIELD[player][v] != None:
            text += FIELD[player][v]
            if HP[player][v] < 10000:
                text += "(HP" + str(HP[player][v]) +"/"+ str(MAX_HP[player][v]) +")"
            if ENERGY[player][v] != []:
                text += "("
                c = collections.Counter(ENERGY[player][v])
                for w in c.keys():
                    text += str(w) + str(c[w]) + " "
                text = text.rstrip()
                text += ")"
            if ITEM[player][v] != None:
                text += "(E:" + str(ITEM[player][v]) +")"
        else:
            text += "なし"

        if v < 6:
            text += "\n"
    if FIELD[player][0] == None:
        text += "\nプレイヤー"+ str(player+1) +"のバトル場にポケモンがいません。\n/setや/changeでバトル場にポケモンを出してください。"

    return text

@client.event
async def on_ready():
    print("on_ready")
    print(discord.__version__)

@client.event
async def on_message(message):
    # グローバル宣言
    global start
    global player
    global content
    global text
    global speak
    global FIELD
    global mess_ori
    global mess_spl
    global support
    global error
    global hp
    global SIDE
    global MAX_HP
    global stadium
    global GX
    global change_hp
    global energy

    # BOTを省く
    if message.author.bot:
        return

    # スタートコマンド 処理を開始させる
    if start == False:
        if message.content == "/start":
            start = True
            text = "1Pと2Pの設定を行います。選手登録してください。"
            speak = True

    # 登録コマンド プレイヤーを確定させる
    elif player[0] == None or player[1] == None:
        if message.content == "/1P" or message.content == "/1p":
            player[0] = message.author
            text = "1Pは" + str(message.author) + "を登録しました。"
            speak = True

        if message.content == "/2P" or message.content == "/2p":
            player[1] = message.author
            text = "2Pは" + str(message.author) + "を登録しました。"
            speak = True

    # ここから実際の対戦記録を開始 ここまでの処理が完了していないと開示されない
    else:
        mess_ori = message.content
        mess_spl = mess_ori.split() #ここからは複数個の変数を要求させるので分ける作業をする

        # セットコマンド ポケモンの配置
        if mess_spl[0] == "/set" or mess_spl[0] == "/se":
            mess_spl, support = supp_checker(mess_spl)

            try:
                hp = int(mess_spl[3])
            except: # ここでエラーがでた → HPの値が数字じゃないか少数か空 → HPの表示を初期値へ
                hp = 65536

            try:
                pl = set(pl_checker(message.author, support), int(mess_spl[1]), mess_spl[2], hp)
            except:
                error = True

            if error:
                text = er()
            else:
                text = ba(pl)

        # アウトコマンド ポケモンの退場
        if mess_spl[0] == "/out" or mess_spl[0] == "/o":
            mess_spl, support = supp_checker(mess_spl)
            try:
                pl = out(pl_checker(message.author, support), int(mess_spl[1]))
            except:
                error = True

            if error:
                text = er()
            else:
                text = ba(pl)

        # チェンジコマンド ポケモンの交代
        if mess_spl[0] == "/change" or mess_spl[0] == "/c":
            mess_spl, support = supp_checker(mess_spl)
            try:
                pl = change(pl_checker(message.author, support), int(mess_spl[1]), int(mess_spl[2]))
            except:
                error = True

            if error:
                text = er()
            else:
                text = ba(pl)

        # ダメージコマンド ポケモンにダメージ
        if mess_spl[0] == "/damage" or mess_spl[0] == "/d":
            if message.author == player[0] and mess_spl[1] != "1P" and mess_spl[1] != "1p":
                target = 1
            elif message.author == player[1] and mess_spl[1] != "2P" and mess_spl[1] != "2p":
                target = 0
            else:
                target = pl_checker(message.author, support)

            mess_spl, support = supp_checker(mess_spl)
            try:
                pl = damage(target, int(mess_spl[1]), int(mess_spl[2]))
            except:
                error = True

            if error:
                text = er()
            else:
                text = ba(pl)

        # サイドコマンド サイドを取る
        if mess_spl[0] == "/side" or mess_spl[0] == "/si":
            mess_spl, support = supp_checker(mess_spl)
            try:
                text = side(pl_checker(message.author, support), int(mess_spl[1]))
            except:
                error = True

            if error:
                text = er()
            else:
                speak = True

        # スタジアムコマンド スタジアムの配置
        if mess_spl[0] == "/stadium" or mess_spl[0] == "/st":
            try:
                stadium = mess_spl[1]
            except:
                stadium = "なし"
            text = "スタジアム:"+ stadium
            speak = True

        # GXコマンド GXワザの使用チェック
        if mess_spl[0] == "/GX" or mess_spl[0] == "/gx" or mess_spl[0] == "/g":
            mess_spl, support = supp_checker(mess_spl)
            try:
                text = gx(pl_checker(message.author, support))
            except:
                error = True

            if error:
                text = er()
            else:
                speak = True

        # ポケモンの道具コマンド
        if mess_spl[0] == "/item" or mess_spl[0] == "/i":
            mess_spl, support = supp_checker(mess_spl)
            try:
                change_hp = int(mess_spl[3])
            except:
                change_hp = 0
            try:
                pl = item(pl_checker(message.author, support), int(mess_spl[1]), mess_spl[2], change_hp)
            except:
                error = True

            if error:
                text = er()
            else:
                text = ba(pl)

        # エネルギー セットコマンド
        if mess_spl[0] == "/energy" or mess_spl[0] == "/e":
            mess_spl, support = supp_checker(mess_spl)
            try:
                energy = int(mess_spl[3])
            except:
                energy = 1

            try:
                pl = set_energy(pl_checker(message.author, support), int(mess_spl[1]), mess_spl[2], energy)
            except:
                error = True

            if error:
                text = er()
            else:
                text = ba(pl)

        # エネルギー トラッシュコマンド
        if mess_spl[0] == "/trash" or mess_spl[0] == "/t":
            mess_spl, support = supp_checker(mess_spl)
            try:
                energy = int(mess_spl[3])
            except:
                energy = 1

            try:
                pl = trash_energy(pl_checker(message.author, support), int(mess_spl[1]), mess_spl[2], energy)
            except:
                error = 1

            if error:
                text = er()
            else:
                text = ba(pl)

        # 情報開示コマンド
        if mess_spl[0] == "/field" or mess_spl[0] == "/f":
            text = ""

            try:
                if  (mess_spl[1] == "1P") or (mess_spl[1] == "1p"):
                    pl = 0
                elif  (mess_spl[1]) == "2P" or (mess_spl[1] == "2p"):
                    pl = 1
                else:
                    int("無理やりエラー起こす")

            except:
                if message.author == player[0]:
                    pl = 1
                elif message.author == player[1]:
                    pl = 0
                else:
                    text += "GX:"
                    if GX[0]:
                        text += "使用済み\n"
                    else:
                        text += "未使用\n"
                    text += "残りサイド:" + str(SIDE[0]) +"枚\n" + ba(0) + "\n\n"

                    pl = 1

            text += "スタジアム:" + stadium + "\n"

            text += "GX:"
            if GX[pl]:
                text += "使用済み\n"
            else:
                text += "未使用\n"
            text += "残りサイド:" + str(SIDE[pl]) +"枚\n" + ba(pl)
            speak = True

        # 終了コマンド すべての値を初期値へ戻す
        if mess_spl[0] == "/finish":
            start = False
            player = [None,None]
            content = ""
            SIDE = [6,6]
            FIELD = [[None for j in range(6)] for i in range(2)]
            HP = [[65536 for j in range(6)] for i in range(2)]
            MAX_HP = [[65536 for j in range(6)] for i in range(2)]
            ITEM = [[None for j in range(6)] for i in range(2)]
            ENERGY = [[[None for k in range(0)] for j in range(6)] for i in range(2)]
            GX = [False, False]
            error = False
            hp = 65536
            energy = 1
            change_hp = 0
            stadium = "なし"

            text = "これで試合を終了します。お疲れさまでした。"
            speak = True

    if speak:
        await message.channel.send(text)
        speak = False

client.run(token)
