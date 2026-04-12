import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/providers.dart';
import '../../../../core/enums/user_role.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/layout/screen_insets.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../help_request/presentation/providers/help_request_providers.dart';
import '../providers/ai_guidance_providers.dart';
import '../providers/incident_realtime_provider.dart';
import '../../data/incident_detail_dto.dart';
import '../response_tier_copy.dart';
import '../widgets/ai_guidance_card.dart';
import '../widgets/assignment_card.dart';
import '../widgets/rejected_organizations_list.dart';
import '../widgets/rejection_reason_list.dart';
import '../widgets/route_status_card.dart';
import '../widgets/timeline_widget.dart';

class IncidentTrackingScreen extends ConsumerStatefulWidget {
  const IncidentTrackingScreen({super.key, this.incidentId});

  /// When null (legacy `/incident-tracking`), tries [SessionKeys.lastIncidentId].
  final String? incidentId;

  @override
  ConsumerState<IncidentTrackingScreen> createState() => _IncidentTrackingScreenState();
}

class _IncidentTrackingScreenState extends ConsumerState<IncidentTrackingScreen> {
  String? _resolvedId;

  @override
  void initState() {
    super.initState();
    if (widget.incidentId != null && widget.incidentId!.isNotEmpty) {
      _resolvedId = widget.incidentId;
      return;
    }
    Future<void>(() async {
      final last = await ref.read(storageServiceProvider).getString(SessionKeys.lastIncidentId);
      if (!mounted) return;
      setState(() {
        _resolvedId = (last != null && last.isNotEmpty) ? last : null;
      });
    });
  }

  String _priorityLine(IncidentDetailDto d) {
    return '${d.priorityLabel} · score ${d.priorityScore.toStringAsFixed(2)}';
  }

  String _routingBullets(IncidentDetailDto d) {
    final v = d.assignedHelperName != null && d.assignedHelperName!.trim().isNotEmpty;
    final o = d.assignedOrganizationName != null && d.assignedOrganizationName!.trim().isNotEmpty;
    final poolV = d.volunteerCandidateAllowed ? 'volunteer routing on' : 'volunteer routing off for this profile';
    final poolO = d.organizationCandidateAllowed ? 'organization routing on' : 'organization routing off for this profile';
    return '${v ? 'Volunteer assigned' : 'No volunteer assigned yet'} · '
        '${o ? 'Organization engaged' : 'No organization assigned yet'} · '
        '$poolV · $poolO';
  }

  @override
  Widget build(BuildContext context) {
    final id = widget.incidentId?.isNotEmpty == true ? widget.incidentId! : _resolvedId;
    if (id != null && id.isNotEmpty) {
      ref.watch(incidentRealtimeProvider(id));
    }

    return Scaffold(
      backgroundColor: AppColors.surfaceCanvas,
      appBar: AppBar(
        title: const Text('Track your request'),
        backgroundColor: AppColors.surfaceCanvas,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () async {
            if (context.canPop()) {
              context.pop();
              return;
            }
            final role = await ref.read(sessionStoreProvider).readRole();
            if (!context.mounted) {
              return;
            }
            if (role == UserRole.affectedUser) {
              context.go(AppRoutes.victimHome);
            } else {
              context.go(AppRoutes.landing);
            }
          },
        ),
      ),
      body: id == null
          ? SafeArea(
              child: SingleChildScrollView(
                padding: ScreenInsets.listVertical(context, horizontal: 24, top: 24, bottomExtra: 32),
                child: ConstrainedBox(
                  constraints: BoxConstraints(
                    minHeight: MediaQuery.sizeOf(context).height -
                        MediaQuery.paddingOf(context).vertical -
                        kToolbarHeight -
                        48,
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'No incident to show yet. Submit a help request first.',
                        textAlign: TextAlign.center,
                        style: AppTextStyles.body(),
                        maxLines: 5,
                        overflow: TextOverflow.fade,
                        softWrap: true,
                      ),
                      const SizedBox(height: 20),
                      FilledButton(
                        onPressed: () => context.go(AppRoutes.requestHelp),
                        child: const Text('Request support'),
                      ),
                    ],
                  ),
                ),
              ),
            )
          : ref.watch(incidentDetailProvider(id)).when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => Center(
                  child: Padding(
                    padding: ScreenInsets.listVertical(context, horizontal: 24, top: 24),
                    child: Text(
                      e is Exception ? e.toString().replaceFirst('Exception: ', '') : e.toString(),
                      textAlign: TextAlign.center,
                      style: AppTextStyles.body(),
                      maxLines: 8,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ),
                data: (dto) {
                  final helperName = dto.assignedHelperName;
                  final pending = helperName == null || helperName.isEmpty;
                  return SafeArea(
                    top: false,
                    child: ListView(
                      keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
                      padding: ScreenInsets.compactHorizontal(context, horizontal: 16, top: 8, bottomExtra: 28),
                      children: [
                      AppCard(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Current status', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
                            const SizedBox(height: 8),
                            Text(
                              dto.status,
                              style: AppTextStyles.body().copyWith(fontWeight: FontWeight.w600),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 6),
                            Text(
                              _priorityLine(dto),
                              style: AppTextStyles.body(),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Zone ${dto.zoneId} · ${dto.severity} · ${dto.peopleCount} people',
                              style: AppTextStyles.bodyMuted(),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            if (dto.preferredLanguage.isNotEmpty) ...[
                              const SizedBox(height: 6),
                              Text(
                                'Preferred language: ${dto.preferredLanguage}',
                                style: AppTextStyles.bodyMuted(),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ],
                        ),
                      ),
                      if (dto.emergencyContactName != null &&
                          dto.emergencyContactName!.isNotEmpty &&
                          dto.emergencyContactPhone != null &&
                          dto.emergencyContactPhone!.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        AppCard(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Emergency contact on file',
                                style: AppTextStyles.titleMedium().copyWith(fontSize: 16),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                dto.emergencyContactName!,
                                style: AppTextStyles.body().copyWith(fontWeight: FontWeight.w600),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                              Text(
                                dto.emergencyContactPhone!,
                                style: AppTextStyles.body(),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                              if (dto.emergencyContactRelationship != null &&
                                  dto.emergencyContactRelationship!.isNotEmpty)
                                Text(
                                  dto.emergencyContactRelationship!,
                                  style: AppTextStyles.bodyMuted(),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              const SizedBox(height: 6),
                              Text(
                                'SMS to this contact is not enabled yet — shown for partner organizations.',
                                style: AppTextStyles.microcopy(),
                                maxLines: 4,
                                overflow: TextOverflow.fade,
                                softWrap: true,
                              ),
                            ],
                          ),
                        ),
                      ],
                      const SizedBox(height: 12),
                      TimelineWidget(
                        incidentId: dto.incidentId,
                        incidentType: dto.incidentType,
                        status: dto.status,
                        createdAt: dto.createdAt,
                      ),
                      const SizedBox(height: 12),
                      AppCard(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Response routing', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
                            const SizedBox(height: 8),
                            if (dto.decisionSummary.isNotEmpty)
                              Text(
                                dto.decisionSummary,
                                style: AppTextStyles.body(),
                                maxLines: 8,
                                overflow: TextOverflow.fade,
                                softWrap: true,
                              )
                            else
                              Text(
                                'PulseGrid classified this incident for coordinated dispatch.',
                                style: AppTextStyles.bodyMuted(),
                                maxLines: 4,
                                overflow: TextOverflow.fade,
                                softWrap: true,
                              ),
                            const SizedBox(height: 8),
                            Text(
                              responseTierHeadline(dto.responseTier),
                              style: AppTextStyles.bodyMuted(),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 6),
                            Text(
                              _routingBullets(dto),
                              style: AppTextStyles.bodyMuted(),
                              maxLines: 5,
                              overflow: TextOverflow.fade,
                              softWrap: true,
                            ),
                            if (dto.escalationRequired) ...[
                              const SizedBox(height: 10),
                              Text(
                                'Escalation is active — partner operations are treating this as higher urgency.',
                                style: AppTextStyles.microcopy().copyWith(fontWeight: FontWeight.w600),
                                maxLines: 4,
                                overflow: TextOverflow.fade,
                                softWrap: true,
                              ),
                            ],
                            if (dto.tierReasons.isNotEmpty) ...[
                              const SizedBox(height: 10),
                              Text(
                                dto.tierReasons.map((e) => e.detail).join(' '),
                                maxLines: 3,
                                overflow: TextOverflow.ellipsis,
                                style: AppTextStyles.microcopy(),
                              ),
                            ],
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                      AssignmentCard(
                        incidentStatus: dto.status,
                        assignmentHeadline: pending
                            ? 'Pending assignment — we are looking for an available volunteer.'
                            : 'Volunteer: $helperName',
                        subtitle: pending
                            ? null
                            : 'Stay reachable; they may message you when en route.',
                      ),
                      if (dto.assignedOrganizationName != null && dto.assignedOrganizationName!.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        AppCard(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Partner organization',
                                style: AppTextStyles.titleMedium().copyWith(fontSize: 16),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              const SizedBox(height: 6),
                              Text(
                                dto.assignedOrganizationName!,
                                style: AppTextStyles.body().copyWith(fontWeight: FontWeight.w600),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                              if (dto.assignedOrganizationType != null && dto.assignedOrganizationType!.isNotEmpty)
                                Text(
                                  'Type: ${dto.assignedOrganizationType}',
                                  style: AppTextStyles.bodyMuted(),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              if (dto.responseTier.isNotEmpty)
                                Text(
                                  responseTierHeadline(dto.responseTier),
                                  style: AppTextStyles.bodyMuted(),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              if (dto.escalationRequired) ...[
                                const SizedBox(height: 8),
                                Text(
                                  'Escalation flagged — partner organizations are prioritizing this request.',
                                  style: AppTextStyles.microcopy(),
                                  maxLines: 4,
                                  overflow: TextOverflow.fade,
                                  softWrap: true,
                                ),
                              ],
                            ],
                          ),
                        ),
                      ],
                      const SizedBox(height: 12),
                      RouteStatusCard(routeStatus: dto.routeStatus, etaMinutes: dto.etaMinutes),
                      const SizedBox(height: 12),
                      ref.watch(affectedUserGuidanceProvider(id)).when(
                            loading: () => const AiGuidanceCard(
                              message: '',
                              loading: true,
                            ),
                            error: (e, _) => AiGuidanceCard(
                              message: e.toString().replaceFirst('Exception: ', ''),
                              isError: true,
                              onRefresh: () => ref.invalidate(affectedUserGuidanceProvider(id)),
                            ),
                            data: (g) => AiGuidanceCard(
                              message: g.message,
                              fallbackUsed: g.fallbackUsed,
                              languageCode: g.language,
                              onRefresh: () => ref.invalidate(affectedUserGuidanceProvider(id)),
                            ),
                          ),
                      const SizedBox(height: 12),
                      RejectionReasonList(candidates: dto.rejected),
                      if (dto.rejectedOrganizations.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        RejectedOrganizationsList(candidates: dto.rejectedOrganizations),
                      ],
                    ],
                    ),
                  );
                },
              ),
    );
  }
}
