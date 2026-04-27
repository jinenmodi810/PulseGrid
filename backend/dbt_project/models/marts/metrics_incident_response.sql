select
  zone_id,
  count(*) as total_incidents,
  avg(time_to_assignment_seconds) as avg_time_to_assignment_seconds,
  avg(time_to_completion_seconds) as avg_time_to_completion_seconds
from {{ ref('stg_gold_incident_lifecycle') }}
group by 1
