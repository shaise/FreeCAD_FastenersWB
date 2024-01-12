# this file hold aliases of fastener types.
# so, in any case there are similar fastener types with just different name,
# or several differen types use the same icon, this table give a way to reuse the data

# to add a new aliass add it in the tables here, then:
# on FastenersCmd.py in FSScrewCommandTable table add an apropriate line.


# a table to reuse icons:
FSIconAliases = {
    'ASMEB18.2.2.4A' : 'ASMEB18.2.2.1A',
    'DIN84' : 'ISO1207',
    'DIN961' : 'ISO8676',
    'DIN933' : 'ISO4017',
    'DIN934' : 'ISO4032',
    'GOST11860-1' : 'DIN1587',
    'GOST1144-1' : 'DIN96',
    'GOST1144-2' : 'DIN96',
    'GOST1144-3' : 'DIN7996',
    'GOST1144-4' : 'DIN7996',
    'ISO299' : 'DIN508',
    'ISO4766' : 'ISO4026',
    'ISO7380-1' : 'ISO7380',
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
