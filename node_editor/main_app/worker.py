from PySide6.QtCore import QObject, QThread, Signal
import traceback

class GraphExecutionWorker(QThread):
    """
    A QThread worker for executing the node graph in the background
    to prevent the GUI from freezing.
    """
    result_ready = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, graph, target_node_id):
        super().__init__()
        self.graph = graph
        self.target_node_id = target_node_id
        self.is_running = True

    def run(self):
        try:
            result = self.graph.execute_graph(self.target_node_id)
            if self.is_running:
                self.result_ready.emit(result)
        except Exception as e:
            error_msg = f"An error occurred during graph execution:\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)

    def stop(self):
        self.is_running = False
