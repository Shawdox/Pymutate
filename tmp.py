def f(st):
    if not st[0] == '~':
        return st.rjust(10, 'n')
    else:
        e = st.rjust(10, 's')
        return f(e)