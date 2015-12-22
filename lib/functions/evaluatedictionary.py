#!/usr/bin python
# -*- coding: utf-8 -*-
import inspect
from datetime import datetime  #this is requred to use <readCSV_Node> parse_dates argument, since it usually has datetime



def evaluationFunction(dictionary, function4arguments=None, validArgumnets=None, log=False):
    """ function will evaluate (apply python-native function *eval()*) passed dictionary,
        taking only those entries, which have key that match passed *function4arguments*'s
        argument names or will take ALL dictionary entries if *function4arguments* is None


        NOTE !!!! Dictionary must not be nested

        Args:
        ------
            dictionary (dict):
                input dictionary, NOT NESTED! to take our parameters from.
                this dictionary should contain at least two entries: `name` and `value`.
                Because the evaluation is based on these two keys.
                    {'name': 'blabla',  <- MANDATORY KEYS!
                     'value': 'hallo',  <- MANDATORY KEYS!
                      ...}

            function4arguments (Optional[function or method]):
                Default None.
                function or method, from which the default argument's names will be gathered.
                Afterwads these argument-names will be compared with value for `name` entrie
                in `dictionary`. If `None` - the `name` will not be compared to anything, but
                will be treated as valid
        
            validArgumnets (Optional[list[str]]):
                Default None
                If not `None` - the argument `function4arguments` will be ignored, and the
                list of valid `name`s is passed explicitly with this argument

        Returns:
        --------
            stateArgs (dict):
                dictionary with one entry: key - is the name of the parameter; value - value
                of this parameter


        Examlple:
        ---------
            Lets imagine we have three different dictionaries that we will feed to this function
            <Input>
            -------
            <<< function4arguments = read_file(fname, skiprows=0, header=None, usecols=None)

            <<< d1 = { 'name': 'fname',
                       'value': '/home/path/to/file.csv'}
            <<< d2 = { 'name': 'create_backup',
                       'value': 'True',
                       'default': False}
            <<< d3 = { 'name': 'skiprows',
                       'value': '[3, 5, 6, 7]',    #Note! String!
                       'tooltip': 'helloworld'}

            <Output>
            -------
            <<< evaluationFunction(d1, function4arguments)
            >>> {'fname': '/home/path/to/file.csv'}
            
            <<< evaluationFunction(d2, function4arguments)
            >>> None
            
            <<< evaluationFunction(d3, function4arguments)
            >>> {'skiprows': [3, 5, 6, 7]}  #Note! not string!

    """
    if not inspect.isfunction(function4arguments) and not inspect.ismethod(function4arguments):
        if function4arguments is not None:
            raise ValueError('Argument passed is not a function, method or None. Received type: {0}'.format(type(function4arguments)))
        
    nameArgFound = False
    for name in ['name', u'name']:
        if name in dictionary.keys():
            nameArgFound = True
    if not nameArgFound:
        return None


    if function4arguments is not None:
        defaultArgNames = inspect.getargspec(function4arguments).args
    else:
        defaultArgNames = list()
    
    if validArgumnets is not None:
        defaultArgNames = validArgumnets

    if log:
        print 'evaluationFunction(): default args of function/method <{0}>'.format(str(function4arguments))
        print 'evaluationFunction(): {0}'.format(defaultArgNames)
    
    stateArgs = None
    # if passed argument name is in defauklt argument names
    if dictionary['name'] in defaultArgNames or (function4arguments is None and validArgumnets is not None):
        stateArgs = dict()
        # save value from passed state...
        if dictionary['value'] in ['', u'']:  #if emty line
            val = dictionary['default']
        else:
            try:
                val = eval(dictionary['value'])
            except Exception, err:
                if log: print Exception, err, '. Received:', dictionary['name'], '=', dictionary['value'],  '>>> I will set value without evaluation'
                val = dictionary['value']


        stateArgs[dictionary['name']] = val
    return stateArgs




def evaluateDict(dictionary, functionToDicts=None, functionToEntries=None, recursionResult=None, log=False, **kwargs):
    """ this is a recursion go through all children of a passed dictionary

        user can optionally toggle execution of a user-defined functions what will be
        run for DICTs and other DTYPEs seperately.

        <recursionResult> should not be passed by user!!! It is used internally by the recursion
        
        Note, that both <functionToDicts> and <functionToEntries> must have one mandatory
        argument <v>.

        **kwargs are passed to <functionToDicts>, <functionToEntries> functions!
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
        res_i = functionToDicts(dictionary, **kwargs)
        if res_i is not None:
            recursionResult.append(res_i)

    # go through root-dict children and apply functions there
    for n, v in dictionary.iteritems():
        if isinstance(v, dict):
            if functionToDicts is not None:
                if log: print 'dict <{0}>: entry <{1}> {2}, applying functionToDict'.format(id(dictionary), n, type(v))
                res_i = functionToDicts(v, **kwargs)
                if res_i is not None:
                    recursionResult.append(res_i)

            if log: print 'dict <{0}>: entry <{1}> {2}, entering recursion'.format(id(dictionary), n, type(v))
            evaluateDict(v, functionToDicts=functionToDicts, functionToEntries=functionToEntries, recursionResult=recursionResult, log=log, **kwargs)
        else:
            if functionToEntries is not None:
                if log: print 'dict <{0}>: entry <{1}> {2} = {3}, applying functionToEntries'.format(id(dictionary), n, type(v), v)
                res_i = functionToEntries(v, **kwargs)
                if res_i is not None:
                    recursionResult.append(res_i)
    return recursionResult
