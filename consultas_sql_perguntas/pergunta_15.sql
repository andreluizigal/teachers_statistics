select c.semester, sum(c.enroled)
from teachers_classes tc
join classes c
on tc.class_id = c.id
where tc.teacher_siape in($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
group by c.semester
order by c.semester

--------------------

select avg(total)
from (
      select c.semester, sum(c.enroled) total
      from teachers_classes tc
      join classes c
      on tc.class_id = c.id
      where tc.teacher_siape in($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
      group by c.semester
      order by c.semester
) q