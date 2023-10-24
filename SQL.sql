--drop table departments, teachers, classes, teachers_classes, courses_classes cascade
--drop table departments
CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

--drop table teachers
CREATE TABLE teachers (
    siape INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments (id)
);

--drop table classes
CREATE TABLE classes (
	id INTEGER,
    discipline_code VARCHAR(255),
    discipline_name VARCHAR(255),
	graduation CHAR,
	mandatory CHAR,
	workload INTEGER,
	modality VARCHAR(255),
	class_number VARCHAR(255),
	semester VARCHAR(255),
	place VARCHAR(255),
	schedule VARCHAR(255),
	capacity INTEGER,
	enroled INTEGER,
	
	PRIMARY KEY (id)
);

--drop table courses
CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

--drop table matrices
CREATE TABLE matrices (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
	course_id INTEGER,
	FOREIGN KEY (course_id) REFERENCES courses (id)
);

--drop table teachers_classes
CREATE TABLE teachers_classes (
	teacher_siape INTEGER,
	class_id INTEGER,
    teacher_workload INTEGER,

	PRIMARY KEY (teacher_siape, class_id),
	FOREIGN KEY (teacher_siape) REFERENCES teachers (siape)
);

--drop table matrices_classes
CREATE TABLE matrices_classes (
	matrix_name VARCHAR(255),
	class_id INTEGER,

	PRIMARY KEY (matrix_name, class_id),
	FOREIGN KEY (class_id) REFERENCES classes (id)
);

-- Verificar nomes iguais
select name, count(*) 
from teachers 
group by name
having count(*) > 1 

-- Verificar nomes que são subquerys de outros
SELECT name1, name2, COUNT(*) as total
FROM (
    SELECT t1.name as name1, t2.name as name2
    FROM teachers t1
    INNER JOIN teachers t2 ON t1.name LIKE CONCAT('%', t2.name, '%') AND t1.name != t2.name
) subquery
GROUP BY name1, name2
HAVING COUNT(*) = 1;


-- GRAFANA ------------------------------------------------------
select t.name, sum(teacher_workload) as "Total (Semestre)"
from teachers t 
join departments d 
on t.department_id = d.id 
join teachers_classes tc
on t.siape = tc.teacher_siape
where d.name = '$department'
group by t.name
order by t.name asc

--
select sum(c.capacity) - sum(c.enroled) "Vagas Livres", sum(c.enroled) "Matriculados"
from classes c
join teachers_classes tc on c.id = tc.class_id
join teachers t on tc.teacher_siape = t.siape
join departments d on t.department_id = d.id
where d.name = '$department'

--
select cc.course, count(*) as "Quantidade Turmas"
from courses_classes cc
join classes c on cc.class_id = c.id
join teachers_classes tc on c.id = tc.class_id
join teachers t on tc.teacher_siape = t.siape
join departments d on t.department_id = d.id
where d.name = '$department'

group by cc.course
order by "Quantidade Turmas" desc

--
select concat(c.discipline_name, ' - T', c.class_number) "Turma", c.enroled "Alunos"
from classes c
join teachers_classes tc on c.id = tc.class_id
join teachers t on tc.teacher_siape = t.siape
where t.name = '$teacher'
ORDER BY "Turma" asc

--
select c.discipline_name, count(*) "Quantidade"
from classes c
join teachers_classes tc on c.id = tc.class_id
join teachers t on tc.teacher_siape = t.siape
where t.name = '$teacher' 
group by c.discipline_name
order by c.discipline_name asc