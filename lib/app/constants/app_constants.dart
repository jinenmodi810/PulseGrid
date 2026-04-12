/// Application-wide constants (non-secret).
class AppConstants {
  const AppConstants._();

  static const String appName = 'PulseGrid';
}

/// Declarative route paths for GoRouter.
///
/// **Product flow (role-based):**
/// - **Landing** `/` → **Role select** → branch:
///   - Affected: register → **Request help** → submit → **Incident tracking**
///   - Volunteer: register → **Volunteer tasks** → task detail → complete → rewards/profile as needed
///   - Organization: register → **Organization dashboard** (institutional response)
///
/// There is no generic “home” hub after sign-up; each role lands on their primary work screen.
class AppRoutes {
  const AppRoutes._();

  /// Premium first screen (PulseGrid story + Continue).
  static const String landing = '/';

  static const String roleSelect = '/role-select';
  static const String registerUser = '/register/user';
  static const String registerVolunteer = '/register/volunteer';
  static const String registerOrganization = '/register/organization';
  static const String loginVictim = '/login/victim';
  static const String loginVolunteer = '/login/volunteer';
  static const String loginOrganization = '/login/organization';
  /// Primary hub after affected-user registration or session restore.
  static const String victimHome = '/home/victim';
  /// Primary hub after volunteer registration or session restore.
  static const String volunteerHome = '/home/volunteer';
  static const String requestHelp = '/request-help';
  /// Live incident tracking with id (POST /incidents success navigates here).
  static const String incidentDetailPath = '/incident/:incidentId';

  static String incidentDetail(String incidentId) => '/incident/$incidentId';
  static const String volunteerTasks = '/volunteer/tasks';
  /// Volunteer task detail (must be registered before [volunteerTasks] in GoRouter).
  static const String volunteerTaskDetailPath = '/volunteer/tasks/:incidentId';

  static String volunteerTaskDetail(String incidentId) => '/volunteer/tasks/$incidentId';
  static const String incidentTracking = '/incident-tracking';
  static const String supportDirectory = '/support-directory';
  static const String rewards = '/rewards';
  static const String organizationDashboard = '/organization/dashboard';
  static const String organizationIncidents = '/organization/incidents';
  static const String organizationResources = '/organization/resources';
  static const String organizationProfile = '/organization/profile';
  /// Dev / deep-link only — not linked from the main role flow.
  static const String adminInspection = '/admin-inspection';
  static const String adminInspectionUsers = '/admin-inspection/users';
  static const String adminInspectionVolunteers = '/admin-inspection/volunteers';
  static const String adminInspectionIncidents = '/admin-inspection/incidents';
  static const String adminInspectionIncidentDetailPath = '/admin-inspection/incident/:incidentId';

  static String adminInspectionIncidentDetail(String incidentId) => '/admin-inspection/incident/$incidentId';

  static const String adminInspectionAssignments = '/admin-inspection/assignments';
  static const String adminInspectionRewards = '/admin-inspection/rewards';
  static const String adminInspectionSupport = '/admin-inspection/support-network';
  static const String profile = '/profile';

  // —— Legacy paths (redirect in router) ——
  @Deprecated('Use landing')
  static const String splash = '/splash';

  @Deprecated('Removed from flow')
  static const String welcome = '/welcome';

  @Deprecated('Removed from flow')
  static const String home = '/home';
}

/// Asset paths registered in pubspec.yaml.
class AssetPaths {
  const AssetPaths._();

  static const String mockIncidents = 'assets/json/mock_incidents.json';
  static const String mockVolunteers = 'assets/json/mock_volunteers.json';
  static const String mockResponders = 'assets/json/mock_responders.json';
  static const String mockHospitals = 'assets/json/mock_hospitals.json';
  static const String mockShelters = 'assets/json/mock_shelters.json';
  static const String mockSupportContacts = 'assets/json/mock_support_contacts.json';
  static const String mockRoutes = 'assets/json/mock_routes.json';
  static const String mockRewards = 'assets/json/mock_rewards.json';
}

/// Local session keys (SharedPreferences).
class SessionKeys {
  const SessionKeys._();

  static const String role = 'session_user_role';
  static const String graphUserId = 'session_graph_user_id';
  static const String graphVolunteerId = 'session_graph_volunteer_id';
  static const String graphOrganizationId = 'session_graph_organization_id';
  static const String organizationType = 'session_organization_type';
  static const String volunteerAvailability = 'session_volunteer_availability';
  static const String zoneId = 'session_zone_id';
  /// Legacy hackathon admin console header storage (not used in main product flows).
  static const String adminMarker = 'session_admin_marker';
  static const String lastIncidentId = 'session_last_incident_id';
  static const String authToken = 'session_access_token';
  /// Cached affected-user profile hints for help-request prefill (not a full profile API).
  static const String userHouseholdSize = 'session_user_household_size';
  static const String userElderlyCount = 'session_user_elderly_count';
  static const String userOxygenDependency = 'session_user_oxygen_dependency';
  static const String userPreferredLanguage = 'session_user_preferred_language';
  static const String userMobilityConcern = 'session_user_mobility_concern';
}
