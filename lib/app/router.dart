import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../features/admin_inspection/presentation/screens/admin_assignments_screen.dart';
import '../features/admin_inspection/presentation/screens/admin_incident_detail_screen.dart';
import '../features/admin_inspection/presentation/screens/admin_incidents_screen.dart';
import '../features/admin_inspection/presentation/screens/admin_inspection_screen.dart';
import '../features/admin_inspection/presentation/screens/admin_rewards_screen.dart';
import '../features/admin_inspection/presentation/screens/admin_support_network_screen.dart';
import '../features/admin_inspection/presentation/screens/admin_users_screen.dart';
import '../features/admin_inspection/presentation/screens/admin_volunteers_screen.dart';
import '../features/auth/presentation/screens/organization_login_screen.dart';
import '../features/auth/presentation/screens/organization_registration_screen.dart';
import '../features/auth/presentation/screens/victim_login_screen.dart';
import '../features/auth/presentation/screens/volunteer_login_screen.dart';
import '../features/auth/presentation/screens/role_select_screen.dart';
import '../features/auth/presentation/screens/user_registration_screen.dart';
import '../features/auth/presentation/screens/volunteer_registration_screen.dart';
import '../features/help_request/presentation/screens/request_help_screen.dart';
import '../features/victim_home/presentation/screens/victim_home_screen.dart';
import '../features/volunteer/presentation/screens/volunteer_home_screen.dart';
import '../features/incident_tracking/presentation/screens/incident_tracking_screen.dart';
import '../features/onboarding/presentation/screens/splash_screen.dart';
import '../features/organization/presentation/screens/organization_dashboard_screen.dart';
import '../features/organization/presentation/screens/organization_incidents_screen.dart';
import '../features/organization/presentation/screens/organization_profile_screen.dart';
import '../features/organization/presentation/screens/organization_resources_screen.dart';
import '../features/profile/presentation/screens/profile_screen.dart';
import '../features/rewards/presentation/screens/rewards_screen.dart';
import '../features/support_directory/presentation/screens/support_directory_screen.dart';
import '../features/volunteer/presentation/screens/volunteer_task_detail_screen.dart';
import '../features/volunteer/presentation/screens/volunteer_tasks_screen.dart';
import 'constants/app_constants.dart';
import 'not_found_screen.dart';

String? _authPathAliases(String path) {
  switch (path) {
    case '/victim/login':
      return AppRoutes.loginVictim;
    case '/volunteer/login':
      return AppRoutes.loginVolunteer;
    case '/organization/login':
      return AppRoutes.loginOrganization;
    case '/register/victim':
    case '/register/affected':
      return AppRoutes.registerUser;
    default:
      return null;
  }
}

/// GoRouter configuration.
///
/// **Cold start:** `main.dart` passes [initialLocation] from `startup_session_resolver.dart`
/// so returning users open their role home (victim, volunteer, or organization dashboard).
///
/// **Onboarding:** landing → role select → register → that role’s home; deeper flows push
/// on top (request help, task feed, org incidents, etc.).
GoRouter buildAppRouter({String? initialLocation}) {
  return GoRouter(
    initialLocation: initialLocation ?? AppRoutes.landing,
    redirect: (context, state) {
      var path = state.uri.path;
      if (path.length > 1 && path.endsWith('/')) {
        return path.substring(0, path.length - 1);
      }
      final alias = _authPathAliases(path);
      if (alias != null) {
        return alias;
      }
      return null;
    },
    errorBuilder: (context, state) => NotFoundScreen(attemptedPath: state.uri.toString()),
    routes: <RouteBase>[
      GoRoute(
        path: AppRoutes.landing,
        name: 'landing',
        pageBuilder: (context, state) => const MaterialPage<void>(child: SplashScreen()),
      ),
      GoRoute(
        path: AppRoutes.splash,
        redirect: (context, state) => AppRoutes.landing,
      ),
      GoRoute(
        path: AppRoutes.welcome,
        redirect: (context, state) => AppRoutes.roleSelect,
      ),
      GoRoute(
        path: AppRoutes.home,
        redirect: (context, state) => AppRoutes.roleSelect,
      ),
      GoRoute(
        path: AppRoutes.roleSelect,
        name: 'roleSelect',
        pageBuilder: (context, state) => const MaterialPage<void>(child: RoleSelectScreen()),
      ),
      GoRoute(
        path: AppRoutes.registerUser,
        name: 'registerUser',
        pageBuilder: (context, state) => const MaterialPage<void>(child: UserRegistrationScreen()),
      ),
      GoRoute(
        path: AppRoutes.registerVolunteer,
        name: 'registerVolunteer',
        pageBuilder: (context, state) => const MaterialPage<void>(child: VolunteerRegistrationScreen()),
      ),
      GoRoute(
        path: AppRoutes.registerOrganization,
        name: 'registerOrganization',
        pageBuilder: (context, state) => const MaterialPage<void>(child: OrganizationRegistrationScreen()),
      ),
      GoRoute(
        path: AppRoutes.loginVictim,
        name: 'loginVictim',
        pageBuilder: (context, state) => const MaterialPage<void>(child: VictimLoginScreen()),
      ),
      GoRoute(
        path: AppRoutes.loginVolunteer,
        name: 'loginVolunteer',
        pageBuilder: (context, state) => const MaterialPage<void>(child: VolunteerLoginScreen()),
      ),
      GoRoute(
        path: AppRoutes.loginOrganization,
        name: 'loginOrganization',
        pageBuilder: (context, state) => const MaterialPage<void>(child: OrganizationLoginScreen()),
      ),
      GoRoute(
        path: AppRoutes.victimHome,
        name: 'victimHome',
        pageBuilder: (context, state) => const MaterialPage<void>(child: VictimHomeScreen()),
      ),
      GoRoute(
        path: AppRoutes.volunteerHome,
        name: 'volunteerHome',
        pageBuilder: (context, state) => const MaterialPage<void>(child: VolunteerHomeScreen()),
      ),
      GoRoute(
        path: AppRoutes.requestHelp,
        name: 'requestHelp',
        pageBuilder: (context, state) => const MaterialPage<void>(child: RequestHelpScreen()),
      ),
      GoRoute(
        path: AppRoutes.volunteerTaskDetailPath,
        name: 'volunteerTaskDetail',
        pageBuilder: (context, state) {
          final id = state.pathParameters['incidentId'] ?? '';
          return MaterialPage<void>(child: VolunteerTaskDetailScreen(incidentId: id));
        },
      ),
      GoRoute(
        path: AppRoutes.volunteerTasks,
        name: 'volunteerTasks',
        pageBuilder: (context, state) => const MaterialPage<void>(child: VolunteerTasksScreen()),
      ),
      GoRoute(
        path: AppRoutes.incidentDetailPath,
        name: 'incidentDetail',
        pageBuilder: (context, state) {
          final id = state.pathParameters['incidentId'] ?? '';
          return MaterialPage<void>(child: IncidentTrackingScreen(incidentId: id.isEmpty ? null : id));
        },
      ),
      GoRoute(
        path: AppRoutes.incidentTracking,
        name: 'incidentTracking',
        pageBuilder: (context, state) => const MaterialPage<void>(child: IncidentTrackingScreen()),
      ),
      GoRoute(
        path: AppRoutes.supportDirectory,
        name: 'supportDirectory',
        pageBuilder: (context, state) => const MaterialPage<void>(child: SupportDirectoryScreen()),
      ),
      GoRoute(
        path: AppRoutes.rewards,
        name: 'rewards',
        pageBuilder: (context, state) => const MaterialPage<void>(child: RewardsScreen()),
      ),
      GoRoute(
        path: AppRoutes.organizationDashboard,
        name: 'organizationDashboard',
        pageBuilder: (context, state) => const MaterialPage<void>(child: OrganizationDashboardScreen()),
      ),
      GoRoute(
        path: AppRoutes.organizationIncidents,
        name: 'organizationIncidents',
        pageBuilder: (context, state) => const MaterialPage<void>(child: OrganizationIncidentsScreen()),
      ),
      GoRoute(
        path: AppRoutes.organizationResources,
        name: 'organizationResources',
        pageBuilder: (context, state) => const MaterialPage<void>(child: OrganizationResourcesScreen()),
      ),
      GoRoute(
        path: AppRoutes.organizationProfile,
        name: 'organizationProfile',
        pageBuilder: (context, state) => const MaterialPage<void>(child: OrganizationProfileScreen()),
      ),
      GoRoute(
        path: AppRoutes.adminInspection,
        name: 'adminInspection',
        pageBuilder: (context, state) => const MaterialPage<void>(child: AdminInspectionScreen()),
      ),
      GoRoute(
        path: AppRoutes.adminInspectionUsers,
        name: 'adminInspectionUsers',
        pageBuilder: (context, state) => const MaterialPage<void>(child: AdminUsersScreen()),
      ),
      GoRoute(
        path: AppRoutes.adminInspectionVolunteers,
        name: 'adminInspectionVolunteers',
        pageBuilder: (context, state) => const MaterialPage<void>(child: AdminVolunteersScreen()),
      ),
      GoRoute(
        path: AppRoutes.adminInspectionIncidents,
        name: 'adminInspectionIncidents',
        pageBuilder: (context, state) => const MaterialPage<void>(child: AdminIncidentsScreen()),
      ),
      GoRoute(
        path: AppRoutes.adminInspectionIncidentDetailPath,
        name: 'adminInspectionIncidentDetail',
        pageBuilder: (context, state) {
          final id = state.pathParameters['incidentId'] ?? '';
          return MaterialPage<void>(child: AdminIncidentDetailScreen(incidentId: id));
        },
      ),
      GoRoute(
        path: AppRoutes.adminInspectionAssignments,
        name: 'adminInspectionAssignments',
        pageBuilder: (context, state) => const MaterialPage<void>(child: AdminAssignmentsScreen()),
      ),
      GoRoute(
        path: AppRoutes.adminInspectionRewards,
        name: 'adminInspectionRewards',
        pageBuilder: (context, state) => const MaterialPage<void>(child: AdminRewardsScreen()),
      ),
      GoRoute(
        path: AppRoutes.adminInspectionSupport,
        name: 'adminInspectionSupport',
        pageBuilder: (context, state) => const MaterialPage<void>(child: AdminSupportNetworkScreen()),
      ),
      GoRoute(
        path: AppRoutes.profile,
        name: 'profile',
        pageBuilder: (context, state) => const MaterialPage<void>(child: ProfileScreen()),
      ),
    ],
  );
}
