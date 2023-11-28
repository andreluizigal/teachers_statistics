select avg(q.enroled)
from (
      select c.discipline_name, sum(c.enroled) enroled
      from teachers_classes tc
      join classes c
      on tc.class_id = c.id
      where c.modality != 'A Distância' and  tc.teacher_siape in($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
      group by c.discipline_name, c.schedule, c.semester

      UNION ALL

      select discipline_name d, sum(c.enroled) enroled
      from teachers_classes tc
      join classes c
      on tc.class_id = c.id
      where c.modality = 'A Distância' and tc.teacher_siape in($teacher) and c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
      group by discipline_name
) q