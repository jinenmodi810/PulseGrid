import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../help_request/presentation/providers/help_request_providers.dart';
import '../../application/submit_voice_sos_usecase.dart';
import '../../application/transcribe_voice_sos_usecase.dart';

final transcribeVoiceSosUsecaseProvider = Provider<TranscribeVoiceSosUsecase>((ref) {
  return TranscribeVoiceSosUsecase(ref.watch(voiceSosRepositoryProvider));
});

final submitVoiceSosUsecaseProvider = Provider<SubmitVoiceSosUsecase>((ref) {
  return SubmitVoiceSosUsecase(ref.watch(voiceSosRepositoryProvider));
});
