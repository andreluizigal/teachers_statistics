
select s.semester, count(*) total
from (
select c.semester, count(*) 
from teachers_classes tc
join classes c
on tc.class_id = c.id
where tc.teacher_workload > 0 and c.modality != 'A Distância' and tc.teacher_siape in ($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
group by c.semester, c.schedule

UNION ALL

select c.semester, count(*)
from teachers_classes tc
join classes c
on tc.class_id = c.id
where c.modality = 'A Distância' and tc.teacher_siape in ($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
group by c.semester, c.discipline_name
) s
group by s.semester

---------------------------

select avg(p.total)
from (
  	  select s.semester, count(*) total
      from (
      select c.semester, count(*) 
      from teachers_classes tc
      join classes c
      on tc.class_id = c.id
      where tc.teacher_workload > 0 and c.modality != 'A Distância' and tc.teacher_siape in ($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
      group by c.semester, c.schedule

      UNION ALL

      select c.semester, count(*)
      from teachers_classes tc
      join classes c
      on tc.class_id = c.id
      where c.modality = 'A Distância' and tc.teacher_siape in ($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
      group by c.discipline_name, tc.teacher_siape, c.semester
      ) s
      group by s.semester
) p 