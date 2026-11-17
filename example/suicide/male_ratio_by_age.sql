select 
	country,
	age,
	suicides_per100k as ratio
from suicides
where
	year = 2015 and
	sex = 'male' and
	country in ('United States', 'Japan', 'Poland', 'Germany')
order by country, age;