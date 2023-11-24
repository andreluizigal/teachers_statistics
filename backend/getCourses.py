from config import dbname, user, password, host
import requests
from modules import TLSAdapter, login_sigaa
from bs4 import BeautifulSoup
import psycopg2
import getpass

try:
    connection = psycopg2.connect(
        dbname=dbname, user=user, password=password, host=host
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

while True:
    login_user = input('Digite seu usuário do SIGAA: ')
    login_password = getpass.getpass('Digite sua senha do SIGAA: ')
    login_role = input('Tipos de vínculo:\n1 - Discente\n2 - Docente\nDigite o número: ')
    if login_role not in ['1', '2']: continue
    if login_sigaa(session, login_user, login_password, login_role): break

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

    print('O banco de dados foi atualizado.')
else: print('O banco de dados já está em dia com o SIGAA')