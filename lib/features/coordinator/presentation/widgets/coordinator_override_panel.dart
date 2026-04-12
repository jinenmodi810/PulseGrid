import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/utils/result.dart';
import '../../../../core/widgets/app_button.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../auth/presentation/providers/auth_providers.dart';
import '../../data/coordinator_actions_repository.dart';
import '../providers/coordinator_actions_providers.dart';

/// Compact coordinator controls for demo overrides (Neo4j-backed).
class CoordinatorOverridePanel extends ConsumerStatefulWidget {
  const CoordinatorOverridePanel({super.key});

  @override
  ConsumerState<CoordinatorOverridePanel> createState() => _CoordinatorOverridePanelState();
}

class _CoordinatorOverridePanelState extends ConsumerState<CoordinatorOverridePanel> {
  final _incidentId = TextEditingController();
  final _newVolunteerId = TextEditingController();
  final _note = TextEditingController();
  bool _busy = false;

  @override
  void dispose() {
    _incidentId.dispose();
    _newVolunteerId.dispose();
    _note.dispose();
    super.dispose();
  }

  Future<void> _run(Future<Result<CoordinatorIncidentActionDto, String>> Function() action) async {
    final iid = _incidentId.text.trim();
    if (iid.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Enter an incident id.')),
      );
      return;
    }
    setState(() => _busy = true);
    final result = await action();
    if (!mounted) return;
    setState(() => _busy = false);
    switch (result) {
      case Success(:final data):
        ref.invalidate(dashboardSummaryProvider);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Updated · status ${data.status}')),
        );
      case Failure(:final error):
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final repo = ref.watch(coordinatorActionsRepositoryProvider);
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Coordinator overrides', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
          const SizedBox(height: 6),
          Text(
            // TODO(Phase1C+): auth-guard these mutations; stream updates over websocket.
            'Reassign, escalate, or block routing on a live incident id.',
            style: AppTextStyles.bodyMuted(),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _incidentId,
            decoration: const InputDecoration(
              labelText: 'Incident id',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _newVolunteerId,
            decoration: const InputDecoration(
              labelText: 'New volunteer id (reassign)',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _note,
            maxLines: 2,
            decoration: const InputDecoration(
              labelText: 'Note / reason',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              AppButton(
                label: _busy ? '…' : 'Reassign',
                onPressed: _busy
                    ? null
                    : () async {
                        final vid = _newVolunteerId.text.trim();
                        if (vid.isEmpty) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Enter new volunteer id.')),
                          );
                          return;
                        }
                        await _run(() => repo.reassign(incidentId: _incidentId.text.trim(), newVolunteerId: vid));
                      },
              ),
              AppButton(
                label: 'Escalate',
                variant: AppButtonVariant.outlined,
                onPressed: _busy
                    ? null
                    : () => _run(() => repo.escalate(incidentId: _incidentId.text.trim(), note: _note.text.trim())),
              ),
              AppButton(
                label: 'Block route',
                variant: AppButtonVariant.outlined,
                onPressed: _busy
                    ? null
                    : () => _run(() => repo.blockRoute(incidentId: _incidentId.text.trim(), reason: _note.text.trim())),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
