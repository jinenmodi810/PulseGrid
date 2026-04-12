import 'package:flutter/material.dart';

/// Consistent scroll padding: horizontal rhythm, top breath, bottom safe area + keyboard.
abstract final class ScreenInsets {
  static EdgeInsets listVertical(BuildContext context, {double horizontal = 20, double top = 8, double bottomExtra = 24}) {
    final mq = MediaQuery.of(context);
    return EdgeInsets.fromLTRB(
      horizontal,
      top,
      horizontal,
      bottomExtra + mq.padding.bottom + mq.viewInsets.bottom,
    );
  }

  static EdgeInsets compactHorizontal(BuildContext context, {double horizontal = 16, double top = 8, double bottomExtra = 24}) {
    final mq = MediaQuery.of(context);
    return EdgeInsets.fromLTRB(
      horizontal,
      top,
      horizontal,
      bottomExtra + mq.padding.bottom + mq.viewInsets.bottom,
    );
  }
}
