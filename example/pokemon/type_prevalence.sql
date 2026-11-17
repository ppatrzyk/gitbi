-- Pokemon types
select
    type1,
    type2,
    count(*) as count
from pokemons
group by type1, type2
order by count desc;