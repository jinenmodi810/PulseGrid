/// Form and input validation helpers.
class Validators {
  const Validators._();

  // TODO(Phase1): expand validators for help request and volunteer flows.

  static String? nonEmpty(String? value, {String message = 'Required'}) {
    if (value == null || value.trim().isEmpty) {
      return message;
    }
    return null;
  }

  static String? email(String? value) {
    if (value == null || value.trim().isEmpty) {
      return null;
    }
    final emailPattern = RegExp(r'^[^@]+@[^@]+\.[^@]+$');
    if (!emailPattern.hasMatch(value.trim())) {
      return 'Enter a valid email';
    }
    return null;
  }

  static String? requiredEmail(String? value) {
    final e = nonEmpty(value, message: 'Enter your email');
    if (e != null) {
      return e;
    }
    return email(value);
  }

  static String? passwordMin8(String? value) {
    final e = nonEmpty(value, message: 'Choose a password');
    if (e != null) {
      return e;
    }
    if ((value ?? '').length < 8) {
      return 'Use at least 8 characters';
    }
    return null;
  }
}
