from PySide6.QtCore import QThread, Signal
import traceback


class GraphExecutionWorker(QThread):
    """
    A QThread worker for executing the node graph in the background
    to prevent the GUI from freezing. Includes progress reporting.
    """
    result_ready = Signal(object)
    error_occurred = Signal(str)
    progress_update = Signal(str, str, int)  # (message, detail, percent)

    def __init__(self, graph, target_node_id):
        super().__init__()
        self.graph = graph
        self.target_node_id = target_node_id
        self.is_running = True

    def run(self):
        try:
            target_node = self.graph.get_node(self.target_node_id)
            if not target_node:
                self.error_occurred.emit(f"Node not found: {self.target_node_id}")
                return

            # Count nodes to execute for progress
            nodes_to_execute = self._get_execution_order(target_node)
            total = len(nodes_to_execute)

            if total == 0:
                # All nodes are cached
                self.progress_update.emit("Using cached results...", "", 100)
                if self.is_running:
                    self.result_ready.emit(target_node.cached_data)
                return

            for i, node in enumerate(nodes_to_execute):
                if not self.is_running:
                    return

                percent = int((i / total) * 100)
                self.progress_update.emit(
                    f"Executing {node.name}...",
                    f"Step {i + 1} of {total}",
                    percent
                )

                # Execute single node
                node.execute()

            # Final 100%
            self.progress_update.emit("Complete", "", 100)

            if self.is_running:
                self.result_ready.emit(target_node.cached_data)

        except Exception as e:
            error_msg = f"An error occurred during graph execution:\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)

    def _get_execution_order(self, target_node, visited=None):
        """Get nodes in execution order (topological sort) that need execution."""
        if visited is None:
            visited = set()

        order = []
        if target_node.id in visited:
            return order

        visited.add(target_node.id)

        # Process inputs first (dependencies)
        for input_node in target_node.inputs:
            order.extend(self._get_execution_order(input_node, visited))

        # Add this node if it needs execution
        if target_node.is_dirty or target_node.cached_data is None:
            order.append(target_node)

        return order

    def stop(self):
        self.is_running = False
