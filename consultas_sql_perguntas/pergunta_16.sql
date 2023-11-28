select '(' || sum(q.qnt) || ')' || ' ' || q.discipline_name, sum(q.total) / (case when sum(q.qnt) > 0 then sum(q.qnt) else 1 end) as media
from(select count(*) qnt, c.discipline_name, sum(c.enroled) total
	from teachers_classes tc
	join classes c
	on tc.class_id = c.id
	where tc.teacher_workload > 0 and c.modality != 'A Distância' and tc.teacher_siape in ($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
	group by c.discipline_name, c.schedule, c.semester
	
	UNION ALL
	
	select 0 qnt, c.discipline_name, sum(c.enroled) total
	from teachers_classes tc
	join classes c
	on tc.class_id = c.id
	where tc.teacher_workload = 0 and c.modality != 'A Distância' and tc.teacher_siape in ($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
	group by c.discipline_name, c.schedule, c.semester
	
	UNION ALL

	select 1 qnt, c.discipline_name, sum(c.enroled) total
	from teachers_classes tc
	join classes c
	on tc.class_id = c.id
	where c.modality = 'A Distância' and tc.teacher_siape in ($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
	group by c.discipline_name, c.semester
) q
group by q.discipline_name
order by media desc
