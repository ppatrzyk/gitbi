-- Dangerous locations
select 
	location,
	count(*) as shootings,
	sum(total_victims) as killed,
	round(avg(fatalities/total_victims), 2) as avg_death_rate,
	round(avg(age_of_shooter), 2) as avg_age
from '../gitbi-example/us_mass_shootings.csv'
group by location
order by killed desc; 