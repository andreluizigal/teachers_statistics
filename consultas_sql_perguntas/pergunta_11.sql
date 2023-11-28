
select s.semester, count(*) total
from (
select c.id::TEXT , c.semester, count(*) 
from teachers t
join teachers_classes tc
on t.siape = tc.teacher_siape
join classes c
on tc.class_id = c.id
where tc.teacher_workload > 0 and c.modality != 'A Distância' and t.department_id in ($department) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
group by c.id, c.semester

UNION ALL

select c.discipline_name, c.semester, count(*)
from teachers t
join teachers_classes tc
on t.siape = tc.teacher_siape
join classes c
on tc.class_id = c.id
where c.modality = 'A Distância' and t.department_id in ($department) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
group by c.discipline_name, t.siape, c.semester
) s
group by s.semester
order by s.semester

------------------------------------------

select avg(p.total)
from (
  	  select s.semester, count(*) total
      from (
      select c.id::TEXT , c.semester, count(*) 
      from teachers t
      join teachers_classes tc
      on t.siape = tc.teacher_siape
      join classes c
      on tc.class_id = c.id
      where tc.teacher_workload > 0 and c.modality != 'A Distância' and t.department_id in ($department) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
      group by c.id, c.semester

      UNION ALL

      select c.discipline_name, c.semester, count(*)
      from teachers t
      join teachers_classes tc
      on t.siape = tc.teacher_siape
      join classes c
      on tc.class_id = c.id
      where c.modality = 'A Distância' and t.department_id in ($department) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
      group by c.discipline_name, t.siape, c.semester
      ) s
      group by s.semester
) p 