"""
History Manager - Undo/Redo system with time-travel debugging

Tracks all actions and allows reverting to previous states.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import copy


class ActionType(Enum):
    """Types of actions that can be undone"""
    MODE_CHANGE = "mode_change"
    MIDI_SEND = "midi_send"
    PRESET_LOAD = "preset_load"
    SETTING_CHANGE = "setting_change"
    AI_GENERATION = "ai_generation"
    FILE_OPERATION = "file_operation"
    NETWORK_ACTION = "network_action"
    AUDIO_PROCESS = "audio_process"
    VIEW_CHANGE = "view_change"


@dataclass
class Action:
    """Represents a single action in history"""
    id: str
    action_type: ActionType
    description: str
    timestamp: datetime
    previous_state: Dict[str, Any]
    new_state: Dict[str, Any]
    undo_callback: Optional[Callable] = None
    redo_callback: Optional[Callable] = None
    undoable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "action_type": self.action_type.value,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "undoable": self.undoable
        }


class HistoryManager:
    """
    Manages action history for undo/redo

    Features:
    - Unlimited undo/redo
    - Time-travel to any point in history
    - Action grouping (batch undo)
    - History browsing
    - State snapshots
    - Selective undo (undo specific actions)
    """

    def __init__(self, max_history: int = 1000):
        """
        Initialize history manager

        Args:
            max_history: Maximum number of actions to keep in history
        """
        self.max_history = max_history

        # History stacks
        self.history: List[Action] = []
        self.redo_stack: List[Action] = []

        # Current state snapshot
        self.current_state: Dict[str, Any] = {}

        # Action counter for IDs
        self._action_counter = 0

        # Batch mode for grouping actions
        self._batch_mode = False
        self._batch_actions: List[Action] = []
        self._batch_description = ""

    def record_action(
        self,
        action_type: ActionType,
        description: str,
        previous_state: Dict[str, Any],
        new_state: Dict[str, Any],
        undo_callback: Optional[Callable] = None,
        redo_callback: Optional[Callable] = None,
        undoable: bool = True
    ) -> Action:
        """
        Record a new action in history

        Args:
            action_type: Type of action
            description: Human-readable description
            previous_state: State before action
            new_state: State after action
            undo_callback: Optional callback to execute on undo
            redo_callback: Optional callback to execute on redo
            undoable: Whether action can be undone

        Returns:
            Created action
        """
        action = Action(
            id=self._generate_action_id(),
            action_type=action_type,
            description=description,
            timestamp=datetime.now(),
            previous_state=copy.deepcopy(previous_state),
            new_state=copy.deepcopy(new_state),
            undo_callback=undo_callback,
            redo_callback=redo_callback,
            undoable=undoable
        )

        # If in batch mode, add to batch instead
        if self._batch_mode:
            self._batch_actions.append(action)
            return action

        # Add to history
        self.history.append(action)

        # Clear redo stack (can't redo after new action)
        self.redo_stack.clear()

        # Trim history if needed
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        # Update current state
        self.current_state = copy.deepcopy(new_state)

        return action

    def _generate_action_id(self) -> str:
        """Generate unique action ID"""
        self._action_counter += 1
        return f"action_{self._action_counter}"

    def can_undo(self) -> bool:
        """Check if undo is possible"""
        if self._batch_mode:
            return False
        return len(self.history) > 0 and any(a.undoable for a in self.history)

    def can_redo(self) -> bool:
        """Check if redo is possible"""
        if self._batch_mode:
            return False
        return len(self.redo_stack) > 0

    def undo(self) -> Optional[Action]:
        """
        Undo the last action

        Returns:
            Undone action, or None if undo not possible
        """
        if not self.can_undo():
            return None

        # Find last undoable action
        action = None
        for i in range(len(self.history) - 1, -1, -1):
            if self.history[i].undoable:
                action = self.history.pop(i)
                break

        if not action:
            return None

        # Execute undo callback if available
        if action.undo_callback:
            try:
                action.undo_callback()
            except Exception as e:
                print(f"[HistoryManager] Error in undo callback: {e}")

        # Restore previous state
        self.current_state = copy.deepcopy(action.previous_state)

        # Add to redo stack
        self.redo_stack.append(action)

        return action

    def redo(self) -> Optional[Action]:
        """
        Redo the last undone action

        Returns:
            Redone action, or None if redo not possible
        """
        if not self.can_redo():
            return None

        action = self.redo_stack.pop()

        # Execute redo callback if available
        if action.redo_callback:
            try:
                action.redo_callback()
            except Exception as e:
                print(f"[HistoryManager] Error in redo callback: {e}")

        # Restore new state
        self.current_state = copy.deepcopy(action.new_state)

        # Add back to history
        self.history.append(action)

        return action

    def undo_multiple(self, count: int) -> List[Action]:
        """
        Undo multiple actions

        Args:
            count: Number of actions to undo

        Returns:
            List of undone actions
        """
        undone_actions = []
        for _ in range(count):
            action = self.undo()
            if action:
                undone_actions.append(action)
            else:
                break
        return undone_actions

    def redo_multiple(self, count: int) -> List[Action]:
        """
        Redo multiple actions

        Args:
            count: Number of actions to redo

        Returns:
            List of redone actions
        """
        redone_actions = []
        for _ in range(count):
            action = self.redo()
            if action:
                redone_actions.append(action)
            else:
                break
        return redone_actions

    def get_history(self, limit: Optional[int] = None) -> List[Action]:
        """
        Get action history

        Args:
            limit: Optional limit on number of actions

        Returns:
            List of actions (most recent first)
        """
        history = list(reversed(self.history))
        if limit:
            return history[:limit]
        return history

    def get_redo_stack(self, limit: Optional[int] = None) -> List[Action]:
        """
        Get redo stack

        Args:
            limit: Optional limit on number of actions

        Returns:
            List of redoable actions (most recent first)
        """
        stack = list(reversed(self.redo_stack))
        if limit:
            return stack[:limit]
        return stack

    def clear_history(self) -> None:
        """Clear all history"""
        self.history.clear()
        self.redo_stack.clear()

    def get_action_by_id(self, action_id: str) -> Optional[Action]:
        """Get action by ID from history or redo stack"""
        for action in self.history:
            if action.id == action_id:
                return action
        for action in self.redo_stack:
            if action.id == action_id:
                return action
        return None

    def undo_to_action(self, action_id: str) -> List[Action]:
        """
        Undo to a specific action (time-travel)

        Args:
            action_id: Action to undo back to

        Returns:
            List of undone actions
        """
        # Find action in history
        action_index = None
        for i, action in enumerate(self.history):
            if action.id == action_id:
                action_index = i
                break

        if action_index is None:
            return []

        # Undo all actions after this one
        num_to_undo = len(self.history) - action_index
        return self.undo_multiple(num_to_undo)

    def get_state_at_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        """
        Get state snapshot at a specific action

        Args:
            action_id: Action ID

        Returns:
            State at that point in history
        """
        action = self.get_action_by_id(action_id)
        if action:
            return action.new_state
        return None

    # ========== Batch Operations ==========

    def start_batch(self, description: str) -> None:
        """
        Start batch mode for grouping multiple actions

        Args:
            description: Description for the batch
        """
        self._batch_mode = True
        self._batch_actions.clear()
        self._batch_description = description

    def end_batch(self) -> Optional[Action]:
        """
        End batch mode and create single batch action

        Returns:
            Batch action containing all batched actions
        """
        if not self._batch_mode:
            return None

        self._batch_mode = False

        if not self._batch_actions:
            return None

        # Create batch action combining all actions
        first_action = self._batch_actions[0]
        last_action = self._batch_actions[-1]

        batch_action = Action(
            id=self._generate_action_id(),
            action_type=ActionType.FILE_OPERATION,  # Generic type
            description=f"Batch: {self._batch_description} ({len(self._batch_actions)} actions)",
            timestamp=datetime.now(),
            previous_state=first_action.previous_state,
            new_state=last_action.new_state,
            undoable=all(a.undoable for a in self._batch_actions)
        )

        # Add to history
        self.history.append(batch_action)
        self.redo_stack.clear()
        self.current_state = copy.deepcopy(batch_action.new_state)

        return batch_action

    def cancel_batch(self) -> None:
        """Cancel batch mode without creating batch action"""
        self._batch_mode = False
        self._batch_actions.clear()
        self._batch_description = ""

    # ========== Statistics ==========

    def get_stats(self) -> Dict[str, Any]:
        """Get history statistics"""
        return {
            "total_actions": len(self.history),
            "undoable_actions": sum(1 for a in self.history if a.undoable),
            "redo_available": len(self.redo_stack),
            "actions_by_type": self._count_by_type(),
            "oldest_action": self.history[0].timestamp.isoformat() if self.history else None,
            "newest_action": self.history[-1].timestamp.isoformat() if self.history else None
        }

    def _count_by_type(self) -> Dict[str, int]:
        """Count actions by type"""
        counts = {}
        for action in self.history:
            type_name = action.action_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts

    def get_recent_actions(self, minutes: int = 5) -> List[Action]:
        """
        Get actions from the last N minutes

        Args:
            minutes: Time window in minutes

        Returns:
            Recent actions
        """
        cutoff = datetime.now().timestamp() - (minutes * 60)
        return [
            action for action in self.history
            if action.timestamp.timestamp() > cutoff
        ]

    def export_history(self) -> List[Dict[str, Any]]:
        """
        Export history as JSON-serializable list

        Returns:
            List of action dictionaries
        """
        return [action.to_dict() for action in self.history]

    def create_snapshot(self, name: str) -> Dict[str, Any]:
        """
        Create a named snapshot of current state

        Args:
            name: Snapshot name

        Returns:
            Snapshot data
        """
        return {
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "state": copy.deepcopy(self.current_state),
            "action_count": len(self.history)
        }
