from config import dbname, user, password, host
from modules import TLSAdapter
import requests
from bs4 import BeautifulSoup
import psycopg2

try:
    connection = psycopg2.connect(
        dbname=dbname, user=user, password=password, host=host
    )
    print("Conexão bem-sucedida ao banco de dados PostgreSQL!")

except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")

cursor = connection.cursor()
cursor.execute("SELECT id FROM departments")
departments = cursor.fetchall()
departments_ids = []
for d in departments:
    departments_ids.append(d[0])

session = requests.session()
session.mount('https://', TLSAdapter())

url = 'https://si3.ufc.br/sigaa/public/departamento/lista.jsf'

response = session.get(url)

if response.status_code < 400:

    soup = BeautifulSoup(response.text, 'html.parser')

    view_state = soup.find('input', {'id': 'javax.faces.ViewState'})['value']

    search = {
        'form': 'form',
        'form:programas': 0,
        'form:buscar': 'Buscar',
        'javax.faces.ViewState': view_state
        
    }

    response = session.post(url, data=search)
    if response.status_code < 400:
        soup = BeautifulSoup(response.text, 'html.parser')

        table = soup.find('table', class_='listagem').find_all('tr', class_=True)
        query = "INSERT INTO departments (id, name) VALUES "

        for department in table:
            id = department.a['href'].split("=")[2]
            if int(id) in departments_ids: continue
            name = department.a.get_text(strip=True)

            # Controle de departamentos utilizados
            if int(id) in [724, 725, 726, 728, 729, 730, 731, 732]:
                query += f"({id},'{name}'),"
        
        if query != "INSERT INTO departments (id, name) VALUES ":
            query = query[:-1] + ";"
            
            cursor = connection.cursor()
            cursor.execute(query)
            cursor.close()
            connection.commit()
            connection.close()

            print('O banco de dados foi atualizado.')
        else: print('O banco de dados já está em dia com o SIGAA')
     
    else: print(f"A requisição falhou. Código: {response.status_code}")
else: print(f"A requisição falhou. Código: {response.status_code}")



