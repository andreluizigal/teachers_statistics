from config import dbname, user, password, host
from modules import TLSAdapter
import requests
from bs4 import BeautifulSoup
import psycopg2
from unidecode import unidecode

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

cursor.execute("select siape from teachers")
teachers = cursor.fetchall()
teachers_siapes = []
for t in teachers:
    teachers_siapes.append(t[0])

session = requests.session()
session.mount('https://', TLSAdapter())

query = 'INSERT INTO teachers VALUES '

for department in departments:
    url = f'https://si3.ufc.br/sigaa/public/departamento/professores.jsf?id={department[0]}'

    response = session.get(url)
    if response.status_code < 400:
        soup = BeautifulSoup(response.text, 'html.parser')
        teachers = soup.find_all('td', class_='descricao')
        
        for teacher in teachers:
            siape = teacher.find('span', class_='pagina').a['href'].split("=")[-1]
            if int(siape) in teachers_siapes: continue
            name = unidecode(teacher.find('span', class_='nome').get_text(strip=True).split("\t")[0][:-1])
            query += f"({siape}, '{name}', {department[0]}),"
            # print(f"{siape}, {name}, {department[0]}")

    else: print(f"A requisição falhou. Código: {response.status_code}")


if query != 'INSERT INTO teachers VALUES ':
    query = query[:-1] + ";"

    cursor.execute(query)
    cursor.close()
    connection.commit()
    connection.close()
    print('O banco de dados foi atualizado.')
else: print('O banco de dados já está em dia com o SIGAA')




