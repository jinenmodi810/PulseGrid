/// Response from register-* and login-* email/password endpoints.
class AuthSignInResult {
  const AuthSignInResult({
    required this.accessToken,
    required this.role,
    required this.id,
  });

  final String accessToken;
  final String role;
  /// Neo4j graph id for the principal (user / volunteer / organization).
  final String id;

  factory AuthSignInResult.fromJson(Map<String, dynamic> json) {
    return AuthSignInResult(
      accessToken: json['access_token'] as String? ?? '',
      role: json['role'] as String? ?? '',
      id: json['id'] as String? ?? '',
    );
  }
}
