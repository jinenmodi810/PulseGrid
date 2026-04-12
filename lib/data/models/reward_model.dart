import '../../core/enums/reward_badge_type.dart';
import 'json_helpers.dart';

class RewardModel {
  const RewardModel({
    required this.id,
    required this.title,
    required this.description,
    required this.badgeType,
    required this.creditsValue,
  });

  final String id;
  final String title;
  final String description;
  final RewardBadgeType badgeType;
  final int creditsValue;

  factory RewardModel.fromJson(Map<String, dynamic> json) {
    return RewardModel(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? 'Reward',
      description: json['description'] as String? ?? '',
      badgeType: enumFromName(
        RewardBadgeType.values,
        json['badge_type'] as String?,
        RewardBadgeType.bronze,
      ),
      creditsValue: (json['credits_value'] as num?)?.toInt() ?? 0,
    );
  }
}
