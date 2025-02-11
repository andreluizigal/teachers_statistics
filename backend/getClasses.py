from config import dbname, user, password, host
from modules import TLSAdapter, login_sigaa
import requests
from bs4 import BeautifulSoup
import psycopg2
import re
from unidecode import unidecode
import traceback
from datetime import datetime
import getpass


def verify_mandatory (session, discipline):
    type = 2
    while True:
        response = session.get('https://www.si3.ufc.br/sigaa/public/componentes/busca_componentes.jsf')

        soup = BeautifulSoup(response.text, 'html.parser')

        view_state = soup.find('input', {'id': 'javax.faces.ViewState'})['value']

        data = {
            "form": "form",
            "form:checkNivel": "on",
            "form:nivel": "G",
            "form:checkTipo": "on",
            "form:tipo": type,
            "form:checkCodigo": "on",
            "form:j_id_jsp_541340994_12": discipline,
            "form:j_id_jsp_541340994_14": '',
            "form:unidades": 0,
            "form:j_id_jsp_541340994_19": "Buscar Componentes",
            "javax.faces.ViewState": view_state
        }

        response = session.post('https://www.si3.ufc.br/sigaa/public/componentes/busca_componentes.jsf', data=data)

        soup = BeautifulSoup(response.text, 'html.parser')

        view_state = soup.find('input', {'id': 'javax.faces.ViewState'})['value']

        try:
            id = soup.find('a', title="Visualizar Detalhes do Componente Curricular").get('onclick').split('id,')[1].split(",")[0]
        except: 
            print("ATIVIDADE")
            return 'Activity'

        data = {
            "j_id_jsp_541340994_22": "j_id_jsp_541340994_22",
            "javax.faces.ViewState": view_state,
            "j_id_jsp_541340994_22:j_id_jsp_541340994_23": "j_id_jsp_541340994_22:j_id_jsp_541340994_23",
            "id": id,
            "publico": "public"
        }

        response = session.post('https://www.si3.ufc.br/sigaa/public/componentes/busca_componentes.jsf', data=data)

        soup = BeautifulSoup(response.text, 'html.parser')

        matrices = soup.find_all('tr', {'class': ['linhaPar', 'linhaImpar']})

        for m in matrices:
            active = m.find('td', class_='colAtivo').get_text()
            if active == 'Sim':
                mandatory = m.find('td', class_='colObg').get_text()
                if mandatory == 'Sim': return True
        return False

def main():
    
    try:
        connection = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host
        )
        print("Conexão bem-sucedida ao banco de dados PostgreSQL!")

    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")

    
    # Controle de semestres
    semesters = []
    for i in range(2):
        if len(semesters) >= 10: break
        if i == 0:
            if datetime.now().month >= 6:
                semesters.append((datetime.now().year - i, 2))
        else: semesters.append((datetime.now().year - i, 2))
        semesters.append((datetime.now().year - i, 1))
    
    # semesters = [(2021, 2)]
    

    # Controle nível de graduação
    levels = ['G', 'S']

    cursor = connection.cursor()
    cursor.execute("select siape, name from teachers where siape not in (select teacher_siape from teachers_classes tc join classes c on tc.class_id = c.id where c.semester in (select case when extract(month from current_date) <= 6 then concat(extract(year from current_date), '.1') else concat(extract(year from current_date), '.2') end as anosemestre)) order by name")
    teachers = cursor.fetchall()

    cursor.execute("select id from classes")
    classes = cursor.fetchall()
    classes_ids = []
    for c in classes:
        classes_ids.append(c[0])

    cursor.execute("select teacher_siape, class_id from teachers_classes")
    teacher_classes = cursor.fetchall()

    

    session = requests.session()
    session.mount('https://', TLSAdapter())

    global login_user
    global login_password
    global login_role
    
    while True:
        if not login_user or not login_password or not login_role:
            login_user = input('Digite seu usuário do SIGAA: ')
            login_password = getpass.getpass('Digite sua senha do SIGAA: ')
            login_role = input('Tipos de vínculo:\n1 - Discente\n2 - Docente\nDigite o número: ')
            if login_role not in ['1', '2']: continue
        if login_sigaa(session, login_user, login_password, login_role): break

    response = session.get("https://si3.ufc.br/sigaa/ensino/turma/busca_turma.jsf")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    view_state = soup.find('input', {'id': 'javax.faces.ViewState'})['value']

    mandatories = []
    optionals = []
    for t in teachers:
        print('\n######################################\nEntrando em:', t[1])

        query1 = 'INSERT INTO classes VALUES '
        query2 = 'INSERT INTO teachers_classes VALUES '
        query3 = 'INSERT INTO matrices_classes VALUES '

        for s in semesters:
            print(f'\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\nSemestre: {s}')
            for l in levels:
                print(f'\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nGraduação: {l}')

                s_concat = f'{s[0]}' + '.' + f'{s[1]}'
                cursor.execute(f"select distinct c.discipline_code from classes c join teachers_classes tc on c.id = tc.class_id where tc.teacher_siape = {t[0]} and c.semester = '{s_concat}' and c.modality = 'A Distância'")
                remote_disciplines = cursor.fetchall()

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
                    "form:inputNomeDocente": t[1],
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

                classes = soup.find_all('a', title='Ver Detalhes dessa turma')
                print("Numero de turmas: ", len(classes))
                for c in classes:
                    class_id = int(c.get('onclick').split('(')[1].split(')')[0])
                    
                    response = session.get(f"https://si3.ufc.br/sigaa/graduacao/turma/view_painel.jsf?ajaxRequest=true&contarMatriculados=true&id={class_id}&_dc=1694655927658")
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    teachers_table = soup.find('table', style='listagem')
                    teachers_table = teachers_table.find_all('tr')
                    
                    teachers_names = []
                    teachers_workload = []

                    for t1 in teachers_table:
                        teachers_names.append(unidecode(t1.get_text().split(' (')[0].split('\t')[-1]))
                        teachers_workload.append(t1.get_text().split(' (')[1].split('h)')[0])

                    # Verificação se é o nome exato
                    if t[1] not in teachers_names:
                        continue
                    #

                    print('----------------------------------------------')

                    modality = soup.find('th', string='Modalidade de Ensino da Disciplina:').find_next('td').text

                    discipline = soup.find('th', string='Componente e Turma:').find_next('td').text.split('Turma ')

                    class_number = discipline[-1]
                    discipline_code = discipline[0].split(' - ')[0]
                    discipline_name = discipline[0].split(' - ', 1)[1][:-3]

                    if class_id not in classes_ids:

                        mandatory = 'F'
                        if l == 'G':
                            if discipline_code in mandatories: mandatory = 'T'
                            elif discipline_code in optionals: mandatory = 'F'
                            else:
                                verify = verify_mandatory(session, discipline_code)
                                if verify == 'Activity':
                                    continue
                                elif verify:
                                        mandatory = 'T'
                                        mandatories.append(discipline_code)
                                else: optionals.append(discipline_code)
                        else: mandatory = 'T'

                        semester = soup.find('th', string=' Ano/Período: ').find_next('td').text

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


                        query1 += f"({class_id}, '{discipline_code}', '{discipline_name}', '{l}', '{mandatory}', {workload}, '{modality}', '{class_number}', '{semester}', '{place}', '{schedule}', {capacity}, {enrolled}),"

                        classes_ids.append(class_id)

                        print(f'professor: {t[1]} // semestre: {semester} // código: {discipline_code} // nome: {discipline_name} // graduação: {l} // obrigatória: {mandatory} //turma: {class_number} // carga: {workload} // local: {place} // horário: {schedule} // modalidade: {modality} // capacidade: {capacity} // matriculados: {enrolled} // curso:')


                    else:
                        print("Turma já cadastrada")

                    if (t[0],class_id) not in teacher_classes:
                        teacher_workload = teachers_workload[teachers_names.index(t[1])]

                        if modality == 'A Distância':
                            if (discipline_code,) in remote_disciplines:
                                teacher_workload = 0
                                print("Remota já cadastrada")
                                print(remote_disciplines)
                            else: 
                                remote_disciplines.append((discipline_code,))
                                print("Remota primeira vez")
                                print(remote_disciplines)

                        query2 += f"({t[0]}, {class_id}, {teacher_workload}),"
                        teacher_classes.append((t[0],class_id))

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
            print(f'O banco de dados foi atualizado em relação a {t[1]}.')
        else: print(f'O banco de dados já está em dia com o SIGAA em relação a {t[1]}')


    cursor.close()
    connection.close()
    global ended
    ended = True

ended = False
tryes = 0

login_user = ''
login_password = ''
login_role = ''

while not ended:
    tryes +=1
    print(f"Tentativa nº {tryes}")
    try:
        main()
    except Exception as e:
        print(f"Erro ocorreu na tentativa {tryes}: {e}")
        traceback.print_exc()
        
print(f'Execução encerrada após {tryes} tentativas.')