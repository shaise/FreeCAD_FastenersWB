import csv

# read .csv files into dictionary tables
# multiple tables can be put in a single file by placing the table name as a single word before the table
def csv2dict(filename, tableMame, fieldsnamed=True):
    with open(filename) as fp:
        reader = csv.reader(
            fp,
            skipinitialspace=True,
            dialect='unix',
            quoting=csv.QUOTE_NONNUMERIC,
        )
        tables = {}
        curTableName = tableMame
        newTable = True
        result = {}
        #if fieldsnamed:
            # skip the first line
        #    next(reader)
        for line_list in reader:
            if len(line_list) == 0:
                continue
            elif len(line_list) == 1:
                newTable = True
                curTableName = line_list[0]
                result = {}
                continue
            if newTable:
                newTable = False
                tables[curTableName] = result
                if fieldsnamed:
                    continue
            result[line_list[0]] = tuple(line_list[1:])
        return tables
