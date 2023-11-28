select q.matrix_name, count(*)
from (
		select mc.matrix_name, count(*)
		from teachers t
		join teachers_classes tc
		on t.siape = tc.teacher_siape
		join classes c
		on tc.class_id = c.id
		join matrices_classes mc
		on c.id = mc.class_id
		where c.modality != 'A Distância' and t.department_id in ($department) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
		group by mc.matrix_name, c.id
		
		UNION ALL
	
		select mc.matrix_name, count(*)
		from teachers t
		join teachers_classes tc
		on t.siape = tc.teacher_siape
		join classes c
		on tc.class_id = c.id
		join matrices_classes mc
		on c.id = mc.class_id
		where c.modality = 'A Distância' and t.department_id in ($department) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
		group by mc.matrix_name, c.semester, tc.teacher_siape 
	) q
group by q.matrix_name
order by count desc