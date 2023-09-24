import requests
import ssl
from bs4 import BeautifulSoup
import psycopg2
import re

dbname = "departaments"
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

class TLSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

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

        response = session.get("https://si3.ufc.br/sigaa/ensino/turma/busca_turma.jsf")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        view_state = soup.find('input', {'id': 'javax.faces.ViewState'})['value']

        cursor = connection.cursor()
        cursor.execute("SELECT name, siape FROM teachers where department_id in (765, 724)")
        # cursor.execute("SELECT name, siape FROM teachers where name = 'MARIA DE FATIMA OLIVEIRA'")
        teachers = cursor.fetchall()

        cursor.execute("select id from classes")
        classes = cursor.fetchall()
        classes_ids = []
        for c in classes:
            classes_ids.append(c[0])

        

        query1 = 'INSERT INTO classes VALUES '
        query2 = 'INSERT INTO teachers_classes VALUES '
        query3 = 'INSERT INTO courses_classes VALUES '



        for teacher in teachers:
            print('\n************************************************\nEntrando em:', teacher[0])
            data = {
                "form": "form",
                "form:selectNivelTurma": "0",
                "form:checkAnoPeriodo": "on",
                "form:inputAno": 2023,
                "form:inputPeriodo": 2,
                "form:selectUnidade": 662,
                "form:inputCodDisciplina": "",
                "form:inputCodTurma": "",
                "form:inputLocal": "",
                "form:inputHorario": "",
                "form:inputNomeDisciplina": "",
                "form:checkDocente": "on",
                "form:inputNomeDocente": teacher[0],
                "form:selectCurso": 0,
                "form:selectPolo": 0,
                "form:selectSituacaoTurma": -1,
                "form:selectTipoTurma": 0,
                "form:selectModalidadeComponente": 0,
                "form:selectOpcaoOrdenacao": 1,
                "turmasEAD": "false",
                "form:buttonBuscar": "Buscar",
                "javax.faces.ViewState": view_state
            }

            cookies = response.cookies
            response = session.post("https://si3.ufc.br/sigaa/ensino/turma/busca_turma.jsf", data=data, cookies=cookies)

            
            soup = BeautifulSoup(response.text, 'html.parser')
            view_state = soup.find('input', {'id': 'javax.faces.ViewState'})['value']

            classes = soup.findAll('a', title='Ver Detalhes dessa turma')

            print("Número de turmas:", len(classes))

            for c in classes:
                class_id = c.get('onclick').split('(')[1].split(')')[0]
                
                response = session.get(f"https://si3.ufc.br/sigaa/graduacao/turma/view_painel.jsf?ajaxRequest=true&contarMatriculados=true&id={class_id}&_dc=1694655927658")
                
                if response.status_code < 400:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Verificação se é o nome exato
                    teachers_table = soup.find('table', style='listagem')
                    teachers_table = teachers_table.find_all('tr')
                    
                    teachers_names = []
                    teachers_workload = []

                    for t in teachers_table:
                        teachers_names.append(t.get_text().split(' (')[0].split('\t')[-1])
                        teachers_workload.append(t.get_text().split(' (')[1].split('h)')[0])

                    if teacher[0] not in teachers_names:
                        continue
                    #

                    print('----------------------------------------------')

                    if class_id not in classes_ids:

                        semester = soup.find('th', string=' Ano/Período: ').find_next('td').text

                        discipline = soup.find('th', string='Componente e Turma:').find_next('td').text.split('Turma ')

                        class_number = discipline[-1]
                        
                        discipline_code = discipline[0].split(' - ')[0]

                        discipline_name = discipline[0].split(' - ', 1)[1][:-3]

                        modality = soup.find('th', string='Modalidade de Ensino da Disciplina:').find_next('td').text

                        workload = soup.find('th', string='Créditos / Carga Horária:').find_next('td').text.split(' / ')[1].split(' horas')[0]

                        place_schedule = soup.find('th', string='Local e Horário:').find_next('td').text
                        
                        place = re.split(r'(:3|:0)', place_schedule)[0][:-9].split('\t')[-1]

                        schedule = re.split(r'(:3|:0)', place_schedule)[0][-6:] + ':' + re.split(r'(\d+:)', place_schedule, 1)[2].split('|(')[0]

                        capacity = soup.find('th', string='Capacidade:').find_next('td').text.split(' a')[0]

                        try:
                            enrolled = soup.find('th', string='Totais:').find_next('td').text.split(' ')[-3][1:]
                        except: enrolled = 0

                        courses = []

                        next_courses = soup.find('caption', string='Vagas Reservadas').find_next('tr')
                        
                        while next_courses:
                            course = next_courses.find('td').text.rsplit(' - ', 1)[0]
                            
                            if course != "VAGAS SEM RESERVA" and course not in courses:
                                courses.append(course)
                                query3 += f"('{course}', {class_id}),"

                            next_courses = next_courses.find_next('tr')
                            

                        query1 += f"({class_id}, '{discipline_code}', '{discipline_name}', {workload}, '{modality}', '{class_number}', '{semester}', '{place}', '{schedule}', {capacity}, {enrolled}),"

                        classes_ids.append(class_id)

                        print(f'professor: {teacher[0]} // semestre: {semester} // código: {discipline_code} // nome: {discipline_name} // turma: {class_number} // carga: {workload} // local: {place} // horário: {schedule} // modalidade: {modality} // capacidade: {capacity} // matriculados: {enrolled} // curso:')

                    teacher_workload = teachers_workload[teachers_names.index(teacher[0])]
                    
                    query2 += f"({teacher[1]}, {class_id}, {teacher_workload}),"

                else: print(f"Não foi possivel acessar a turma: {class_id}")


        query1 = query1[:-1] + ";"
        query2 = query2[:-1] + ";"
        query3 = query3[:-1] + ";"

        query = query1 + query2 + query3

        print(query3)


        cursor.execute(query)
        cursor.close()
        connection.commit()
        connection.close()

        print("query executada")




    else:
        print(f"A requisição falhou. Código: {response.status_code}")


else:
    print(f"A requisição falhou. Código: {response.status_code}")



