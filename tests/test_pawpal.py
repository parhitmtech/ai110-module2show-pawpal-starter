"""
tests/test_pawpal.py
--------------------
Automated tests for PawPal+ core logic.
Run with: python -m pytest tests/ -v
"""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler, ScheduledItem


# ══════════════════════════════════════════════════════════════════════════════
# Task Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestTask:

    def test_task_creation_defaults(self):
        """A new task should have completed=False and priority='medium' by default."""
        task = Task(title="Walk", duration_minutes=30)
        assert task.title            == "Walk"
        assert task.duration_minutes == 30
        assert task.priority         == "medium"
        assert task.completed        is False

    def test_mark_complete_changes_status(self):
        """Calling mark_complete() should set completed to True."""
        task = Task(title="Walk", duration_minutes=30)
        assert task.completed is False
        task.mark_completed()
        assert task.completed is True

    def test_mark_complete_is_idempotent(self):
        """Calling mark_complete() twice should not raise and status stays True."""
        task = Task(title="Walk", duration_minutes=30)
        task.mark_completed()
        task.mark_completed()
        assert task.completed is True

    def test_mark_incomplete_resets_status(self):
        """mark_incomplete() should set completed back to False."""
        task = Task(title="Walk", duration_minutes=30, completed=True)
        task.mark_incomplete()
        assert task.completed is False

    def test_task_str_contains_title(self):
        """__str__ should include the task title."""
        task = Task(title="Morning walk", duration_minutes=20, priority="high")
        assert "Morning walk" in str(task)

    def test_task_str_completed_shows_checkmark(self):
        """Completed tasks should show ✓ in their string representation."""
        task = Task(title="Walk", duration_minutes=10)
        task.mark_completed()
        assert "✓" in str(task)

    def test_task_with_notes(self):
        """A task with notes should include them in __str__."""
        task = Task(title="Meds", duration_minutes=5, notes="Half tablet")
        assert "Half tablet" in str(task)


# ══════════════════════════════════════════════════════════════════════════════
# Pet Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestPet:

    def test_pet_starts_with_no_tasks(self):
        """A newly created pet should have an empty task list."""
        pet = Pet(name="Mochi", species="dog", age=3)
        assert len(pet.get_tasks()) == 0

    def test_add_task_increases_count(self):
        """Adding a task should increase the pet's task count by 1."""
        pet  = Pet(name="Mochi", species="dog", age=3)
        task = Task(title="Walk", duration_minutes=30)
        pet.add_task(task)
        assert len(pet.get_tasks()) == 1

    def test_add_multiple_tasks(self):
        """Adding three tasks should result in a task list of length 3."""
        pet = Pet(name="Mochi", species="dog", age=3)
        for i in range(3):
            pet.add_task(Task(title=f"Task {i}", duration_minutes=10))
        assert len(pet.get_tasks()) == 3

    def test_remove_task_by_title(self):
        """remove_task() should remove the task with the matching title."""
        pet  = Pet(name="Mochi", species="dog", age=3)
        task = Task(title="Walk", duration_minutes=30)
        pet.add_task(task)
        result = pet.remove_task("Walk")
        assert result is True
        assert len(pet.get_tasks()) == 0

    def test_remove_nonexistent_task_returns_false(self):
        """remove_task() should return False when no task with that title exists."""
        pet    = Pet(name="Mochi", species="dog", age=3)
        result = pet.remove_task("Nonexistent")
        assert result is False

    def test_get_pending_tasks_excludes_completed(self):
        """get_pending_tasks() should only return tasks that are not completed."""
        pet   = Pet(name="Mochi", species="dog", age=3)
        done  = Task(title="Walk",    duration_minutes=30, completed=True)
        todo  = Task(title="Feeding", duration_minutes=10)
        pet.add_task(done)
        pet.add_task(todo)
        pending = pet.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].title == "Feeding"

    def test_get_completed_tasks(self):
        """get_completed_tasks() should only return completed tasks."""
        pet  = Pet(name="Mochi", species="dog", age=3)
        done = Task(title="Walk", duration_minutes=30)
        done.mark_completed()
        todo = Task(title="Feeding", duration_minutes=10)
        pet.add_task(done)
        pet.add_task(todo)
        assert len(pet.get_completed_tasks()) == 1

    def test_total_task_minutes(self):
        """total_task_minutes() should sum all task durations."""
        pet = Pet(name="Mochi", species="dog", age=3)
        pet.add_task(Task(title="Walk",    duration_minutes=30))
        pet.add_task(Task(title="Feeding", duration_minutes=10))
        assert pet.total_task_minutes() == 40


# ══════════════════════════════════════════════════════════════════════════════
# Owner Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestOwner:

    def test_owner_starts_with_no_pets(self):
        """A newly created owner should have an empty pet list."""
        owner = Owner(name="Jordan")
        assert len(owner.get_pets()) == 0

    def test_add_pet_increases_count(self):
        """Adding a pet should increase the owner's pet count by 1."""
        owner = Owner(name="Jordan")
        pet   = Pet(name="Mochi", species="dog", age=3)
        owner.add_pet(pet)
        assert len(owner.get_pets()) == 1

    def test_remove_pet_by_name(self):
        """remove_pet() should remove the pet with the matching name."""
        owner = Owner(name="Jordan")
        pet   = Pet(name="Mochi", species="dog", age=3)
        owner.add_pet(pet)
        result = owner.remove_pet("Mochi")
        assert result is True
        assert len(owner.get_pets()) == 0

    def test_remove_nonexistent_pet_returns_false(self):
        """remove_pet() should return False when no pet with that name exists."""
        owner  = Owner(name="Jordan")
        result = owner.remove_pet("Ghost")
        assert result is False

    def test_get_all_tasks_returns_tuples(self):
        """get_all_tasks() should return (pet, task) tuples for all pets."""
        owner = Owner(name="Jordan")
        pet   = Pet(name="Mochi", species="dog", age=3)
        pet.add_task(Task(title="Walk", duration_minutes=30))
        owner.add_pet(pet)
        all_tasks = owner.get_all_tasks()
        assert len(all_tasks) == 1
        assert all_tasks[0][0] == pet
        assert all_tasks[0][1].title == "Walk"

    def test_get_all_tasks_across_multiple_pets(self):
        """get_all_tasks() should aggregate tasks from all pets."""
        owner = Owner(name="Jordan")
        dog   = Pet(name="Mochi", species="dog", age=3)
        cat   = Pet(name="Luna",  species="cat", age=5)
        dog.add_task(Task(title="Walk",     duration_minutes=30))
        dog.add_task(Task(title="Feeding",  duration_minutes=10))
        cat.add_task(Task(title="Playtime", duration_minutes=20))
        owner.add_pet(dog)
        owner.add_pet(cat)
        assert len(owner.get_all_tasks()) == 3

    def test_default_available_minutes(self):
        """Owner should default to 120 available minutes."""
        owner = Owner(name="Jordan")
        assert owner.available_minutes == 120


# ══════════════════════════════════════════════════════════════════════════════
# Scheduler Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestScheduler:

    def _make_owner(self, available_minutes=120):
        """Helper: create a basic owner with two pets and several tasks."""
        owner = Owner(name="Jordan", available_minutes=available_minutes)
        dog   = Pet(name="Mochi", species="dog", age=3)
        cat   = Pet(name="Luna",  species="cat", age=5)

        dog.add_task(Task(title="Walk",          duration_minutes=30, priority="high"))
        dog.add_task(Task(title="Feeding",        duration_minutes=10, priority="high"))
        dog.add_task(Task(title="Training",       duration_minutes=20, priority="medium"))
        dog.add_task(Task(title="Brush",          duration_minutes=15, priority="low"))
        cat.add_task(Task(title="Medication",     duration_minutes=5,  priority="high"))
        cat.add_task(Task(title="Cat feeding",    duration_minutes=10, priority="high"))
        cat.add_task(Task(title="Litter clean",   duration_minutes=10, priority="medium"))

        owner.add_pet(dog)
        owner.add_pet(cat)
        return owner

    def test_build_schedule_returns_list(self):
        """build_schedule() should return a list."""
        scheduler = Scheduler(owner=self._make_owner())
        result    = scheduler.build_schedule()
        assert isinstance(result, list)

    def test_scheduled_tasks_fit_in_available_time(self):
        """Total scheduled duration must not exceed available_minutes."""
        owner     = self._make_owner(available_minutes=60)
        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()
        total = sum(item.task.duration_minutes for item in scheduler.schedule)
        assert total <= 60

    def test_high_priority_tasks_scheduled_before_low(self):
        """High priority tasks should appear before low priority ones."""
        owner     = self._make_owner(available_minutes=120)
        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()
        priorities = [item.task.priority for item in scheduler.schedule]
        # Find positions of high and low priority
        high_indices = [i for i, p in enumerate(priorities) if p == "high"]
        low_indices  = [i for i, p in enumerate(priorities) if p == "low"]
        if high_indices and low_indices:
            assert max(high_indices) < min(low_indices), (
                "All high priority tasks should appear before any low priority task"
            )

    def test_tasks_exceeding_time_are_skipped(self):
        """Tasks that do not fit in available time should appear in skipped."""
        # Only 15 minutes available — most tasks will be skipped
        owner     = self._make_owner(available_minutes=15)
        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()
        assert len(scheduler.skipped) > 0

    def test_no_tasks_returns_empty_schedule(self):
        """An owner with no tasks should produce an empty schedule."""
        owner     = Owner(name="Jordan", available_minutes=120)
        owner.add_pet(Pet(name="Mochi", species="dog", age=3))
        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()
        assert scheduler.schedule == []

    def test_explain_plan_returns_list_of_strings(self):
        """explain_plan() should return a non-empty list of strings."""
        scheduler = Scheduler(owner=self._make_owner())
        scheduler.build_schedule()
        explanation = scheduler.explain_plan()
        assert isinstance(explanation, list)
        assert all(isinstance(line, str) for line in explanation)
        assert len(explanation) > 0

    def test_explain_plan_with_no_tasks(self):
        """explain_plan() with no tasks should return a helpful message."""
        owner     = Owner(name="Jordan", available_minutes=120)
        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()
        explanation = scheduler.explain_plan()
        assert any("No tasks" in line for line in explanation)

    def test_start_times_are_sequential(self):
        """Each scheduled item's start time should equal the previous item's end time."""
        owner     = self._make_owner(available_minutes=120)
        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()
        for i in range(1, len(scheduler.schedule)):
            prev = scheduler.schedule[i - 1]
            curr = scheduler.schedule[i]
            assert curr.start_time == prev.end_time, (
                f"Gap between '{prev.task.title}' and '{curr.task.title}'"
            )

    def test_mark_all_complete(self):
        """mark_all_complete() should set completed=True on all scheduled tasks."""
        owner     = self._make_owner(available_minutes=120)
        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()
        scheduler.mark_all_complete()
        for item in scheduler.schedule:
            assert item.task.completed is True

    def test_get_summary_keys(self):
        """get_summary() should return a dict with the expected keys."""
        owner     = self._make_owner()
        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()
        summary   = scheduler.get_summary()
        expected_keys = {
            "owner_name", "available_minutes", "scheduled",
            "skipped", "total_minutes_used"
        }
        assert expected_keys.issubset(summary.keys())

    def test_completed_tasks_not_rescheduled(self):
        """Tasks already marked complete should not appear in the schedule."""
        owner = Owner(name="Jordan", available_minutes=120)
        dog   = Pet(name="Mochi", species="dog", age=3)
        done  = Task(title="Walk",    duration_minutes=30, completed=True)
        todo  = Task(title="Feeding", duration_minutes=10)
        dog.add_task(done)
        dog.add_task(todo)
        owner.add_pet(dog)

        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()

        scheduled_titles = [item.task.title for item in scheduler.schedule]
        assert "Walk"    not in scheduled_titles
        assert "Feeding" in scheduled_titles


# ══════════════════════════════════════════════════════════════════════════════
# Phase 5 — Sorting, Filtering, Recurrence, Conflict Detection
# ══════════════════════════════════════════════════════════════════════════════

from datetime import date, timedelta


class TestSorting:

    def _make_scheduled_scheduler(self):
        """Helper: owner with tasks added out of priority order."""
        owner = Owner(name="Jordan", available_minutes=120)
        pet   = Pet(name="Mochi", species="dog", age=3)
        # Added low → medium → high deliberately to prove sorting works
        pet.add_task(Task(title="Grooming",  duration_minutes=15, priority="low"))
        pet.add_task(Task(title="Training",  duration_minutes=20, priority="medium"))
        pet.add_task(Task(title="Walk",      duration_minutes=30, priority="high"))
        pet.add_task(Task(title="Feeding",   duration_minutes=10, priority="high"))
        owner.add_pet(pet)
        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()
        return scheduler

    def test_sort_by_time_returns_chronological_order(self):
        """sort_by_time() should return items with strictly ascending start times."""
        scheduler = self._make_scheduled_scheduler()
        sorted_items = scheduler.sort_by_time()
        start_times  = [item.start_time for item in sorted_items]
        assert start_times == sorted(start_times)

    def test_sort_by_time_does_not_mutate_schedule(self):
        """sort_by_time() should return a new list and not modify self.schedule."""
        scheduler      = self._make_scheduled_scheduler()
        original_order = [item.task.title for item in scheduler.schedule]
        scheduler.sort_by_time()
        after_sort     = [item.task.title for item in scheduler.schedule]
        assert original_order == after_sort

    def test_sort_by_time_empty_schedule(self):
        """sort_by_time() on an empty schedule should return an empty list."""
        owner     = Owner(name="Jordan", available_minutes=120)
        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()
        assert scheduler.sort_by_time() == []

    def test_high_priority_scheduled_first_reflected_in_sort(self):
        """After sorting, the first item should be the earliest start time."""
        scheduler    = self._make_scheduled_scheduler()
        sorted_items = scheduler.sort_by_time()
        assert sorted_items[0].start_time == 0


class TestFiltering:

    def _make_owner(self):
        """Helper: owner with two pets and varied tasks."""
        owner = Owner(name="Jordan", available_minutes=120)
        dog   = Pet(name="Mochi", species="dog", age=3)
        cat   = Pet(name="Luna",  species="cat", age=5)
        dog.add_task(Task(title="Walk",      duration_minutes=30, priority="high"))
        dog.add_task(Task(title="Training",  duration_minutes=20, priority="medium"))
        cat.add_task(Task(title="Medication",duration_minutes=5,  priority="high"))
        cat.add_task(Task(title="Playtime",  duration_minutes=20, priority="low"))
        owner.add_pet(dog)
        owner.add_pet(cat)
        return owner

    def test_filter_by_pet_name_returns_only_that_pets_tasks(self):
        """filter_tasks(pet_name='Mochi') should return only Mochi's tasks."""
        owner   = self._make_owner()
        results = owner.filter_tasks(pet_name="Mochi")
        assert all(pet.name == "Mochi" for pet, _ in results)
        assert len(results) == 2

    def test_filter_by_pet_name_nonexistent_returns_empty(self):
        """filter_tasks with a pet name that doesn't exist should return []."""
        owner   = self._make_owner()
        results = owner.filter_tasks(pet_name="Ghost")
        assert results == []

    def test_filter_by_completed_false_returns_pending_only(self):
        """filter_tasks(completed=False) should return only incomplete tasks."""
        owner = self._make_owner()
        # Mark one task complete
        owner.get_pets()[0].get_tasks()[0].mark_completed()
        results = owner.filter_tasks(completed=False)
        assert all(not task.completed for _, task in results)

    def test_filter_by_completed_true_returns_done_only(self):
        """filter_tasks(completed=True) should return only completed tasks."""
        owner = self._make_owner()
        owner.get_pets()[0].get_tasks()[0].mark_completed()
        results = owner.filter_tasks(completed=True)
        assert all(task.completed for _, task in results)
        assert len(results) == 1

    def test_filter_by_priority(self):
        """filter_tasks(priority='high') should return only high priority tasks."""
        owner   = self._make_owner()
        results = owner.filter_tasks(priority="high")
        assert all(task.priority == "high" for _, task in results)
        assert len(results) == 2

    def test_filter_combined_pet_and_priority(self):
        """filter_tasks(pet_name, priority) should apply both filters together."""
        owner   = self._make_owner()
        results = owner.filter_tasks(pet_name="Mochi", priority="high")
        assert len(results) == 1
        assert results[0][0].name    == "Mochi"
        assert results[0][1].priority == "high"

    def test_filter_no_args_returns_all_tasks(self):
        """filter_tasks() with no arguments should return all tasks."""
        owner   = self._make_owner()
        results = owner.filter_tasks()
        assert len(results) == 4


class TestRecurrence:

    def test_daily_task_rolls_due_date_forward_one_day(self):
        """Marking a daily task complete should set due_date to today + 1."""
        task = Task(title="Walk", duration_minutes=20,
                    frequency="daily", due_date=date.today())
        task.mark_completed()
        assert task.due_date == date.today() + timedelta(days=1)

    def test_weekly_task_rolls_due_date_forward_seven_days(self):
        """Marking a weekly task complete should set due_date to today + 7."""
        task = Task(title="Bath", duration_minutes=25,
                    frequency="weekly", due_date=date.today())
        task.mark_completed()
        assert task.due_date == date.today() + timedelta(days=7)

    def test_daily_task_resets_to_pending_after_complete(self):
        """A daily task should be pending again after mark_complete()."""
        task = Task(title="Walk", duration_minutes=20, frequency="daily")
        task.mark_completed()
        assert task.completed is False

    def test_weekly_task_resets_to_pending_after_complete(self):
        """A weekly task should be pending again after mark_complete()."""
        task = Task(title="Bath", duration_minutes=25, frequency="weekly")
        task.mark_completed()
        assert task.completed is False

    def test_once_task_stays_completed_no_rollover(self):
        """A once task should stay completed and not roll the due date."""
        original_due = date.today()
        task = Task(title="Vet checkup", duration_minutes=60,
                    frequency="once", due_date=original_due)
        task.mark_completed()
        assert task.completed  is True
        assert task.due_date   == original_due

    def test_daily_task_rolls_multiple_times(self):
        """Marking a daily task complete twice should roll the date forward twice."""
        task = Task(title="Walk", duration_minutes=20,
                    frequency="daily", due_date=date.today())
        task.mark_completed()
        task.mark_completed()
        assert task.due_date == date.today() + timedelta(days=2)

    def test_is_due_today_returns_true_for_today(self):
        """is_due_today() should return True when due_date is today."""
        task = Task(title="Walk", duration_minutes=20, due_date=date.today())
        assert task.is_due_today() is True

    def test_is_due_today_returns_false_for_future_date(self):
        """is_due_today() should return False when due_date is in the future."""
        task = Task(title="Walk", duration_minutes=20,
                    due_date=date.today() + timedelta(days=1))
        assert task.is_due_today() is False

    def test_future_task_not_scheduled(self):
        """A task with a future due_date should not appear in the schedule."""
        owner = Owner(name="Jordan", available_minutes=120)
        pet   = Pet(name="Mochi", species="dog", age=3)
        future_task = Task(title="Future walk", duration_minutes=20,
                           due_date=date.today() + timedelta(days=1))
        today_task  = Task(title="Feeding",     duration_minutes=10)
        pet.add_task(future_task)
        pet.add_task(today_task)
        owner.add_pet(pet)

        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()
        scheduled_titles = [item.task.title for item in scheduler.schedule]

        assert "Future walk" not in scheduled_titles
        assert "Feeding"     in scheduled_titles


class TestConflictDetection:

    def _make_conflicting_scheduler(self):
        """Helper: scheduler with two manually overlapping items."""
        owner = Owner(name="Jordan", available_minutes=120)
        dog   = Pet(name="Rex",   species="dog", age=2)
        cat   = Pet(name="Pixel", species="cat", age=1)
        owner.add_pet(dog)
        owner.add_pet(cat)

        t1 = Task(title="Walk",     duration_minutes=30, priority="high")
        t2 = Task(title="Playtime", duration_minutes=20, priority="medium")
        dog.add_task(t1)
        cat.add_task(t2)

        scheduler = Scheduler(owner=owner)
        # Inject overlapping items manually: t1 runs 0→30, t2 starts at 20
        scheduler.schedule = [
            ScheduledItem(pet=dog, task=t1, start_time=0),
            ScheduledItem(pet=cat, task=t2, start_time=20),
        ]
        return scheduler

    def test_detect_conflicts_returns_list(self):
        """detect_conflicts() should always return a list."""
        owner     = Owner(name="Jordan", available_minutes=120)
        scheduler = Scheduler(owner=owner)
        assert isinstance(scheduler.detect_conflicts(), list)

    def test_overlapping_items_flagged_as_conflict(self):
        """Two items whose time windows overlap should produce a conflict warning."""
        scheduler = self._make_conflicting_scheduler()
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) > 0

    def test_conflict_warning_contains_task_names(self):
        """Conflict warning should mention the names of both conflicting tasks."""
        scheduler = self._make_conflicting_scheduler()
        warning   = scheduler.detect_conflicts()[0]
        assert "Walk"     in warning
        assert "Playtime" in warning

    def test_no_conflict_on_sequential_tasks(self):
        """Tasks that run back-to-back with no overlap should not be flagged."""
        owner = Owner(name="Jordan", available_minutes=120)
        dog   = Pet(name="Rex", species="dog", age=2)
        owner.add_pet(dog)

        t1 = Task(title="Walk",    duration_minutes=30, priority="high")
        t2 = Task(title="Feeding", duration_minutes=10, priority="high")
        dog.add_task(t1)
        dog.add_task(t2)

        scheduler = Scheduler(owner=owner)
        # Sequential: t1 ends at 30, t2 starts at 30 — no overlap
        scheduler.schedule = [
            ScheduledItem(pet=dog, task=t1, start_time=0),
            ScheduledItem(pet=dog, task=t2, start_time=30),
        ]
        assert scheduler.detect_conflicts() == []

    def test_no_conflict_on_empty_schedule(self):
        """An empty schedule should produce no conflicts."""
        owner     = Owner(name="Jordan", available_minutes=120)
        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()
        assert scheduler.detect_conflicts() == []

    def test_no_conflict_on_single_item(self):
        """A schedule with only one item cannot have a conflict."""
        owner = Owner(name="Jordan", available_minutes=120)
        dog   = Pet(name="Rex", species="dog", age=2)
        t1    = Task(title="Walk", duration_minutes=30)
        dog.add_task(t1)
        owner.add_pet(dog)

        scheduler = Scheduler(owner=owner)
        scheduler.schedule = [ScheduledItem(pet=dog, task=t1, start_time=0)]
        assert scheduler.detect_conflicts() == []

    def test_multiple_conflicts_all_reported(self):
        """If three items all overlap, all conflict pairs should be reported."""
        owner = Owner(name="Jordan", available_minutes=120)
        dog   = Pet(name="Rex", species="dog", age=2)
        owner.add_pet(dog)

        t1 = Task(title="A", duration_minutes=30)
        t2 = Task(title="B", duration_minutes=30)
        t3 = Task(title="C", duration_minutes=30)
        dog.add_task(t1)
        dog.add_task(t2)
        dog.add_task(t3)

        scheduler = Scheduler(owner=owner)
        # All three overlap: 0→30, 10→40, 20→50
        scheduler.schedule = [
            ScheduledItem(pet=dog, task=t1, start_time=0),
            ScheduledItem(pet=dog, task=t2, start_time=10),
            ScheduledItem(pet=dog, task=t3, start_time=20),
        ]
        # Three pairs: (A,B), (A,C), (B,C)
        assert len(scheduler.detect_conflicts()) == 3