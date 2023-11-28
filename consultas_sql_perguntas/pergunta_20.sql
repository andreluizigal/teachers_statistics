select avg(tc.teacher_workload)
from teachers_classes tc
join classes c
on tc.class_id = c.id
where tc.teacher_workload > 0 and tc.teacher_siape in($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)