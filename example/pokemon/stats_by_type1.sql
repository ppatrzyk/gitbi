-- Pokemon statistics based on type1
select
    type1,
    count(*) as count,
    round(avg(hp), 2) as avg_hp,
    round(avg(attack), 2) as avg_attack,
    round(avg(defense), 2) as avg_defense,
    round(avg(speed), 2) as avg_speed
from pokemons
group by type1
order by count desc;
