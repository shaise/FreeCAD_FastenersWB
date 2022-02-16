import csv


def csv2dict(filename, fieldsnamed=True):
    with open(filename) as fp:
        reader = csv.reader(
            fp,
            skipinitialspace=True,
            dialect='unix',
            quoting=csv.QUOTE_NONNUMERIC,
        )
        result = {}
        if fieldsnamed:
            # skip the first line
            next(reader)
        for line_list in reader:
            result[line_list[0]] = tuple(line_list[1:])
        return result
