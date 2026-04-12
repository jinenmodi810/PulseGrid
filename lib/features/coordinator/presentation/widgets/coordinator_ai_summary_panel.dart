import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../incident_tracking/presentation/providers/ai_guidance_providers.dart';
import '../../../incident_tracking/presentation/widgets/ai_guidance_card.dart';

/// Paste an incident id to preview an AI triage summary (demo-friendly).
class CoordinatorAiSummaryPanel extends ConsumerStatefulWidget {
  const CoordinatorAiSummaryPanel({super.key});

  @override
  ConsumerState<CoordinatorAiSummaryPanel> createState() => _CoordinatorAiSummaryPanelState();
}

class _CoordinatorAiSummaryPanelState extends ConsumerState<CoordinatorAiSummaryPanel> {
  final _controller = TextEditingController();
  String? _activeId;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('AI incident summary', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
          const SizedBox(height: 6),
          Text(
            'Paste an incident id. Summaries are assistive only — assignments stay system-owned.',
            style: AppTextStyles.bodyMuted(),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _controller,
            decoration: const InputDecoration(
              labelText: 'Incident id',
              border: OutlineInputBorder(),
              isDense: true,
            ),
            autocorrect: false,
          ),
          const SizedBox(height: 10),
          FilledButton.tonal(
            onPressed: () {
              final id = _controller.text.trim();
              setState(() => _activeId = id.isEmpty ? null : id);
              if (id.isNotEmpty) {
                ref.invalidate(organizationIncidentSummaryProvider(id));
              }
            },
            child: const Text('Generate summary'),
          ),
          if (_activeId != null && _activeId!.isNotEmpty) ...[
            const SizedBox(height: 14),
            ref.watch(organizationIncidentSummaryProvider(_activeId!)).when(
                  loading: () => const AiGuidanceCard(
                    title: 'Incident summary',
                    message: '',
                    loading: true,
                  ),
                  error: (e, _) => AiGuidanceCard(
                    title: 'Incident summary',
                    message: e.toString().replaceFirst('Exception: ', ''),
                    isError: true,
                    onRefresh: () => ref.invalidate(organizationIncidentSummaryProvider(_activeId!)),
                  ),
                  data: (g) => AiGuidanceCard(
                    title: 'Incident summary',
                    message: g.message,
                    fallbackUsed: g.fallbackUsed,
                    languageCode: g.language,
                    onRefresh: () => ref.invalidate(organizationIncidentSummaryProvider(_activeId!)),
                  ),
                ),
          ],
        ],
      ),
    );
  }
}
