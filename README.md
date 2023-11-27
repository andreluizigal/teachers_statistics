# Projeto de Otimização da Análise de Dados Acadêmicos - UFC

## Descrição do Projeto

Este projeto visa desenvolver uma aplicação para otimizar a análise de dados acadêmicos na Universidade Federal do Ceará (UFC). A aplicação realiza a coleta de dados de departamentos, docentes e turmas diretamente do portal [SIGAA da UFC](https://si3.ufc.br/sigaa/public), armazena esses dados em um banco de dados PostgreSQL e fornece recursos avançados de análise estatística e geração de gráficos através do Grafana.

## Conteúdo do Repositório

- **backend**: Contém os scripts desenvolvidos para realizar o Web Scraping no portal SIGAA.
  
- **docker-compose.yml**: Arquivo de configuração dos containers.

## Pré-requisitos

- Docker
- Docker Compose

## Instalação

1. Clone este repositório: `git clone https://github.com/andreluizigal/teachers_statistics.git`
2. Suba os containers com Docker Compose: `docker-compose up --build -d`
3. Acesse a Aplicação em [localhost:3000](localhost:3000)
4. (OPCIONAL) Excluir container da aplicação: `docker-compose down -v`

## Atualização do Banco de Dados

1. Execute comando: `docker ps -a`
2. Verifique o ID do container 'grafana_container' e execute o comando `docker exec -it <id_do_contêiner> /bin/bash`.
3. Execute `ls` para verificar os scripts disponíveis
4. Execute os scripts na ordem: `python <script.py>` (getDepartments.py > getCourses.py > getClasses.py)

## Inclusão de Departamentos
1. Acesse a página [Docentes da UFC](https://si3.ufc.br/sigaa/public/docente/busca_docentes.jsf)
2. Inspecione o input do campo 'Departamento' do formulário de busca (Botão direito do mouse > Inspecionar)
3. Expanda a tag HTML &lt;select&gt;
4. Verifique cada &lt;option&gt; dos departamentos e seus subgrupos que deseje incluir e anote o atributo 'value' deles
5. Abra o arquivo [backend/getDepartments.py](backend/getDepartments.py) em seu editor de preferência
6. Abaixo da linha onde há o comentário 'Controle departamentos', crie novos grupos de departamentos incluindo arrays dentro do array principal no formato \[id_departamento, id_subgrupo_1, id_subgrupo_2, ...\]
7. Salve as alterações, suba os containers novamente e execute os scripts para [Atualização do Banco de Dados](#atualização-do-banco-de-dados)

## Inclusão de Docentes Ausentes
1. Acesse a página [Docentes da UFC](https://si3.ufc.br/sigaa/public/docente/busca_docentes.jsf)
2. Busque pelo nome do docente desejado
3. Anote o nome do docente como aparece no resultado da busca
3. Copie o endereço do link 'ver página pública' do docente encontrado (Botão direito do mouse > Copiar endereço do link)
4. Remova a parte inicial do endereço, e anote apenas o código de sua siape, após '...siape='
5. Abra o arquivo [backend/extraTeachers.py](backend/extraTeachers.py) em seu editor de preferência
6. Adicione o docente no array no formato (siape, nome, id_departamento)
7. Salve as alterações, suba os containers novamente e execute os scripts para [Atualização do Banco de Dados](#atualização-do-banco-de-dados)
