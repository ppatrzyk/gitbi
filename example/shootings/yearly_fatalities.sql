-- fatalities by year
select 
	year,
	sum(fatalities) as fatalities
from '../gitbi-example/us_mass_shootings.csv'
group by year
order by year desc;