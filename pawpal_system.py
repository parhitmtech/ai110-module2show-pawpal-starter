"""
- pawpal_system.py
- Backend layer for the entire system
- Contains all the required classes: Owner, Pet, Task, Scheduler 
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"
    completed: bool = False

    def mark_completed(self) -> None:
        """Mark this task as completed"""
        pass

@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        pass

    def get_tasks(self) -> List[Task]:
        """Return the full list of tasks for this pet"""
        pass

@dataclass
class Owner:
    name: str
    available_minutes: int = 120
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list"""
        pass

    def get_pets(self) -> List[Pet]:
        """Return the list of pets this owner has."""
        pass

class Scheduler:
    
    def __init__(self, pet: Pet, available_minutes: int):
        self.pet = pet
        self.available_minutes = available_minutes

    def build_scheduler(self) -> List[Task]:
        """
        Select and order tasks based on priority and available time
        Returns a list of Task objects that fit within available_minutes
        """
        pass

    def explain_plan(self) -> List[str]:
        """
        Return a list of human-readable strings explaining the schedule
        Each string describes why a task was included or skipped
        """
        pass