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

--drop table teachers_classes
CREATE TABLE teachers_classes (
	teacher_siape INTEGER,
	class_id INTEGER,
    teacher_workload INTEGER

	PRIMARY KEY (teacher_siape, class_id)
	FOREIGN KEY (siape) REFERENCES teachers (siape)
);

--drop table courses_classes
CREATE TABLE courses_classes (
	course VARCHAR(255),
	class_id INTEGER,

	PRIMARY KEY (course, class_id),
	FOREIGN KEY (class_id) REFERENCES classes (id)
);



-- Verificar nomes que são subquerys de outros
SELECT name1, name2, COUNT(*) as total
FROM (
    SELECT t1.name as name1, t2.name as name2
    FROM teachers t1
    INNER JOIN teachers t2 ON t1.name LIKE CONCAT('%', t2.name, '%') AND t1.name != t2.name
) subquery
GROUP BY name1, name2
HAVING COUNT(*) = 1;