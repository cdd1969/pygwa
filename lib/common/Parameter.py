from pyqtgraph.parametertree import Parameter as pyqtgraphParameter
import logging
logger = logging.getLogger(__name__)

class customParameter(pyqtgraphParameter):
    """
    A Parameter is the basic unit of data in a parameter tree. Each parameter has
    a name, a type, a value, and several other properties that modify the behavior of the
    Parameter. Parameters may have parent / child / sibling relationships to construct
    organized hierarchies. Parameters generally do not have any inherent GUI or visual
    interpretation; instead they manage ParameterItem instances which take care of
    display and user interaction.
    
    Note: It is fairly uncommon to use the Parameter class directly; mostly you
    will use subclasses which provide specialized type and data handling. The static
    pethod Parameter.create(...) is an easy way to generate instances of these subclasses.

    For more Parameter types, see ParameterTree.parameterTypes module.
    
    ===================================  =========================================================
    **Signals:**
    sigStateChanged(self, change, info)  Emitted when anything changes about this parameter at
                                         all.
                                         The second argument is a string indicating what changed
                                         ('value', 'childAdded', etc..)
                                         The third argument can be any extra information about
                                         the change
    sigTreeStateChanged(self, changes)   Emitted when any child in the tree changes state
                                         (but only if monitorChildren() is called)
                                         the format of *changes* is [(param, change, info), ...]
    sigValueChanged(self, value)         Emitted when value is finished changing
    sigValueChanging(self, value)        Emitted immediately for all value changes,
                                         including during editing.
    sigChildAdded(self, child, index)    Emitted when a child is added
    sigChildRemoved(self, child)         Emitted when a child is removed
    sigRemoved(self)                     Emitted when this parameter is removed
    sigParentChanged(self, parent)       Emitted when this parameter's parent has changed
    sigLimitsChanged(self, limits)       Emitted when this parameter's limits have changed
    sigDefaultChanged(self, default)     Emitted when this parameter's default value has changed
    sigNameChanged(self, name)           Emitted when this parameter's name has changed
    sigOptionsChanged(self, opts)        Emitted when any of this parameter's options have changed
    ===================================  =========================================================
    """
    def __init__(self, **opts):
        super(customParameter, self).__init__(**opts)

    def children(self, child2observe=None, recursive=False, ignore_groups=False, ignore_actions=True):
        """Return a list of this parameter's children.

        In contrast to standard pyqtgraph method, it can list all nested children
        and ignore group parameters as well:

            To receive a list of ALL children and subchildren of this param:
                self.children(recursion=True)
            To receive a list of ALL children and subchildren of this param excluding groups:
                self.children(recursion=True, ignore_groups=True)

            To receive a list of ALL children and subchildren of param `SomeParam`:
                self.children(child2observe=SomeParam, recursion=True)

            If `child2observe`, `recursive`, `ignore_groups` are `False`:
                self.children() is the original method of pyqtgraphParameter.children()

        Args:
        -----
            child2observe(pyqtgraph.Parameter or None):
                optional keyword to search children not in `self` but in
                passed `Parameter` (eventhough it may be not the children `self`)
                If `None` will seach in `self`
            
            recursive (bool):
                flag to search all levels of nested widget (True) instead of
                searching the top-level (False)
            
            ignore_actions (bool):
                flag to ignore `action` parameters (i.e. pushbuttons)
            
            ignore_groups (bool):
                flag to ignore `group` parameters
        """
        if child2observe is None:
            child2observe = self
        children = child2observe.childs[:]

        if recursive:
            for child in children:
                if child.hasChildren():
                    children += self.children(child2observe=child, recursive=recursive)
        if ignore_groups:
            children = [child for child in children if not child.isType('group')]
        if ignore_actions:
            children = [child for child in children if not child.isType('action')]
        return children


    def childValue(self, *names, **opts):
            """ Get value of the child. Additionally may pass required datatype check and evaluation flag.

            To access the child-parameter pass the name of the child or a tuple (path, to, child) in `*names`
            in **opts you may pass two keywords: `datatype` and `evaluate`

            if `evaluate=True` - will try to evaluate value and check its datatype (see allowed dtypes)
            if `datatype=list` - will try to compare `dtype(value)` with `list`. If it is not - will return
                                `unicode(value)`
            """

            datatype = opts.get('datatype', None)
            evaluate = opts.get('evaluate', True)
            log = opts.get('log', False)
            child = self.child(*names)
            if hasattr(child, 'value') and callable(getattr(child, 'value')):
                childVal = child.value()
            else:
                raise KeyError('Parameter {0} does not have `.value()` method'.format(child))
                
            if evaluate:
                return self.evaluateValue(childVal, datatype=datatype, log=log)
            else:
                childValEval = childVal

            if datatype:
                allowed_datatypes = datatype
            else:
                allowed_datatypes = (str, unicode, list, tuple, dict, int, long, complex, float, bool, type(None))

            if isinstance(childValEval, allowed_datatypes):
                return childValEval
            else:
                if log: print ('Warning! Parameter {0} has value {1} of invalid type {2}. Must be one of these type : {4}. Will convert to unicode and return {3}'.format(child, childValEval, type(childValEval), unicode(childValEval), allowed_datatypes))
                return unicode(childValEval)

    def evaluateValue(self, value, datatype=None, log=False):
        """
        if `datatype=list` - will try to compare `dtype(value)` with `list`. If it is not - will return
                            `unicode(value)`
        """
        try:
            valueEval = eval(value)
        except:
            if log: print ('Warning! Cannot evaluate value {0} is of type {1}.'.format(value, type(value)))
            valueEval = value

        if datatype:
            allowed_datatypes = datatype
        else:
            allowed_datatypes = (str, unicode, list, tuple, dict, int, long, complex, float, bool, type(None))

        if isinstance(valueEval, allowed_datatypes):
            return valueEval
        else:
            if log: print ('Warning! Value {0} is of invalid type {1}. Must be one of these type : {3}. Will convert to unicode and return {2}'.format(valueEval, type(valueEval), unicode(valueEval), allowed_datatypes))
            return unicode(valueEval)

    def restoreState(self, state):
        logger.debug("restoring [{0}] param's state".format(self.name()))
        try:
            super(customParameter, self).restoreState(state)
        except Exception, err:
            logger.error("Failed to restore [{0}] param's state".format(self.name()), exc_info=True)
        logger.debug("[{0}] param's state restored".format(self.name()))