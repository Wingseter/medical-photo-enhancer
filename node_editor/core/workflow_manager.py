"""
Workflow Manager for saving, loading, and listing node graph workflows.
"""
import json
import os
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from PySide6.QtGui import QPixmap
from PySide6.QtCore import QByteArray, QBuffer, Qt


class WorkflowManager:
    """Manages workflow saving, loading, and listing."""

    DEFAULT_WORKFLOWS_DIR = Path(__file__).parent.parent / "workflows"

    def __init__(self, workflows_dir: Optional[str] = None):
        self.workflows_dir = Path(workflows_dir) if workflows_dir else self.DEFAULT_WORKFLOWS_DIR
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

    def save_workflow(
        self,
        name: str,
        graph,
        node_widgets: dict,
        description: str = "",
        thumbnail: Optional[QPixmap] = None
    ) -> str:
        """
        Save a workflow to a JSON file.

        Args:
            name: Workflow name
            graph: NodeGraph instance
            node_widgets: Dict mapping node_id to NodeWidget for position/size
            description: Optional description
            thumbnail: Optional QPixmap thumbnail

        Returns:
            The filepath of the saved workflow.
        """
        workflow_data = {
            "metadata": {
                "name": name,
                "description": description,
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "thumbnail": self._pixmap_to_base64(thumbnail) if thumbnail else None
            },
            "nodes": [],
            "connections": [],
            "execution": {
                "output_node_id": None,
                "input_node_ids": []
            }
        }

        # Collect node data
        for node_id, node in graph.nodes.items():
            position = {"x": 0, "y": 0}
            size = {"width": 180, "height": 100}

            # Get position and size from widget if available
            if node_id in node_widgets:
                widget = node_widgets[node_id]
                pos = widget.pos()
                position = {"x": pos.x(), "y": pos.y()}
                size = {"width": widget.width, "height": widget.height}

            node_data = {
                "id": node_id,
                "type": node.name,
                "position": position,
                "size": size,
                "parameters": {}
            }

            # Copy parameter values
            for param_name, param_props in node.parameters.items():
                node_data["parameters"][param_name] = {
                    "type": param_props.get("type"),
                    "value": param_props.get("value"),
                    "range": param_props.get("range"),
                    "step": param_props.get("step")
                }

            workflow_data["nodes"].append(node_data)

            # Track input/output nodes for execution hints
            if node.name == "Input":
                workflow_data["execution"]["input_node_ids"].append(node_id)
            elif node.name == "Output":
                workflow_data["execution"]["output_node_id"] = node_id

        # Collect connections (from output to input)
        for node_id, node in graph.nodes.items():
            for input_node in node.inputs:
                workflow_data["connections"].append({
                    "from_node": input_node.id,
                    "to_node": node_id
                })

        # Save to file
        filename = self._sanitize_filename(name) + ".json"
        filepath = self.workflows_dir / filename

        # Handle duplicate names
        counter = 1
        while filepath.exists():
            filename = f"{self._sanitize_filename(name)}_{counter}.json"
            filepath = self.workflows_dir / filename
            counter += 1

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def load_workflow(self, filepath: str) -> Dict:
        """Load a workflow from a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_workflows(self) -> List[Dict]:
        """List all available workflows with metadata."""
        workflows = []

        for filepath in self.workflows_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_filepath'] = str(filepath)
                    workflows.append(data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading workflow {filepath}: {e}")

        # Sort by updated_at descending
        workflows.sort(
            key=lambda w: w.get('metadata', {}).get('updated_at', ''),
            reverse=True
        )

        return workflows

    def delete_workflow(self, filepath: str) -> bool:
        """Delete a workflow file."""
        try:
            os.remove(filepath)
            return True
        except OSError:
            return False

    def get_thumbnail(self, workflow_data: Dict) -> Optional[QPixmap]:
        """Extract thumbnail from workflow data."""
        thumb_str = workflow_data.get('metadata', {}).get('thumbnail')
        if thumb_str:
            return self._base64_to_pixmap(thumb_str)
        return None

    def _sanitize_filename(self, name: str) -> str:
        """Convert name to safe filename."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name.strip()

    def _pixmap_to_base64(self, pixmap: QPixmap) -> str:
        """Convert QPixmap to base64 string."""
        if pixmap is None or pixmap.isNull():
            return ""

        # Scale down for storage
        scaled = pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QBuffer.WriteOnly)
        scaled.save(buffer, "PNG")

        return f"data:image/png;base64,{base64.b64encode(byte_array.data()).decode()}"

    def _base64_to_pixmap(self, base64_str: str) -> Optional[QPixmap]:
        """Convert base64 string back to QPixmap."""
        if not base64_str or not base64_str.startswith("data:image"):
            return None

        try:
            _, data = base64_str.split(",", 1)
            image_data = base64.b64decode(data)

            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            return pixmap
        except Exception:
            return None
