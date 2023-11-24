from config import dbname, user, password, host
from extraTeachers import extra_teachers
from modules import TLSAdapter
import requests
from bs4 import BeautifulSoup
import psycopg2
from unidecode import unidecode

# Controle departamentos
departments_groups = [[724, 747], [725, 739, 744], [726, 736], [728, 737, 740], [729, 738], [730], [731, 745], [732, 741], [765, 766]]

try:
    connection = psycopg2.connect(
        dbname=dbname, user=user, password=password, host=host
    )
    print("Conexão bem-sucedida ao banco de dados PostgreSQL!")

except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")

cursor = connection.cursor()
cursor.execute("SELECT id FROM departments")
departments_query = cursor.fetchall()
departments_ids = []
for d in departments_query:
    departments_ids.append(d[0])

cursor.execute("select siape from teachers")
teachers = cursor.fetchall()
teachers_siapes = []
for t in teachers:
    teachers_siapes.append(t[0])

session = requests.session()
session.mount('https://', TLSAdapter())


response = session.get('https://www.si3.ufc.br/sigaa/public/docente/busca_docentes.jsf?aba=p-academico')

soup = BeautifulSoup(response.text, 'html.parser')

query1 = "INSERT INTO departments VALUES "
query2 = "INSERT INTO teachers VALUES "

for group in departments_groups:
    if group[0] not in departments_ids:
        name = soup.find('option', {'value': group[0]}).get_text().split(' - FORTALEZA')[0].split('DEPARTAMENTO DE ')[1]
        query1 += f"({group[0]},'{name}'),"
    
    for d in group:
        
        view_state = soup.find('input', {'id': 'javax.faces.ViewState'})['value']
        search = {
            "form": "form",
            "form:nome": "",
            "form:departamento": d,
            "form:buscar": "Buscar",
            'javax.faces.ViewState': view_state 
        }

        response = session.post('https://www.si3.ufc.br/sigaa/public/docente/busca_docentes.jsf', data=search)

        soup = BeautifulSoup(response.text, 'html.parser')
        teachers = soup.find_all('tr', {'class': ['linhaPar', 'linhaImpar']})

        for t in teachers:
            t_siape = t.find('a')['href'].split('siape=')[1]
            if int(t_siape) not in teachers_siapes:
                t_name = unidecode(t.find('span', class_ = 'nome').get_text())
                query2 += f"({t_siape}, '{t_name}', {group[0]}),"
                teachers_siapes.append(int(t_siape))


# Professores Extras
for t in extra_teachers:
    if int(t[0]) not in teachers_siapes:
        query2 += f"({t[0]}, '{t[1]}', {t[2]}),"
        teachers_siapes.append(int(t[0]))


if query1 != "INSERT INTO departments VALUES ": query1 = query1[:-1] + ";"
else: query1 = ''
if query2 != "INSERT INTO teachers VALUES ": query2 = query2[:-1] + ";"
else: query2 = ''

query = query1 + query2

if query != '':
    cursor.execute(query)
    cursor.close()
    connection.commit()
    connection.close()
    print(f'O banco de dados foi atualizado.')
else: print(f'O banco de dados já estava em dia com o SIGAA.')




