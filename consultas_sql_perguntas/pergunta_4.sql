select replace(d.name, 'ENGENHARIA', 'ENG') departamento, avg(q.total) media
from departments d
join (select s.semester, s.department_id, count(*) total
	  from (
		select c.id::TEXT , c.semester, t.department_id, count(*) 
		from teachers t
		join teachers_classes tc
		on t.siape = tc.teacher_siape
		join classes c
		on tc.class_id = c.id
		where c.modality != 'A Distância' and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
		group by c.id, c.semester, t.department_id

		UNION ALL

		select c.discipline_name, c.semester, t.department_id, count(*)
		from teachers t
		join teachers_classes tc
		on t.siape = tc.teacher_siape
		join classes c
		on tc.class_id = c.id
		where c.modality = 'A Distância' and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
		group by c.discipline_name, t.siape, c.semester, t.department_id
	  ) s
	  group by s.semester, s.department_id
) q
on d.id = q.department_id
group by d.name
order by d.name 

-------------------------------

select avg(p.media)
from (
  select replace(substring(d.name, 9), 'ENGENHARIA', 'ENG') departamento, avg(q.total) media
  from departments d
  join (select s.semester, s.department_id, count(*) total
      from (
      select c.id::TEXT , c.semester, t.department_id, count(*) 
      from teachers t
      join teachers_classes tc
      on t.siape = tc.teacher_siape
      join classes c
      on tc.class_id = c.id
      where tc.teacher_workload > 0 and c.modality != 'A Distância' and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
      group by c.id, c.semester, t.department_id

      UNION ALL

      select c.discipline_name, c.semester, t.department_id, count(*)
      from teachers t
      join teachers_classes tc
      on t.siape = tc.teacher_siape
      join classes c
      on tc.class_id = c.id
      where c.modality = 'A Distância' and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
      group by c.discipline_name, t.siape, c.semester, t.department_id
      ) s
      group by s.semester, s.department_id
  ) q
  on d.id = q.department_id
  group by d.name
  order by d.name
) p 