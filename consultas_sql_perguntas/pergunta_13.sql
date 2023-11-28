select q.semester, sum(q.teacher_workload)
from (
	select c.semester, c.discipline_name, tc.teacher_workload
	from teachers_classes tc
	join classes c
	on tc.class_id = c.id
  where tc.teacher_siape in($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
	group by c.semester, c.discipline_name, tc.teacher_workload
) q
group by q.semester
order by q.semester

---------------------------------------

select avg(total)
from (
      select q.semester, sum(q.teacher_workload) total
      from (
            select c.semester, c.discipline_name, tc.teacher_workload
            from teachers_classes tc
            join classes c
            on tc.class_id = c.id
            where tc.teacher_siape in($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
            group by c.semester, c.discipline_name, tc.teacher_workload
      ) q
      group by q.semester
      order by q.semester
) q