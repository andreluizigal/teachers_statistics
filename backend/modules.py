import ssl
import requests
import getpass

class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)
    
def login_sigaa (session):
    url = 'https://si3.ufc.br/sigaa/logar.do?dispatch=logOn'
    response = session.get(url)
    while True:
        cookies = response.cookies

        user = input('Digite seu usuário do SIGAA: ')
        password = getpass.getpass('Digite sua senha do SIGAA: ')

        login_data = {
        "user.login": user,
        "user.senha": password
        }

        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Length": "101",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": f"{cookies}",
            "Host": "si3.ufc.br",
            "Origin": "https://si3.ufc.br",
            "Referer": "https://si3.ufc.br/sigaa/logar.do?dispatch=logOff",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "sec-ch-ua": "'Chromium';v='116', 'Not)A;Brand';v='24', 'Google Chrome';v='116'",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
        }

        response = session.post(url, data=login_data, cookies=cookies, headers=headers)

        if 'Usuário e/ou senha inválidos' in response.text: 
            print('Login inválido')
            continue
        try: response = session.get("https://si3.ufc.br/sigaa/escolhaVinculo.do?dispatch=escolher&vinculo=1")
        except: print('Apenas 1 vínculo')

        response = session.get("https://si3.ufc.br/sigaa/paginaInicial.do")
        response = session.get("https://si3.ufc.br/sigaa/verPortalDiscente.do")
        return