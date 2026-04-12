import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/status_badge.dart';
import '../../../../data/models/support_contact_model.dart';

class SupportContactCard extends StatelessWidget {
  const SupportContactCard({super.key, required this.contact});

  final SupportContactModel contact;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Row(
        children: [
          const Icon(Icons.phone_in_talk),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(contact.label, style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
                const SizedBox(height: 4),
                Text(contact.phone, style: AppTextStyles.body()),
              ],
            ),
          ),
          StatusBadge(label: contact.type.name, tone: StatusBadgeTone.neutral),
        ],
      ),
    );
  }
}
