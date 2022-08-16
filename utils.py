import csv

# read .csv files into dictionary tables
# multiple tables can be put in a single file by placing the table name as a single word before the table
# several names can share the same table by placing all the names as a single word line above the table
def csv2dict(filename, defaultTableMame, fieldsnamed=True):
    with open(filename) as fp:
        reader = csv.reader(
            fp,
            skipinitialspace=True,
            dialect='unix',
            quoting=csv.QUOTE_NONNUMERIC,
        )
        tables = {}
        newTable = False
        firstTime = True
        result = {}
        #if fieldsnamed:
            # skip the first line
        #    next(reader)
        for line_list in reader:
            if len(line_list) == 0:
                continue
            elif len(line_list) == 1:
                if newTable == False:
                    result = {}
                    newTable = True
                tables[line_list[0]] = result
                continue
            if newTable or firstTime:
                if firstTime:
                    tables[defaultTableMame] = result
                    firstTime = False
                newTable = False
                if fieldsnamed:
                    continue
            result[line_list[0]] = tuple(line_list[1:])
        return tables
