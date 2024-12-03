def f(dct):
    lst = []
    idx_1rcf = 0
    list_8bly = sorted(dct)
    while idx_1rcf < len(list_8bly):
        key = list_8bly[idx_1rcf]
        lst.append((key, dct[key]))
        idx_1rcf = idx_1rcf + 1
    return lst