from . import machines


VERSION = (0, 1, 0, 'a', 0)


# Thanks again, Django.
def get_version(version=VERSION):
    "Returns a PEP 386-compliant version number from VERSION."
    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')

    parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:parts])

    if version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]] + str(version[4])

    return str(main + sub)
