import importlib
import copy
from .node import Node
from .taskSpecSchema import TaskSpecSchema
import os

__all__ = ['Task']

DEFAULT_MODULE = os.getenv('GQUANT_PLUGIN_MODULE', "gquant.plugin_nodes")
MODLIB = importlib.import_module(DEFAULT_MODULE)


class Task(object):
    ''' A strong typed Task class that is converted from dictionary.
    '''

    def __init__(self, task_spec):

        self._task_spec = {}  # internal dict

        # whatever is passed in has to be valid
        TaskSpecSchema.validate(task_spec)
        self._task_spec = copy.copy(task_spec)
        # deepcopies of inputs can still be done
        self._task_spec[TaskSpecSchema.inputs] = \
            copy.deepcopy(task_spec[TaskSpecSchema.inputs])

    def __getitem__(self, key):
        return self._task_spec[key]

    def get(self, key, default=None):
        return self._task_spec.get(key, default)

    def get_node_obj(self, replace=None):
        """
        instantiate a node instance for this task given the replacement setup

        Arguments
        -------
        replace: dict
            conf parameters replacement

        Returns
        -----
        object
            Node instance
        """
        task_spec = copy.copy(self._task_spec)
        task_spec.update(replace)

        node_id = task_spec[TaskSpecSchema.task_id]
        modulepath = task_spec.get(TaskSpecSchema.filepath)

        node_type = task_spec[TaskSpecSchema.node_type]
        task = Task(task_spec)

        if isinstance(node_type, str):
            if modulepath is not None:
                spec = importlib.util.spec_from_file_location(node_id,
                                                              modulepath)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                NodeClass = getattr(mod, node_type)
            else:
                global MODLIB
                NodeClass = getattr(MODLIB, node_type)
        elif issubclass(node_type, Node):
            NodeClass = node_type
        else:
            raise "Not supported"

        node = NodeClass(task)
        return node


if __name__ == "__main__":
    t = {'id': 'test',
         'type': "DropNode",
         'conf': {},
         'inputs': ["node_other"]}
    task = Task(t)
