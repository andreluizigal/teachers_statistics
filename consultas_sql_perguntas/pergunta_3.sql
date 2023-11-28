select replace(d.name, 'ENGENHARIA', 'ENG') departamento, count(*) total
from departments d
join (
	select t.department_id, mc.matrix_name, count(*)
	from teachers t
	join teachers_classes tc
	on t.siape = tc.teacher_siape
	join matrices_classes mc
	on tc.class_id = mc.class_id
	join classes c
	on mc.class_id = c.id
	where c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
	group by t.department_id, mc.matrix_name
	) t
on d.id = t.department_id
group by d.name
order by d.name

-----------------------------------

select avg(p.total)
from (
  select d.name departamento, count(*) total
  from departments d
  join (
    select t.department_id, mc.matrix_name, count(*)
    from teachers t
    join teachers_classes tc
    on t.siape = tc.teacher_siape
    join matrices_classes mc
    on tc.class_id = mc.class_id
    join classes c
    on mc.class_id = c.id
    where c.semester in ($semester) and c.graduation in ($level) and c.mandatory in ($mandatory)
    group by t.department_id, mc.matrix_name
    ) t
  on d.id = t.department_id
  group by d.name
  order by d.name
) p