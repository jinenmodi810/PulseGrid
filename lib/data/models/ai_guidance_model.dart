/// AI-generated operational guidance for coordinators or responders.
class AiGuidanceModel {
  const AiGuidanceModel({
    required this.title,
    required this.body,
    this.generatedAt,
  });

  final String title;
  final String body;
  final DateTime? generatedAt;

  factory AiGuidanceModel.fromJson(Map<String, dynamic> json) {
    return AiGuidanceModel(
      title: json['title'] as String? ?? 'Guidance',
      body: json['body'] as String? ?? '',
      generatedAt: json['generated_at'] != null
          ? DateTime.tryParse(json['generated_at'] as String)
          : null,
    );
  }
}
