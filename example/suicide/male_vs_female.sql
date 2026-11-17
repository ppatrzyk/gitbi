-- male vs female suicide rate in some countries (2014)
create temp table males as
    select
        country,
        age,
        suicides_per100k as male_rate
    from suicides
    where 
        sex = 'male' and 
        year = 2014 and 
        country in ('United States', 'Japan', 'Poland', 'Germany');

create temp table females as
    select
        country,
        age,
        suicides_per100k as female_rate
    from suicides
    where 
        sex = 'female' and 
        year = 2014 and 
        country in ('United States', 'Japan', 'Poland', 'Germany');

select 
    m.country,
    m.age,
    m.male_rate,
    f.female_rate,
    round(m.male_rate / f.female_rate, 2) as male_to_female_ratio
from males m
inner join females f
on 
    m.country = f.country and
    m.age = f.age
order by male_to_female_ratio desc;
