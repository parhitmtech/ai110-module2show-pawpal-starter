"""
- pawpal_system.py
- Backend layer for the entire system
- Contains all the required classes: Owner, Pet, Task, Scheduler 
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional

# Priority Helpers

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

def _priority_rank(task: "Task") -> int:
    """Return a sort key for priority (lower = higher priority)."""
    return PRIORITY_ORDER.get(task.priority.lower(), 99)

@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"
    completed: bool = False
    notes: Optional[str] = None
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)

    def mark_completed(self) -> None:
        """Mark this task as completed"""
        self.completed = True
        if (self.frequency == "daily"):
            self.due_date = self.due_date + timedelta(days=1)
            self.completed = False  # reset so it appears tomorrow
        
        elif (self.frequency == "weekly"):
            self.due_date = self.due_date + timedelta(days=7)
            self.completed = False  # reset so it appears next week
    
    def mark_incomplete(self) -> None:
        """Reset this task to incomplete (useful for a new day)"""
        self.completed = False

    def is_due_today(self) -> bool:    
        """Check if task is due today or not"""               
        return self.due_date <= date.today()

    def __str__(self) -> str:
        status = "✓" if self.completed else "○"
        note = f"  ({self.notes})" if self.notes else ""
        return (
            f"[{status}] {self.title}"
            f"- {self.duration_minutes} min"
            f"| {self.priority.upper()} priority"
            f"{note}"
        )

@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: Task) -> bool:
        """Return the full list of tasks for this pet"""
        original_count = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.title != title]
        return len(self.tasks) < original_count

    def get_tasks(self) -> List[Task]:
        return self.tasks
    
    def get_pending_tasks(self) -> List[Task]:
        """Return only the tasks that have not been completed"""
        return [t for t in self.tasks if not t.completed]

    def get_completed_tasks(self) -> List[Task]:
        """Return only the tasks that have been completed"""
        return [t for t in self.tasks if t.completed]

    def total_task_minutes(self) -> int:
        """Return the total duration of all tasks for this pet in minutes"""
        return sum(t.duration_minutes for t in self.tasks)
    
    def __str__(self) -> str:
        """Return a readable one-line summary of the pet"""
        return (
            f"{self.name} ({self.species}, {self.age} yr) "
            f"- {len(self.tasks)} task(s)"
        )

@dataclass
class Owner:
    name: str
    available_minutes: int = 120
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list"""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> bool:
        original_count = len(self.pets)
        self.pets = [p for p in self.pets if p.name != name]
        return len(self.pets) < original_count

    def get_pets(self) -> List[Pet]:
        """Return the list of pets this owner has."""
        return self.pets
    
    def get_all_tasks(self) -> List[tuple]:
        """
        Return all tasks across all pets as (pet, task) tuples.
        This is what the Scheduler calls to get a unified task view
        """
        all_tasks = []
        for pet in self.pets:
            for task in pet.get_tasks():
                all_tasks.append((pet, task))
        return all_tasks
    
    def get_all_pending_tasks(self) -> List[tuple]:
        """
        Return all incomplete tasks across all pets as (pet, task) tuples
        """
        return [
            (pet, task)
            for pet, task in self.get_all_tasks()
            if not task.completed and task.is_due_today()
        ]
    
    def total_task_minutes(self) -> int:
        """Return total minutes of all tasks across all parts"""
        return sum(pet.total_task_minutes() for pet in self.pets)
    
    def filter_tasks(
            self,
            pet_name: Optional[str] = None,
            completed: Optional[bool] = None,
            priority: Optional[str] = None,
            frequency: Optional[str] = None,
    ) -> List[tuple]:
        results = self.get_all_tasks()

        if (pet_name is not None):
            results = [(p, t) for p, t in results if p.name == pet_name]

        if (completed is not None):
            results = [(p, t) for p, t in results if t.completed == completed]

        if (priority is not None):
            results = [(p, t) for p, t in results if t.priority == priority]

        if (frequency is not None):
            results = [(p, t) for p, t in results if t.frequency == frequency]

        return results
        
    def __str__(self) -> str:
        """Return a readable one-line summary of the owner."""
        return (
            f"{self.name} — {len(self.pets)} pet(s), "
            f"{self.available_minutes} min available today"
        )

@dataclass
class ScheduledItem:
    """
    A task that has been placed in a schedule with a start time attached
    """
    pet: Pet
    task: Task
    start_time: int

    @property
    def end_time(self) -> int:
        """Return the minute at which this task ends"""
        return self.start_time + self.task.duration_minutes
    
    def start_time_str(self) -> str:
        """Convert start_time minutes offset to a readable HH:MM string"""
        total = 480 + self.start_time
        hours, mins = divmod(total, 60)
        period = "AM" if hours < 12 else "PM"
        hours = hours if hours <= 12 else hours - 12
        return f"{hours}:{mins:02d} {period}"
    
    def end_time_str(self) -> str:
        """Convert end_time inutes offset to a readable HH:MM string"""
        total = 480 + self.end_time
        hours, mins = divmod(total, 60)
        period = "AM" if hours < 12 else "PM"
        hours  = hours if hours <= 12 else hours - 12
        return f"{hours}:{mins:02d} {period}"
    
    def __str__(self) -> str:
        """Return a formatted one-line schedule entry."""
        return (
            f"{self.start_time_str()} → {self.end_time_str()}  "
            f"[{self.task.priority.upper()}]  "
            f"{self.task.title} for {self.pet.name}"
        )

class Scheduler:
    
    def __init__(self, owner: Owner):
        """Initialize the class scheduler for a given owner"""
        self.owner = owner
        self.schedule: List[ScheduledItem] = []
        self.skipped: List[tuple] = []

    def build_schedule(self) -> List[ScheduledItem]:
        """
        Select and order tasks based on priority and available time
        Returns a list of Task objects that fit within available_minutes
        """
        self.schedule = []
        self.skipped = []

        pending = self.owner.get_all_pending_tasks()
 
        if not pending:
            return self.schedule
 
        # Sort: high priority first, then by duration ascending
        # (shorter tasks first within same priority = fit more tasks in)
        sorted_tasks = sorted(
            pending,
            key=lambda pt: (_priority_rank(pt[1]), pt[1].duration_minutes)
        )
 
        time_used = 0
        available = self.owner.available_minutes
 
        for pet, task in sorted_tasks:
            if time_used + task.duration_minutes <= available:
                item = ScheduledItem(
                    pet=pet,
                    task=task,
                    start_time=time_used,
                )
                self.schedule.append(item)
                time_used += task.duration_minutes
            else:
                remaining = available - time_used
                self.skipped.append((
                    pet,
                    task,
                    f"not enough time — needs {task.duration_minutes} min, "
                    f"only {remaining} min remaining"
                ))
 
        return self.schedule
    
    def sort_by_time(self) -> List[ScheduledItem]:
        return sorted(self.schedule, key=lambda item: item.start_time)
    
    def detect_conflicts(self) -> List[str]:
        warnings = []
        items = self.schedule

        for i in range(len(items)):
            for j in range(i+1, len(items)):
                a, b = items[i], items[j]
                # Overlap condition: a starts before b ends AND b starts before a ends
                if (a.start_time < b.end_time and b.start_time < a.end_time):
                    warnings.append(
                        f"Conflict: '{a.task.title}' for {a.pet.name} "
                        f"({a.start_time_str()} → {a.end_time_str()}) overlaps with "
                        f"'{b.task.title}' for {b.pet.name} "
                        f"({b.start_time_str()} → {b.end_time_str()})"
                    )
        return warnings

    def explain_plan(self) -> List[str]:
        """Return a list of human-readable strings explaining the full schedule."""
        if not self.schedule and not self.skipped:
            return ["No tasks found. Add some tasks to get started!"]
 
        lines = []
        lines.append(f"Daily Schedule for {self.owner.name}'s pets "
                     f"({self.owner.available_minutes} min available)")
        lines.append("─" * 55)
 
        if self.schedule:
            lines.append("Scheduled tasks:")
            for item in self.sort_by_time():
                lines.append(f"   {item}")
                if item.task.notes:
                    lines.append(f"      Note: {item.task.notes}")
            total = sum(i.task.duration_minutes for i in self.schedule)
            lines.append(f"\n   Total time: {total} min used "
                         f"of {self.owner.available_minutes} min available")
        else:
            lines.append("   No tasks could be scheduled.")
 
        if self.skipped:
            lines.append("\nSkipped tasks:")
            for pet, task, reason in self.skipped:
                lines.append(f"   {task.title} for {pet.name} "
                             f"({task.duration_minutes} min) — {reason}")
 
        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("\nConflicts detected:")
            for w in conflicts:
                lines.append(f"   {w}")
 
        lines.append("─" * 55)
        return lines
    
    def mark_all_complete(self) -> None:
        """Mark every scheduled task as completed"""
        for item in self.schedule:
            item.task.mark_completed()
    
    def get_summary(self) -> int:
        return {
            "owner_name":         self.owner.name,
            "available_minutes":  self.owner.available_minutes,
            "scheduled": [
                {
                    "pet":      item.pet.name,
                    "task":     item.task.title,
                    "priority": item.task.priority,
                    "duration": item.task.duration_minutes,
                    "start":    item.start_time_str(),
                    "end":      item.end_time_str(),
                    "notes":    item.task.notes or "",
                }
                for item in self.schedule
            ],
            "skipped": [
                {
                    "pet":      pet.name,
                    "task":     task.title,
                    "priority": task.priority,
                    "duration": task.duration_minutes,
                    "reason":   reason,
                }
                for pet, task, reason in self.skipped
            ],
            "total_minutes_used": sum(
                i.task.duration_minutes for i in self.schedule
            ),
        }