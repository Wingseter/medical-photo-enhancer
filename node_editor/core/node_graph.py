import uuid

class Node:
    def __init__(self, name, params=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.inputs = []
        self.outputs = []
        self.parameters = params if params is not None else {}
        self.cached_data = None
        self._is_dirty = True

    def add_input(self, node):
        if node not in self.inputs:
            self.inputs.append(node)
            node.outputs.append(self)
            self.set_dirty()

    def remove_input(self, node):
        if node in self.inputs:
            self.inputs.remove(node)
            node.outputs.remove(self)
            self.set_dirty()

    @property
    def is_dirty(self):
        return self._is_dirty

    def set_dirty(self, dirty=True):
        if self._is_dirty == dirty:
            return
        self._is_dirty = dirty
        if dirty:
            self.cached_data = None
            for output_node in self.outputs:
                output_node.set_dirty(True)

    def get_parameter(self, name):
        return self.parameters.get(name, {}).get('value')

    def set_parameter(self, name, value):
        if name in self.parameters:
            if self.parameters[name]['value'] != value:
                self.parameters[name]['value'] = value
                self.set_dirty()
        else:
            raise KeyError(f"Parameter '{name}' not found in node '{self.name}'")

    def process(self, input_data):
        raise NotImplementedError

    def execute(self):
        if not self.is_dirty and self.cached_data is not None:
            return self.cached_data

        input_data = [parent.execute() for parent in self.inputs]
        
        if any(data is None for data in input_data) and self.name != "Input":
            print(f"Warning: Node '{self.name}' has missing input data. Skipping process.")
            return None

        try:
            print(f"Executing node: {self.name} ({self.id})")
            self.cached_data = self.process(input_data)
            self.set_dirty(False)
        except Exception as e:
            print(f"Error processing node {self.name}: {e}")
            self.cached_data = None

        return self.cached_data


class NodeGraph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node_class, *args, **kwargs):
        node = node_class(*args, **kwargs)
        self.nodes[node.id] = node
        return node

    def get_node(self, node_id):
        return self.nodes.get(node_id)

    def connect(self, output_node_id, input_node_id):
        output_node = self.get_node(output_node_id)
        input_node = self.get_node(input_node_id)
        if output_node and input_node:
            # Prevent cycles (simple check: if input_node is already an output of output_node)
            if input_node in output_node.outputs:
                print(f"Warning: Cycle detected or already connected between {output_node.name} and {input_node.name}")
                return False
            
            input_node.add_input(output_node)
            return True
        return False
        
    def disconnect(self, output_node_id, input_node_id):
        output_node = self.get_node(output_node_id)
        input_node = self.get_node(input_node_id)
        if output_node and input_node:
            input_node.remove_input(output_node)

    def execute_graph(self, end_node_id):
        end_node = self.get_node(end_node_id)
        if not end_node:
            print(f"Error: End node with ID '{end_node_id}' not found.")
            return None
        return end_node.execute()
