select q.discipline_name, count(*)
from (
	select c.id::TEXT, c.discipline_name, count(*)
	from teachers t
	join teachers_classes tc
	on t.siape = tc.teacher_siape
	join classes c
	on tc.class_id = c.id
	where tc.teacher_workload > 0 and t.department_id in ($department) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory) and c.modality not in ('A Distância')
	group by c.id, c.discipline_name
	
	UNION ALL
	select c.semester, c.discipline_name, count(*)
	from teachers t
	join teachers_classes tc
	on t.siape = tc.teacher_siape
	join classes c
	on tc.class_id = c.id
	where t.department_id in ($department) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory) and c.modality in ('A Distância')
	group by c.semester, tc.teacher_siape, c.discipline_name
) q
group by q.discipline_name
order by count desc

