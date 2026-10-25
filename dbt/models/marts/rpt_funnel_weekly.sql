-- Session funnel by week: sessions with a view -> with an add-to-cart -> with a purchase,
-- and the step conversion rates. "Purchase sessions" counts sessions with a transaction.
select
    cast({{ dbt.date_trunc('week', 'session_date') }} as date)                  as week_start,
    count(*) filter (where has_view)                                            as view_sessions,
    count(*) filter (where has_add_to_cart)                                     as cart_sessions,
    count(*) filter (where has_purchase)                                        as purchase_sessions,
    cast(count(*) filter (where has_add_to_cart) as double)
        / nullif(count(*) filter (where has_view), 0)                          as view_to_cart,
    cast(count(*) filter (where has_purchase) as double)
        / nullif(count(*) filter (where has_add_to_cart), 0)                   as cart_to_purchase,
    cast(count(*) filter (where has_purchase) as double)
        / nullif(count(*) filter (where has_view), 0)                          as view_to_purchase
from {{ ref('fct_sessions') }}
group by 1
