import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_chip.dart';

class VolunteerSkillSelector extends StatefulWidget {
  const VolunteerSkillSelector({super.key});

  @override
  State<VolunteerSkillSelector> createState() => _VolunteerSkillSelectorState();
}

class _VolunteerSkillSelectorState extends State<VolunteerSkillSelector> {
  final Set<String> _skills = {'logistics'};

  @override
  Widget build(BuildContext context) {
    final options = ['logistics', 'medical', 'communications', 'childcare', 'translation'];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Skills', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
        const SizedBox(height: 8),
        Text(
          // TODO(Phase1): persist skills with volunteer profile repository.
          'Select what you can offer during deployments.',
          style: AppTextStyles.bodyMuted(),
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: options.map((skill) {
            final selected = _skills.contains(skill);
            return AppChip(
              label: skill,
              selected: selected,
              onSelected: (_) {
                setState(() {
                  if (selected) {
                    _skills.remove(skill);
                  } else {
                    _skills.add(skill);
                  }
                });
              },
            );
          }).toList(),
        ),
      ],
    );
  }
}
