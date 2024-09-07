def div_ceil(nominator, denominator):
    a = nominator // denominator
    b = 1 if nominator % denominator > 0 else 0
    return a + b
