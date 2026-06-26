cat > /root/agent2.py << 'ENDOFFILE'
import anthropic
import urllib.request, urllib.parse, json, time

CLIENT_ID = "mSDgjGmCZziVZHk2EtqX"
CLIENT_SECRET = "r0Vwf5VSMLB3aPqTYkARZ9hadcAs4SwrGYY0HtnX"
client = anthropic.Anthropic(api_key="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")

SCENARIO = """Ty menedzher po prodazham stellazhej GARANT-STELLAG. Otvechaj TOLKO na russkom yazyke. KATALOG: LAYT STO 60-120kg. LF 180-220kg. SGRF 300kg. SGR OTs 350-550kg. STSENARIY: 1-Privetstvie 2-Utochni razmery 3-Nagruzku 4-Kol-vo polok 5-Tsena i dostavka. VOZRAZHENIYA: Dorogo-sprosi byudzhet. Podumayu-zafiksiruy tsenu na 3 dnya. Deshevle-metall 2mm garantiya 1 god. Pri torge ili prosby skidki otvechaj: Peredayu vas menedzheru, on svyazhetsya s vami. ADRESA: Moskva 1y Rizhskiy per 2G. Samovyvoz PSK Sergeevo g.Chekhov. Dostavka 1-2 dnya. DOVERIE: s 2015 goda, 3000+ klientov, garantiya 1 god, oplata posle polucheniya. Pravila: kratko, odin vopros za raz."""

def get_token():
    data = urllib.parse.urlencode({"grant_type":"client_credentials","client_id":CLIENT_ID,"client_secret":CLIENT_SECRET,"scope":"messenger:read messenger:write"}).encode()
    with urllib.request.urlopen(urllib.request.Request("https://api.avito.ru/token",data=data,method="POST")) as r:
        return json.loads(r.read())["access_token"]

def get_uid(token):
    with urllib.request.urlopen(urllib.request.Request("https://api.avito.ru/core/v1/accounts/self",headers={"Authorization":f"Bearer {token}"})) as r:
        return json.loads(r.read())["id"]

def get_chats(token,uid):
    try:
        with urllib.request.urlopen(urllib.request.Request(f"https://api.avito.ru/messenger/v2/accounts/{uid}/chats?unread_only=false&chat_types=u2i",headers={"Authorization":f"Bearer {token}"})) as r:
            return json.loads(r.read()).get("chats",[])
    except Exception as e:
        print(f"get_chats error: {e}")
        return []

def get_msgs(token,uid,cid):
    try:
        with urllib.request.urlopen(urllib.request.Request(f"https://api.avito.ru/messenger/v3/accounts/{uid}/chats/{cid}/messages/",headers={"Authorization":f"Bearer {token}"})) as r:
            data = json.loads(r.read())
            print(f"msgs type: {type(data)}, keys: {list(data.keys()) if isinstance(data,dict) else 'list'}")
            if isinstance(data, list):
                return data
            return data.get("messages", data.get("items", []))
    except Exception as e:
        print(f"get_msgs error: {e}")
        return []

def send(token,uid,cid,text):
    data=json.dumps({"message":{"text":text},"type":"text"}).encode()
    urllib.request.urlopen(urllib.request.Request(f"https://api.avito.ru/messenger/v1/accounts/{uid}/chats/{cid}/messages",data=data,method="POST",headers={"Authorization":f"Bearer {token}","Content-Type":"application/json"}))

def reply(msgs,text):
    hist=[]
    for m in msgs:
        if m.get("type")=="text" and m.get("content",{}).get("text",""):
            hist.append({"role":"user" if m["direction"]=="in" else "assistant","content":m["content"]["text"]})
    hist.append({"role":"user","content":text})
    return client.messages.create(model="claude-sonnet-4-6",max_tokens=512,system=SCENARIO,messages=hist).content[0].text

def run():
    try:
        token=get_token()
        uid=get_uid(token)
        chats=get_chats(token,uid)
        if chats: print(f"Chatov: {len(chats)}")
        for chat in chats:
            msgs=get_msgs(token,uid,chat["id"])
            if not msgs: continue
