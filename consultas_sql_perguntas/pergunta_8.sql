select t.name, avg(q.soma)
from teachers t
join (select t.siape, sum(c.enroled) soma
	  from teachers t
	  join teachers_classes tc
	  on t.siape = tc.teacher_siape
	  join classes c
	  on tc.class_id = c.id
	  where t.department_id in ($department) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
	  group by t.siape, c.semester
) q
on t.siape = q.siape
group by t.name
order by t.name