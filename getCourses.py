import requests
import ssl
from bs4 import BeautifulSoup
import psycopg2
import re

class TLSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)
    
dbname = "departments"
user = "postgres"
password = "1234"
host = "localhost"  
port = "5432" 

try:
    connection = psycopg2.connect(
        dbname=dbname, user=user, password=password, host=host, port=port
    )
    print("Conexão bem-sucedida ao banco de dados PostgreSQL!")

except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")


cursor = connection.cursor()

cursor.execute("select id from courses")
courses = cursor.fetchall()
courses_ids = []
for c in courses:
    courses_ids.append(c[0])

cursor.execute("select id from matrices")
matrices = cursor.fetchall()
matrices_ids = []
for m in matrices:
    matrices_ids.append(m[0])

query1 = 'INSERT INTO courses VALUES '
query2 = 'INSERT INTO matrices VALUES '

session = requests.session()
session.mount('https://', TLSAdapter())

url = 'https://si3.ufc.br/sigaa/logar.do?dispatch=logOn'

response = session.get(url)

if response.status_code < 400:
    cookies = response.cookies

    login_data = {
    "user.login": "andref190",
    "user.senha": "Dedekitas!23"
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

    if response.status_code < 400:

        response = session.get("https://si3.ufc.br/sigaa/escolhaVinculo.do?dispatch=escolher&vinculo=2")

        response = session.get("https://si3.ufc.br/sigaa/paginaInicial.do")

        response = session.get("https://si3.ufc.br/sigaa/verPortalDiscente.do")

        response = session.get("https://si3.ufc.br/sigaa/graduacao/matriz_curricular/lista.jsf")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        view_state = soup.find('input', {'id': 'javax.faces.ViewState'})['value']

        courses = soup.find_all('option')

        for c in courses[1:]:
            c_id = int(c.get('value'))
            if c_id not in courses_ids:
                name = c.text
                query1 += f"({c_id},'{name}'),"
            
            data = {
                "busca": "busca",
                "paramBusca": "curso",
                "busca:curso": c_id,
                "busca:j_id_jsp_32707105_202": "Buscar",
                "javax.faces.ViewState": view_state
            }

            cookies = response.cookies
            response = session.post("https://si3.ufc.br/sigaa/graduacao/matriz_curricular/lista.jsf", data=data, cookies=cookies)

            soup = BeautifulSoup(response.text, 'html.parser')
            
            matrices = soup.find_all('tr', {'class': ['linhaPar', 'linhaImpar']})

            for m in matrices:
                m_id = m.find('input', {'name': 'id'}).get('value')
                if int(m_id) not in matrices_ids:
                    m_name = m.find('td').text
                    query2 += f"({m_id},'{m_name}', {c_id}),"

        if query1 != 'INSERT INTO courses VALUES ': query1 = query1[:-1] + ";"
        else: query1 = ''
        if query2 != 'INSERT INTO matrices VALUES ': query2 = query2[:-1] + ";"
        else: query2 = ''

        query = query1 + query2

        if query != '':
            cursor.execute(query)
            cursor.close()
            connection.commit()
            connection.close()

            print('Banco de dados atualizado.')
        else: print('O banco de dados está em dia com o SIGAA')

    else: print(f"A requisição falhou. Código: {response.status_code}")
else: print(f"A requisição falhou. Código: {response.status_code}")









        