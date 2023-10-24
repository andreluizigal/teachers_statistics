import requests
import ssl
from bs4 import BeautifulSoup
import psycopg2
import re
from unidecode import unidecode

class TLSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

def verify_mandatory (session, course, matrix, discipline):

    response = session.get(f'https://si3.ufc.br/sigaa/public/curso/curriculo.jsf?lc=pt_BR&id={course}')

    soup = BeautifulSoup(response.text, 'html.parser')

    view_state = soup.find('input', {'id': 'javax.faces.ViewState'})['value']

    sufix = re.split(r'(Presencial - |A Distância - )', matrix)[-1]

    title = soup.find('td', string = sufix)

    id = title.find_next('a', title='Relatório da Estrutura Curricular').get('onclick').split('id,')[1].split("'")[0]

    data = {
        "j_id_jsp_1195785150_26": "j_id_jsp_1195785150_26",
        "j_id_jsp_1195785150_26:j_id_jsp_1195785150_37": "j_id_jsp_1195785150_26:j_id_jsp_1195785150_37",
        "javax.faces.ViewState": view_state,
        "id": id
    }

    response = session.post('https://www.si3.ufc.br/sigaa/public/curso/curriculo.jsf', data=data)

    soup = BeautifulSoup(response.text, 'html.parser')

    disciplines = soup.find_all('tr', class_='componentes')
    
    for d in disciplines:
        code = d.find('td').text.split(' - ')[0]
        if code == discipline:
            mandatory = d.find('i').text
            if mandatory == "Obrigatória": return True
            else: return False
    return False

ended = False
def main():
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
            cursor.execute("select name, siape from teachers where siape not in (select teacher_siape from teachers_classes) order by name")
            teachers = cursor.fetchall()

            cursor.execute("select id from classes")
            classes = cursor.fetchall()
            classes_ids = []
            for c in classes:
                classes_ids.append(c[0])

            # Controle de semestres
            semesters = [(2019, 1), (2019, 2), (2020, 1), (2020, 2), (2021, 1), (2021, 2), (2022, 1), (2022, 2), (2023, 1), (2023, 2)]

            # Controle graduação
            levels = ['G', '0']

            for t in teachers:
                print('\n######################################\nEntrando em:', t[0])

                query1 = 'INSERT INTO classes VALUES '
                query2 = 'INSERT INTO teachers_classes VALUES '
                query3 = 'INSERT INTO matrices_classes VALUES '

                for s in semesters:
                    print(f'\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\nSemestre: {s}')
                    teacher_classes_ids = []
                    for l in levels:
                        print(f'\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nGraduação: {l}')
                        if l == 'G':
                            data = {
                                "form": "form",
                                "form:checkNivel": "on",
                                "form:selectNivelTurma": l,
                                "form:checkAnoPeriodo": "on",
                                "form:inputAno": s[0],
                                "form:inputPeriodo": s[1],
                                "form:selectUnidade": 662,
                                "form:inputCodDisciplina": "",
                                "form:inputCodTurma": "",
                                "form:inputLocal": "",
                                "form:inputHorario": "",
                                "form:inputNomeDisciplina": "",
                                "form:checkDocente": "on",
                                "form:inputNomeDocente": t[0],
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
                        else:
                            data = {
                                "form": "form",
                                "form:selectNivelTurma": l,
                                "form:checkAnoPeriodo": "on",
                                "form:inputAno": s[0],
                                "form:inputPeriodo": s[1],
                                "form:selectUnidade": 662,
                                "form:inputCodDisciplina": "",
                                "form:inputCodTurma": "",
                                "form:inputLocal": "",
                                "form:inputHorario": "",
                                "form:inputNomeDisciplina": "",
                                "form:checkDocente": "on",
                                "form:inputNomeDocente": t[0],
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
                        print("Numero de turmas: ", len(classes))
                        for c in classes:
                            class_id = int(c.get('onclick').split('(')[1].split(')')[0])
                            
                            response = session.get(f"https://si3.ufc.br/sigaa/graduacao/turma/view_painel.jsf?ajaxRequest=true&contarMatriculados=true&id={class_id}&_dc=1694655927658")
                            
                            if response.status_code < 400:
                                soup = BeautifulSoup(response.text, 'html.parser')
                                
                                # Verificação se é o nome exato
                                teachers_table = soup.find('table', style='listagem')
                                teachers_table = teachers_table.find_all('tr')
                                
                                teachers_names = []
                                teachers_workload = []

                                for t1 in teachers_table:
                                    teachers_names.append(unidecode(t1.get_text().split(' (')[0].split('\t')[-1]))
                                    teachers_workload.append(t1.get_text().split(' (')[1].split('h)')[0])
                                
                                if t[0] not in teachers_names:
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

                                    try:
                                        place_schedule = soup.find('th', string='Local e Horário:').find_next('td').text
                                        
                                        place = re.split(r'(:3|:0)', place_schedule)[0][:-9].split('\t')[-1]

                                        schedule = re.split(r'(:3|:0)', place_schedule)[0][-6:] + ':' + re.split(r'(\d+:)', place_schedule, 1)[2].split('|(')[0]
                                    except:
                                        place = ""
                                        schedule = ""
                                    
                                    

                                    try:
                                        enrolled = soup.find('th', string='Totais:').find_next('td').text
                                        if 'matriculado' in enrolled: 
                                            enrolled = enrolled.split(' ')[-3][1:]
                                        else: enrolled = '0'
                                    except: enrolled = 0

                                    try:
                                        capacity = soup.find('th', string='Capacidade:').find_next('td').text.split(' a')[0]
                                    except: capacity = enrolled

                                    matrices = []

                                    next_matrices = soup.find('caption', string='Vagas Reservadas').find_next('tr')
                                    
                                    while next_matrices:
                                        matrix = next_matrices.find('td').text.rsplit(' - ', 1)[0]
                                        
                                        if matrix != "VAGAS SEM RESERVA" and matrix not in matrices:
                                            matrices.append(matrix)
                                            query3 += f"('{matrix}', {class_id}),"
                                        next_matrices = next_matrices.find_next('tr')
                                    
                                    mandatory = 'F'
                                    if l == 'G':
                                        for m in matrices:
                                            cursor.execute(f"select course_id from matrices where name = '{m}'")
                                            course = cursor.fetchone()

                                            if verify_mandatory(session, course[0], m, discipline_code):
                                                mandatory = 'T'
                                                break


                                    query1 += f"({class_id}, '{discipline_code}', '{discipline_name}', '{l}', '{mandatory}', {workload}, '{modality}', '{class_number}', '{semester}', '{place}', '{schedule}', {capacity}, {enrolled}),"

                                    classes_ids.append(class_id)

                                    print(f'professor: {t[0]} // semestre: {semester} // código: {discipline_code} // nome: {discipline_name} // graduação: {l} // obrigatória: {mandatory} //turma: {class_number} // carga: {workload} // local: {place} // horário: {schedule} // modalidade: {modality} // capacidade: {capacity} // matriculados: {enrolled} // curso:')


                                else:
                                    print("Turma já cadastrada")

                                if class_id not in teacher_classes_ids:
                                    teacher_workload = teachers_workload[teachers_names.index(t[0])]
                                    query2 += f"({t[1]}, {class_id}, {teacher_workload}),"
                                    teacher_classes_ids.append(class_id)

                            else: print(f"Não foi possivel acessar a turma: {class_id}")

                if query1 != 'INSERT INTO classes VALUES ': query1 = query1[:-1] + ";"
                else: query1 = ''
                if query2 != 'INSERT INTO teachers_classes VALUES ': query2 = query2[:-1] + ";"
                else: query2 = ''
                if query3 != 'INSERT INTO matrices_classes VALUES ': query3 = query3[:-1] + ";"
                else: query3 = ''

                query = query1 + query2 + query3

                if query != '':
                    cursor.execute(query)
                    connection.commit()
                    

                    print('Banco de dados atualizado.')
            else: print('O banco de dados está em dia com o SIGAA')




        else: print(f"A requisição falhou. Código: {response.status_code}")
    else: print(f"A requisição falhou. Código: {response.status_code}")

    cursor.close()
    connection.close()
    global ended
    ended = True
    print()

tryes = 0
while not ended:
    tryes +=1
    print(f"Tentativa nº {tryes}")
    try:
        main()
    except Exception as e:
        print(f"Erro ocorreu na tentativa {tryes}: {e}")