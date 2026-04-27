select
  incident_id,
  created_at,
  assigned_at,
  accepted_at,
  completed_at,
  time_to_assignment_seconds,
  time_to_acceptance_seconds,
  time_to_completion_seconds,
  zone_id,
  priority_label,
  assigned_volunteer_id,
  assigned_organization_id,
  final_status
from read_parquet('../.analytics_cache/fact_incident_lifecycle/*.parquet')
