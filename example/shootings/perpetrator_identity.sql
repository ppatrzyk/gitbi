select 
	gender,
	race,
	count(*) as shootings
from './example/us_mass_shootings.csv'
group by gender, race
order by gender, race;