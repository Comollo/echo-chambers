# define some common useful functions


def border_msg(msg):
    """
    Print your message in a nice border

    Parameter
    ---------
    msg : string, integer, float
    """
    row = len(msg)
    h = ''.join(['+'] + ['-' * row] + ['+'])
    if type(msg) == str:
        pass
    else:
        msg = str(msg)
    result = h + '\n'"|" + msg + "|"'\n' + h
    print(result)


def print_element(iterable):
    """
    Print the element of your iterable object

    Parameter
    ---------
    iterable : list, dict, set
    """
    for element in iterable:
        print(element)
