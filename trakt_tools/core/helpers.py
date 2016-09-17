def total_seconds(delta):
    return (
        delta.microseconds + 0.0 + (
            delta.seconds + delta.days * 24 * 3600
        ) * 10 ** 6
    ) / 10 ** 6
