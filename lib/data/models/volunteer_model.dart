class VolunteerModel {
  const VolunteerModel({
    required this.id,
    required this.displayName,
    required this.skills,
    required this.credits,
  });

  final String id;
  final String displayName;
  final List<String> skills;
  final int credits;

  factory VolunteerModel.fromJson(Map<String, dynamic> json) {
    final skillsRaw = json['skills'];
    final skills = <String>[];
    if (skillsRaw is List) {
      for (final item in skillsRaw) {
        if (item is String) {
          skills.add(item);
        }
      }
    }
    return VolunteerModel(
      id: json['id'] as String? ?? '',
      displayName: json['display_name'] as String? ?? 'Volunteer',
      skills: skills,
      credits: (json['credits'] as num?)?.toInt() ?? 0,
    );
  }
}
