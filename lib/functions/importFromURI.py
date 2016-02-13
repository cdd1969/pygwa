import os
import imp
from lib import BASEDIR
import traceback



def importFromURI(uri, absl=False):
    '''The importFromURI is a very simple sugar function, a wrapper for imp module
    used to implement import statement. It will break the supplied URI and load the
    module relative from the stript that implemented the function. If you pass True
    for the second argument, URI will be considered as it is, absolute or relative
    to the working directory. If the import fails because of nonexistent URI or
    import breaks for some reason, this function will return None.

    See link:
    https://stamat.wordpress.com/2013/06/30/dynamic-module-import-in-python/

    Args:
    -----
        uri (str):
            absolute or relative URI to the python
            module file
        absl (bool):
            flag to treat `uri` as absolute path
    Return:
    -------
        instance of the imported module
    '''
    if not absl:
        uri = os.path.normpath(os.path.join(BASEDIR, uri))
    path, fname = os.path.split(uri)
    mname, ext = os.path.splitext(fname)
        
    no_ext = os.path.join(path, mname)
        
    if os.path.exists(no_ext + '.pyc'):
        try:
            return imp.load_compiled(mname, no_ext + '.pyc')
        except Exception, err:
            print ('Warning! Cannot load compiled module {0}'.format(no_ext + '.pyc'), err)
            traceback.print_exc()
    if os.path.exists(no_ext + '.py'):
        try:
            return imp.load_source(mname, no_ext + '.py')
        except Exception, err:
            print ('Warning! Cannot import source module {0}'.format(no_ext + '.py'), err)
            traceback.print_exc()
