import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../auth/presentation/widgets/zone_chip_selector.dart';
import 'need_chip_selector.dart';

/// Incident types supported for demo + Neo4j persistence.
const kIncidentTypes = <String>[
  'flood',
  'fire',
  'medical',
  'collapse',
  'power_outage',
  'other',
];

const kSeverities = <String>['low', 'medium', 'high', 'critical'];

/// Zone-only routing copy for the help request flow (no implied live GPS).
const kMvpZoneLocationFootnote =
    'PulseGrid uses the zone you select for matching — live device GPS and maps are not enabled in this build yet.';

class RequestForm extends StatelessWidget {
  const RequestForm({
    super.key,
    required this.incidentType,
    required this.onIncidentType,
    required this.severity,
    required this.onSeverity,
    required this.peopleController,
    required this.zoneId,
    required this.onZoneId,
    required this.noteController,
    required this.elderly,
    required this.onElderly,
    required this.childPresent,
    required this.onChildPresent,
    required this.injury,
    required this.onInjury,
    required this.oxygenRequired,
    required this.onOxygenRequired,
    required this.shelterNeeded,
    required this.onShelterNeeded,
    required this.foodNeeded,
    required this.onFoodNeeded,
    required this.transportNeeded,
    required this.onTransportNeeded,
    this.profileSyncHint,
    this.zoneFootnote = kMvpZoneLocationFootnote,
  });

  final String incidentType;
  final ValueChanged<String> onIncidentType;
  final String severity;
  final ValueChanged<String> onSeverity;
  final TextEditingController peopleController;
  final String zoneId;
  final ValueChanged<String> onZoneId;
  final TextEditingController noteController;
  final bool elderly;
  final ValueChanged<bool> onElderly;
  final bool childPresent;
  final ValueChanged<bool> onChildPresent;
  final bool injury;
  final ValueChanged<bool> onInjury;
  final bool oxygenRequired;
  final ValueChanged<bool> onOxygenRequired;
  final bool shelterNeeded;
  final ValueChanged<bool> onShelterNeeded;
  final bool foodNeeded;
  final ValueChanged<bool> onFoodNeeded;
  final bool transportNeeded;
  final ValueChanged<bool> onTransportNeeded;
  final String? profileSyncHint;
  final String? zoneFootnote;

  String _labelFor(String value) {
    return value.replaceAll('_', ' ').split(' ').map((w) {
      if (w.isEmpty) return w;
      return '${w[0].toUpperCase()}${w.substring(1)}';
    }).join(' ');
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (profileSyncHint != null && profileSyncHint!.isNotEmpty) ...[
          DecoratedBox(
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.6),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.auto_awesome, size: 20, color: Theme.of(context).colorScheme.primary),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      profileSyncHint!,
                      style: AppTextStyles.body().copyWith(fontSize: 13, height: 1.35),
                      maxLines: 6,
                      overflow: TextOverflow.fade,
                      softWrap: true,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
        ],
        Text('Incident details', style: AppTextStyles.titleMedium()),
        const SizedBox(height: 12),
        InputDecorator(
          decoration: const InputDecoration(
            labelText: 'Incident type',
            border: OutlineInputBorder(),
            contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              isExpanded: true,
              value: incidentType,
              items: [
                for (final t in kIncidentTypes)
                  DropdownMenuItem(value: t, child: Text(_labelFor(t))),
              ],
              onChanged: (v) {
                if (v != null) onIncidentType(v);
              },
            ),
          ),
        ),
        const SizedBox(height: 12),
        InputDecorator(
          decoration: const InputDecoration(
            labelText: 'Severity',
            border: OutlineInputBorder(),
            contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              isExpanded: true,
              value: severity,
              items: [
                for (final s in kSeverities)
                  DropdownMenuItem(value: s, child: Text(_labelFor(s))),
              ],
              onChanged: (v) {
                if (v != null) onSeverity(v);
              },
            ),
          ),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: peopleController,
          keyboardType: TextInputType.number,
          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
          decoration: const InputDecoration(
            labelText: 'People affected',
            border: OutlineInputBorder(),
            helperText: 'Edit to override your saved household size for this request only',
          ),
        ),
        const SizedBox(height: 16),
        ZoneChipSelector(
          selectedZoneId: zoneId,
          onSelected: onZoneId,
          label: 'Current zone',
          footnote: zoneFootnote,
        ),
        const SizedBox(height: 20),
        NeedChipSelector(
          elderly: elderly,
          onElderly: onElderly,
          childPresent: childPresent,
          onChildPresent: onChildPresent,
          injury: injury,
          onInjury: onInjury,
          oxygenRequired: oxygenRequired,
          onOxygenRequired: onOxygenRequired,
          shelterNeeded: shelterNeeded,
          onShelterNeeded: onShelterNeeded,
          foodNeeded: foodNeeded,
          onFoodNeeded: onFoodNeeded,
          transportNeeded: transportNeeded,
          onTransportNeeded: onTransportNeeded,
        ),
        TextField(
          controller: noteController,
          maxLines: 3,
          maxLength: 2000,
          decoration: const InputDecoration(
            labelText: 'Short note',
            alignLabelWithHint: true,
            border: OutlineInputBorder(),
          ),
        ),
      ],
    );
  }
}
