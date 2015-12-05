import inspect


def evaluateDict(dictionary, functionToDicts=None, functionToEntries=None, recursionResult=None, log=False):
    """ this is a recursion go through all children of a passed dictionary

        user can optionally toggle execution of a user-defined functions what will be
        run for DICTs and other DTYPEs seperately.

        <recursionResult> should not be passed by user!!! It is used internally by the recursion
        
        Note, that both <functionToDicts> and <functionToEntries> must have one mandatory
        argument <v>.
    """
    if functionToDicts is not None and not inspect.isfunction(functionToDicts):
        raise ValueError('Passed argument is not a function. Received type: {0}'.format(type(functionToDicts)))
    if functionToEntries is not None and not inspect.isfunction(functionToEntries):
        raise ValueError('Passed argument is not a function. Received type: {0}'.format(type(functionToEntries)))
    if not isinstance(dictionary, dict):
        raise ValueError('Passed argument is not a dictionary. Received type: {0}'.format(type(dictionary)))
    if not isinstance(recursionResult, (list, type(None))):
        raise ValueError('Passed argument is not a list or None. Received type: {0}'.format(type(recursionResult)))
    

    if recursionResult is None:
        recursionResult = list()

    # apply function to root-level dictionary
    if functionToDicts is not None and not recursionResult:
        if log: print 'dict <{0}>: applying functionToDict'.format(id(dictionary))
        res_i = functionToDicts(dictionary)
        if res_i is not None:
            recursionResult.append(res_i)

    # go through root-dict children and apply functions there
    for n, v in dictionary.iteritems():
        if isinstance(v, dict):
            if functionToDicts is not None:
                if log: print 'dict <{0}>: entry <{1}> {2}, applying functionToDict'.format(id(dictionary), n, type(v))
                res_i = functionToDicts(v)
                if res_i is not None:
                    recursionResult.append(res_i)

            if log: print 'dict <{0}>: entry <{1}> {2}, entering recursion'.format(id(dictionary), n, type(v))
            evaluateDict(v, functionToDicts=functionToDicts, functionToEntries=functionToEntries, recursionResult=recursionResult, log=log)
        else:
            if functionToEntries is not None:
                if log: print 'dict <{0}>: entry <{1}> {2} = {3}, applying functionToEntries'.format(id(dictionary), n, type(v), v)
                res_i = functionToEntries(v)
                if res_i is not None:
                    recursionResult.append(res_i)
    return recursionResult
