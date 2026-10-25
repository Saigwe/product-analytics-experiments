-- Conversion (any purchase) by experiment variant.
select
    a.experiment_id,
    a.variant,
    count(distinct a.user_id)                                                       as users,
    count(distinct case when e.event_name = 'purchase' then e.user_id end)          as purchasers,
    1.0 * count(distinct case when e.event_name = 'purchase' then e.user_id end)
        / count(distinct a.user_id)                                                 as conversion_rate
from {{ ref('stg_bronze__assignments') }} a
left join {{ ref('stg_bronze__events') }} e on e.user_id = a.user_id
group by 1, 2
