select s.semester, count(*)
from (
	select q.semester, count(*)
	from (
			select mc.matrix_name, c.semester, count(*)
			from teachers_classes tc
			join classes c
			on tc.class_id = c.id
			join matrices_classes mc
			on c.id = mc.class_id
			where tc.teacher_siape in ($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
			group by mc.matrix_name, c.id, c.semester
		) q
	group by q.matrix_name, q.semester
) s
group by s.semester

------------------------

select count(*)
from(select mc.matrix_name , count(*)
	from teachers_classes tc
	join classes c
	on tc.class_id = c.id
	join matrices_classes mc
	on c.id = mc.class_id
	where tc.teacher_siape in ($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
	group by mc.matrix_name
	) q