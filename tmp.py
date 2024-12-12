def f(st):
    if st[(5 + -5)] == '~':
        e = st.rjust((9 + 1), 's')
        return f(e)
    else:
        return st.rjust((96 + -86), 'n')