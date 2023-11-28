select q.semester, avg(q.soma) media
from (select t.siape, c.semester, sum(tc.teacher_workload) soma
	  from teachers t
	  join teachers_classes tc
	  on t.siape = tc.teacher_siape
	  join classes c
	  on tc.class_id = c.id
	  where t.department_id in ($department) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
	  group by t.siape, c.semester
	 ) q
group by q.semester
order by q.semester

---------------------------------

select avg(t.soma) media
from (select t.siape, sum(tc.teacher_workload) soma
      from teachers t
      join teachers_classes tc
      on t.siape = teacher_siape
      join classes c
      on tc.class_id = c.id
      where t.department_id in ($department) 
      and c.semester in ($semester) 
      and c.graduation in ($level) 
      and c.mandatory in ($mandatory)
      group by t.siape, c.semester
) t