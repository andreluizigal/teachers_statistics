select replace(d.name, 'ENGENHARIA', 'ENG') departamento, avg(t.soma) media
from departments d
join (select t.name, t.department_id, sum(tc.teacher_workload) soma
	  from teachers t
	  join teachers_classes tc
	  on t.siape = tc.teacher_siape
	  join classes c
	  on tc.class_id = c.id
	  where c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
	  group by t.name, t.department_id, c.semester
	 ) t
on d.id = t.department_id
group by d.name
order by d.name

--------------------------------------------

select avg(p.media)
from (
  select replace(substring(d.name, 9), 'ENGENHARIA', 'ENG') departamento, avg(t.soma) media
  from departments d
  join (select t.name, t.department_id, sum(tc.teacher_workload) soma
      from teachers t
      join teachers_classes tc
      on t.siape = tc.teacher_siape
      join classes c
      on tc.class_id = c.id
      where c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
      group by t.name, t.department_id, c.semester
    ) t
  on d.id = t.department_id
  group by d.name
  order by d.name
) p