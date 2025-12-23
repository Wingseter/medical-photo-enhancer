import pkgutil
import inspect
from pathlib import Path
from node_editor.core.node_graph import Node

# --- Automatic Node Registration System ---

NODE_TYPES = {}

def register_nodes():
    """
    Dynamically imports all modules in this directory and registers any
    subclasses of the Node class. This makes the system plug-and-play.
    """
    if NODE_TYPES: # Already registered
        return

    package_dir = Path(__file__).resolve().parent
    for (_, module_name, _) in pkgutil.iter_modules([str(package_dir)]):
        # Import the module
        module = __import__(f"{__name__}.{module_name}", fromlist=["*"])
        
        # Find all Node subclasses in the imported module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Node) and obj is not Node:
                # Use the node's internal name for registration
                try:
                    instance = obj()
                    NODE_TYPES[instance.name] = obj
                    print(f"Successfully registered node: {instance.name}")
                except Exception as e:
                    print(f"Could not instantiate or register node {name}: {e}")

# Call registration function when this package is imported
register_nodes()