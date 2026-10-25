select * from {{ ref('rpt_retention_cohorts') }} where retention_pct < 0 or retention_pct > 100
