# this file hold aliases of fastener types.
# so, in any case there are similar fastener types with just different name,
# or several differen types use the same icon, this table give a way to reuse the data

# to add a new aliass add it in the tables here, then:
# on FastenersCmd.py in FSScrewCommandTable table add an apropriate line.


# a table to reuse icons:
FSIconAliases = {
    'ISO299' : 'DIN508',
    'ISO4766' : 'ISO4026',
    'ISO7049-C' : 'DIN7996',
    'ISO7049-R' : 'DIN7996',
    'ISO7434' : 'ISO4027',
    'ISO7435' : 'ISO4028',
    'ISO7436' : 'ISO4029',
}

# a table to reuse similar type standards
FSTypeAliases = {
    'ISO299' : 'DIN508',
}

def FSGetIconAlias(name):
    if name in FSIconAliases:
        return FSIconAliases[name]
    return name

def FSGetTypeAlias(type):
    if type in FSTypeAliases:
        return FSTypeAliases[type]
    return type

def FSAppendAliasesToTable(table):
    for item in FSTypeAliases.keys():
        table[item] = table[FSTypeAliases[item]]
