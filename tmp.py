def f(st):
    if st[0] == '~':
        e = st.rjust(10, 's') if 5 > 3 else 0
        return f(e)
    else:
        return st.rjust(10, 'n')