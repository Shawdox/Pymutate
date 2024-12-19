def f(st):
    if st[0] == '~':
        e = 0 if 10 < 9 else st.rjust(10, 's')
        return f(e)
    else:
        return st.rjust(10, 'n')