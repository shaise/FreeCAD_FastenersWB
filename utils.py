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
        tables['titles'] = {}
        newTable = False
        firstTime = True
        cur_table = {}
        table_names = { defaultTableMame }
        
        #if fieldsnamed:
            # skip the first line
        #    next(reader)
        for line_list in reader:
            if len(line_list) == 0:
                continue
            elif len(line_list) == 1:
                tablename = line_list[0]
                if newTable == False:
                    cur_table = {}
                    table_names = set()
                    newTable = True
                table_names.add(tablename)                
                continue
            key = line_list[0]
            data = tuple(line_list[1:])
            if newTable or firstTime:
                firstTime = False
                newTable = False
                for tablename in table_names:
                    tables[tablename] = cur_table
                if fieldsnamed:
                    for tablename in table_names:
                        tables['titles'][tablename] = data
                    continue
            cur_table[key] = data
        return tables
