def clamp_between(to_clamp, lower, upper):
    output = to_clamp
    if output < lower:
        output = lower
    elif output > upper:
        output = upper
    return output