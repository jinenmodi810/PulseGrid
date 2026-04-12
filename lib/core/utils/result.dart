/// Lightweight result type for repository and service boundaries.
sealed class Result<T, E> {
  const Result();

  R fold<R>({required R Function(T data) onSuccess, required R Function(E error) onFailure});
}

final class Success<T, E> extends Result<T, E> {
  const Success(this.data);

  final T data;

  @override
  R fold<R>({required R Function(T data) onSuccess, required R Function(E error) onFailure}) {
    return onSuccess(data);
  }
}

final class Failure<T, E> extends Result<T, E> {
  const Failure(this.error);

  final E error;

  @override
  R fold<R>({required R Function(T data) onSuccess, required R Function(E error) onFailure}) {
    return onFailure(error);
  }
}
