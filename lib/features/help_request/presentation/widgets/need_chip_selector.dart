import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';

class NeedChipSelector extends StatelessWidget {
  const NeedChipSelector({
    super.key,
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
  });

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

  Widget _row(String title, List<Widget> chips) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: AppTextStyles.label()),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: chips,
        ),
        const SizedBox(height: 14),
      ],
    );
  }

  Widget _chip({required String label, required bool selected, required ValueChanged<bool> onSelected}) {
    return FilterChip(
      label: Text(label),
      selected: selected,
      onSelected: onSelected,
      showCheckmark: true,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('People & medical context', style: AppTextStyles.titleMedium().copyWith(fontSize: 15)),
        const SizedBox(height: 8),
        _row(
          '',
          [
            _chip(label: 'Elderly present', selected: elderly, onSelected: onElderly),
            _chip(label: 'Child present', selected: childPresent, onSelected: onChildPresent),
            _chip(label: 'Injury', selected: injury, onSelected: onInjury),
            _chip(label: 'Oxygen required', selected: oxygenRequired, onSelected: onOxygenRequired),
          ],
        ),
        Text('Logistics needs', style: AppTextStyles.titleMedium().copyWith(fontSize: 15)),
        const SizedBox(height: 8),
        _row(
          '',
          [
            _chip(label: 'Shelter', selected: shelterNeeded, onSelected: onShelterNeeded),
            _chip(label: 'Food', selected: foodNeeded, onSelected: onFoodNeeded),
            _chip(label: 'Transport', selected: transportNeeded, onSelected: onTransportNeeded),
          ],
        ),
      ],
    );
  }
}
