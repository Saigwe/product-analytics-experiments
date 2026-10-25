-- Rates are proportions. Funnel steps count sessions, and RetailRocket allows a purchase without a
-- logged add-to-cart in the same session, so only the view step is a hard upper bound.
select *
from {{ ref('rpt_funnel_weekly') }}
where cart_sessions > view_sessions
   or purchase_sessions > view_sessions
   or view_to_cart not between 0 and 1
   or view_to_purchase not between 0 and 1
