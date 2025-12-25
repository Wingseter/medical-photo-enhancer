"""
Batch Processing Worker - QThread for processing multiple images through a workflow.
"""
import cv2
import os
import traceback
from pathlib import Path
from typing import List, Dict

from PySide6.QtCore import QThread, Signal

from node_editor.core.node_graph import NodeGraph
from node_editor.nodes import NODE_TYPES


class BatchProcessingWorker(QThread):
    """Worker thread for processing multiple images through a workflow."""

    progress = Signal(int, int, str)         # current, total, filename
    image_completed = Signal(str, object)    # output_path, result_image (numpy)
    finished = Signal()
    error = Signal(str)

    def __init__(
        self,
        workflow_data: Dict,
        image_paths: List[str],
        output_folder: str
    ):
        super().__init__()
        self.workflow_data = workflow_data
        self.image_paths = image_paths
        self.output_folder = output_folder
        self._is_running = True

    def run(self):
        try:
            # Ensure output folder exists
            os.makedirs(self.output_folder, exist_ok=True)

            total = len(self.image_paths)

            for idx, image_path in enumerate(self.image_paths):
                if not self._is_running:
                    break

                filename = Path(image_path).name
                self.progress.emit(idx + 1, total, filename)

                try:
                    result = self._process_single_image(image_path)

                    if result is not None:
                        # Generate output filename
                        stem = Path(image_path).stem
                        suffix = Path(image_path).suffix or ".png"
                        output_filename = f"{stem}_processed{suffix}"
                        output_path = os.path.join(self.output_folder, output_filename)

                        # Handle duplicate filenames
                        counter = 1
                        while os.path.exists(output_path):
                            output_filename = f"{stem}_processed_{counter}{suffix}"
                            output_path = os.path.join(self.output_folder, output_filename)
                            counter += 1

                        # Convert RGB to BGR for OpenCV saving
                        if len(result.shape) == 3:
                            result_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
                        else:
                            result_bgr = result

                        cv2.imwrite(output_path, result_bgr)
                        self.image_completed.emit(output_path, result)

                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    traceback.print_exc()

            self.finished.emit()

        except Exception as e:
            self.error.emit(f"Batch processing failed:\n{traceback.format_exc()}")

    def _process_single_image(self, image_path: str):
        """
        Process a single image through the workflow.
        Creates a fresh graph for each image to avoid state issues.
        """
        # Create fresh graph
        graph = NodeGraph()

        # Recreate from workflow
        id_mapping = graph.recreate_from_workflow(self.workflow_data, NODE_TYPES)

        # Find input node(s) and set the image path
        input_node_ids = self.workflow_data.get('execution', {}).get('input_node_ids', [])

        for old_id in input_node_ids:
            new_id = id_mapping.get(old_id)
            if new_id:
                node = graph.get_node(new_id)
                if node and 'filepath' in node.parameters:
                    node.parameters['filepath']['value'] = image_path
                    node.set_dirty()

        # Find output node and execute
        output_node_id = self.workflow_data.get('execution', {}).get('output_node_id')
        if output_node_id:
            new_output_id = id_mapping.get(output_node_id)
            if new_output_id:
                return graph.execute_graph(new_output_id)

        return None

    def stop(self):
        """Request the worker to stop."""
        self._is_running = False
