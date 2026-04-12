import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/constants/app_constants.dart';
import '../../../../app/providers.dart';
import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/utils/result.dart';
import '../../../../core/widgets/app_button.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/loading_view.dart';
import '../../../help_request/presentation/providers/help_request_providers.dart';
import '../../../incident_tracking/data/incident_detail_dto.dart';
import '../../../incident_tracking/presentation/providers/ai_guidance_providers.dart';
import '../../../incident_tracking/presentation/widgets/ai_guidance_card.dart';
import '../../../incident_tracking/presentation/widgets/assignment_card.dart';
import '../../../incident_tracking/presentation/providers/incident_realtime_provider.dart';
import '../../../incident_tracking/presentation/response_tier_copy.dart';
import '../../../incident_tracking/presentation/widgets/route_status_card.dart';
import '../providers/volunteer_realtime_provider.dart';
import '../providers/volunteer_task_providers.dart';

class VolunteerTaskDetailScreen extends ConsumerStatefulWidget {
  const VolunteerTaskDetailScreen({super.key, required this.incidentId});

  final String incidentId;

  @override
  ConsumerState<VolunteerTaskDetailScreen> createState() => _VolunteerTaskDetailScreenState();
}

class _VolunteerTaskDetailScreenState extends ConsumerState<VolunteerTaskDetailScreen> {
  bool _busy = false;

  String _needsLine(IncidentDetailDto d) {
    final parts = <String>[];
    if (d.shelterNeeded) parts.add('Shelter');
    if (d.foodNeeded) parts.add('Food');
    if (d.transportNeeded) parts.add('Transport');
    if (d.elderly) parts.add('Elderly');
    if (d.childPresent) parts.add('Child');
    if (d.injury) parts.add('Injury');
    if (d.oxygenRequired) parts.add('Oxygen');
    return parts.isEmpty ? 'No special flags recorded.' : parts.join(' · ');
  }

  Future<String?> _volunteerId() => ref.read(storageServiceProvider).getString(SessionKeys.graphVolunteerId);

  Future<void> _accept() async {
    final vid = await _volunteerId();
    if (!mounted || vid == null || vid.isEmpty) return;
    setState(() => _busy = true);
    final r = await ref.read(acceptTaskUsecaseProvider).call(incidentId: widget.incidentId, volunteerId: vid);
    if (!mounted) return;
    setState(() => _busy = false);
    switch (r) {
      case Success():
        invalidateVolunteerTaskCaches(ref, incidentId: widget.incidentId);
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Task accepted.')));
      case Failure(:final error):
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  Future<void> _complete() async {
    final vid = await _volunteerId();
    if (!mounted || vid == null || vid.isEmpty) return;
    setState(() => _busy = true);
    final r = await ref.read(completeTaskUsecaseProvider).call(incidentId: widget.incidentId, volunteerId: vid);
    if (!mounted) return;
    setState(() => _busy = false);
    switch (r) {
      case Success(:final data):
        invalidateVolunteerTaskCaches(ref, incidentId: widget.incidentId);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Marked resolved. Credits ${data.volunteerCredits} · trust ${data.volunteerTrustScore.toStringAsFixed(2)}',
            ),
          ),
        );
      case Failure(:final error):
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  @override
  Widget build(BuildContext context) {
    ref.watch(incidentRealtimeProvider(widget.incidentId));
    ref.watch(volunteerRealtimeBySessionProvider);
    final detailAsync = ref.watch(incidentDetailProvider(widget.incidentId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Task detail'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: detailAsync.when(
        loading: () => const LoadingView(message: 'Loading incident…'),
        error: (e, _) => Padding(
          padding: const EdgeInsets.all(24),
          child: Text(
            e.toString().replaceFirst('Exception: ', ''),
            textAlign: TextAlign.center,
          ),
        ),
        data: (dto) {
          final s = dto.status.toLowerCase();
          final showAccept = s != 'accepted' && s != 'resolved';
          final showComplete = s != 'resolved';
          final helperName = dto.assignedHelperName;
          final pendingHelper = helperName == null || helperName.isEmpty;

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              AppCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Incident', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
                    const SizedBox(height: 8),
                    Text('${dto.incidentType} · ${dto.severity}', style: AppTextStyles.body()),
                    const SizedBox(height: 4),
                    Text('Zone ${dto.zoneId} · Priority ${dto.priorityLabel}', style: AppTextStyles.bodyMuted()),
                    if (dto.note.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Text(dto.note, style: AppTextStyles.body()),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 12),
              AppCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Needs', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
                    const SizedBox(height: 6),
                    Text(_needsLine(dto), style: AppTextStyles.body()),
                  ],
                ),
              ),
              if (dto.responseTier.isNotEmpty) ...[
                const SizedBox(height: 12),
                AppCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Coordination mode', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
                      const SizedBox(height: 6),
                      Text(responseTierHeadline(dto.responseTier), style: AppTextStyles.body()),
                      if (dto.decisionSummary.isNotEmpty) ...[
                        const SizedBox(height: 6),
                        Text(
                          dto.decisionSummary,
                          maxLines: 4,
                          overflow: TextOverflow.ellipsis,
                          style: AppTextStyles.bodyMuted(),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
              const SizedBox(height: 12),
              AssignmentCard(
                incidentStatus: dto.status,
                assignmentHeadline: pendingHelper
                    ? 'Pending assignment'
                    : 'Volunteer: $helperName',
                subtitle: pendingHelper ? 'You can still accept if this task is in your zone.' : null,
              ),
              const SizedBox(height: 12),
              RouteStatusCard(routeStatus: dto.routeStatus, etaMinutes: dto.etaMinutes),
              const SizedBox(height: 12),
              ref.watch(volunteerGuidanceProvider(widget.incidentId)).when(
                    loading: () => const AiGuidanceCard(
                      title: 'Volunteer guidance',
                      message: '',
                      loading: true,
                    ),
                    error: (e, _) => AiGuidanceCard(
                      title: 'Volunteer guidance',
                      message: e.toString().replaceFirst('Exception: ', ''),
                      isError: true,
                      onRefresh: () => ref.invalidate(volunteerGuidanceProvider(widget.incidentId)),
                    ),
                    data: (g) => AiGuidanceCard(
                      title: 'Volunteer guidance',
                      message: g.message,
                      fallbackUsed: g.fallbackUsed,
                      languageCode: g.language,
                      onRefresh: () => ref.invalidate(volunteerGuidanceProvider(widget.incidentId)),
                    ),
                  ),
              const SizedBox(height: 20),
              if (showAccept)
                AppButton(
                  label: _busy ? 'Please wait…' : 'Accept task',
                  onPressed: _busy ? null : _accept,
                  hero: true,
                ),
              if (showAccept && showComplete) const SizedBox(height: 12),
              if (showComplete)
                AppButton(
                  label: _busy ? 'Please wait…' : 'Mark complete',
                  onPressed: _busy ? null : _complete,
                  variant: AppButtonVariant.outlined,
                  hero: true,
                ),
            ],
          );
        },
      ),
    );
  }
}
