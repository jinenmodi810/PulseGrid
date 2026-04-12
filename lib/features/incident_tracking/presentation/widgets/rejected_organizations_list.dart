import 'package:flutter/material.dart';

import '../../../../app/theme/app_text_styles.dart';
import '../../../../core/widgets/app_card.dart';
import '../../data/incident_detail_dto.dart';

class RejectedOrganizationsList extends StatelessWidget {
  const RejectedOrganizationsList({super.key, required this.candidates});

  final List<RejectedOrganizationDto> candidates;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Partners considered', style: AppTextStyles.titleMedium().copyWith(fontSize: 16)),
          const SizedBox(height: 8),
          if (candidates.isEmpty)
            Text('No alternate organization ranking for this incident.', style: AppTextStyles.bodyMuted())
          else
            for (final c in candidates)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.apartment_outlined, size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(c.name.isEmpty ? c.organizationId : c.name, style: AppTextStyles.body()),
                          Text(c.reason, style: AppTextStyles.bodyMuted()),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
        ],
      ),
    );
  }
}
