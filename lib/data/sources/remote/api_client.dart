import 'package:dio/dio.dart';

import '../../../core/network/api_env.dart';
import '../../../features/auth/data/session_store.dart';

/// HTTP client wrapper (Dio). Base URL from [resolveApiBaseUrl]; Bearer token from [SessionStore].
class ApiClient {
  ApiClient({Dio? dio, SessionStore? sessionStore})
      : _dio = dio ??
            Dio(
              BaseOptions(
                connectTimeout: const Duration(seconds: 12),
                receiveTimeout: const Duration(seconds: 24),
              ),
            ),
        _sessionStore = sessionStore {
    final store = _sessionStore;
    if (store != null) {
      _dio.interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) async {
            final t = await store.getAuthToken();
            if (t != null && t.isNotEmpty) {
              options.headers['Authorization'] = 'Bearer $t';
            }
            handler.next(options);
          },
          onError: (err, handler) async {
            if (err.response?.statusCode == 401) {
              await store.clearSession();
            }
            handler.next(err);
          },
        ),
      );
    }
  }

  final Dio _dio;
  final SessionStore? _sessionStore;

  void configureBaseUrl() {
    _dio.options.baseUrl = resolveApiBaseUrl();
  }

  Dio get client => _dio;
}
