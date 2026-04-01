"""
main.py
-------
Terminal demo for PawPal+ Phase 4.
Demonstrates sorting, filtering, recurring tasks, and conflict detection.
Run with: python main.py
"""

from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler


def section(title: str) -> None:
    print(f"\n{'=' * 55}")
    print(f"  {title}")
    print('=' * 55)


def main():
    print("\n🐾  PawPal+ — Phase 4 Terminal Demo")

    # Setup 
    jordan = Owner(name="Jordan", available_minutes=90)
    mochi  = Pet(name="Mochi", species="dog", age=3)
    luna   = Pet(name="Luna",  species="cat", age=5)
    jordan.add_pet(mochi)
    jordan.add_pet(luna)

    # Tasks added deliberately out of priority order to demo sorting
    mochi.add_task(Task(title="Grooming brush",    duration_minutes=15, priority="low"))
    mochi.add_task(Task(title="Training session",  duration_minutes=20, priority="medium"))
    mochi.add_task(Task(title="Morning walk",      duration_minutes=30, priority="high",
                        notes="Use the park route"))
    mochi.add_task(Task(title="Breakfast feeding", duration_minutes=10, priority="high"))
    luna.add_task(Task(title="Medication",         duration_minutes=5,  priority="high",
                       notes="Half tablet with food"))
    luna.add_task(Task(title="Playtime",           duration_minutes=20, priority="medium"))
    luna.add_task(Task(title="Litter box clean",   duration_minutes=10, priority="medium"))

    # Demo 1: Sorting 
    section("DEMO 1 — Sorting by time after scheduling")

    scheduler = Scheduler(owner=jordan)
    scheduler.build_schedule()

    print("\nUnsorted schedule order (as built):")
    for item in scheduler.schedule:
        print(f"  {item}")

    print("\nSorted by start time (sort_by_time):")
    for item in scheduler.sort_by_time():
        print(f"  {item}")

    # Demo 2: Filtering 
    section("DEMO 2 — Filtering tasks")

    print("\nAll tasks for Mochi only:")
    for pet, task in jordan.filter_tasks(pet_name="Mochi"):
        print(f"  [{pet.name}] {task}")

    print("\nAll HIGH priority tasks:")
    for pet, task in jordan.filter_tasks(priority="high"):
        print(f"  [{pet.name}] {task}")

    # Mark one complete then filter by completion status
    scheduler.schedule[0].task.mark_complete()
    print("\nCompleted tasks after marking first scheduled task done:")
    for pet, task in jordan.filter_tasks(completed=True):
        print(f"  [{pet.name}] {task}")

    print("\nStill pending tasks:")
    for pet, task in jordan.filter_tasks(completed=False):
        print(f"  [{pet.name}] {task}")

    # Demo 3: Recurring tasks 
    section("DEMO 3 — Recurring tasks")

    daily_walk  = Task(title="Evening walk",  duration_minutes=20,
                       priority="high", frequency="daily",  due_date=date.today())
    weekly_bath = Task(title="Bath time",     duration_minutes=25,
                       priority="medium", frequency="weekly", due_date=date.today())
    once_vet    = Task(title="Vet checkup",   duration_minutes=60,
                       priority="high", frequency="once",   due_date=date.today())

    mochi.add_task(daily_walk)
    mochi.add_task(weekly_bath)
    mochi.add_task(once_vet)

    print(f"\nBefore mark_complete:")
    print(f"  Daily  — due: {daily_walk.due_date}  | completed: {daily_walk.completed}")
    print(f"  Weekly — due: {weekly_bath.due_date} | completed: {weekly_bath.completed}")
    print(f"  Once   — due: {once_vet.due_date}    | completed: {once_vet.completed}")

    daily_walk.mark_complete()
    weekly_bath.mark_complete()
    once_vet.mark_complete()

    print(f"\nAfter mark_complete:")
    print(f"  Daily  — due: {daily_walk.due_date}  | completed: {daily_walk.completed}"
          f"  ← rolled forward 1 day, reset to pending")
    print(f"  Weekly — due: {weekly_bath.due_date} | completed: {weekly_bath.completed}"
          f"  ← rolled forward 7 days, reset to pending")
    print(f"  Once   — due: {once_vet.due_date}    | completed: {once_vet.completed}"
          f"  ← stays completed, no rollover")

    # Demo 4: Conflict detection 
    section("DEMO 4 — Conflict detection")

    # Build a conflicting schedule manually by forcing overlapping start times
    from pawpal_system import ScheduledItem

    conflict_owner = Owner(name="Test", available_minutes=120)
    dog = Pet(name="Rex", species="dog", age=2)
    cat = Pet(name="Pixel", species="cat", age=1)
    conflict_owner.add_pet(dog)
    conflict_owner.add_pet(cat)

    t1 = Task(title="Morning walk",   duration_minutes=30, priority="high")
    t2 = Task(title="Feeding",        duration_minutes=15, priority="high")
    t3 = Task(title="Playtime",       duration_minutes=20, priority="medium")
    dog.add_task(t1)
    dog.add_task(t2)
    cat.add_task(t3)

    conflict_scheduler = Scheduler(owner=conflict_owner)
    # Manually inject overlapping items to demonstrate detection
    conflict_scheduler.schedule = [
        ScheduledItem(pet=dog, task=t1, start_time=0),    # 8:00 → 8:30
        ScheduledItem(pet=cat, task=t3, start_time=20),   # 8:20 → 8:40  ← overlaps t1
        ScheduledItem(pet=dog, task=t2, start_time=35),   # 8:35 → 8:50  ← no overlap
    ]

    print("\nSchedule with intentional overlap:")
    for item in conflict_scheduler.schedule:
        print(f"  {item}")

    conflicts = conflict_scheduler.detect_conflicts()
    if conflicts:
        print("\nConflicts found:")
        for w in conflicts:
            print(f"  {w}")
    else:
        print("\nNo conflicts detected.")

    # Full plan with all features 
    section("FULL PLAN — explain_plan() output")
    fresh_owner = Owner(name="Jordan", available_minutes=90)
    fresh_mochi = Pet(name="Mochi", species="dog", age=3)
    fresh_luna  = Pet(name="Luna",  species="cat", age=5)
    fresh_mochi.add_task(Task(title="Morning walk",      duration_minutes=30, priority="high"))
    fresh_mochi.add_task(Task(title="Breakfast feeding", duration_minutes=10, priority="high"))
    fresh_mochi.add_task(Task(title="Training session",  duration_minutes=20, priority="medium"))
    fresh_mochi.add_task(Task(title="Grooming brush",    duration_minutes=15, priority="low"))
    fresh_luna.add_task(Task(title="Medication",         duration_minutes=5,  priority="high",
                             notes="Half tablet with food"))
    fresh_luna.add_task(Task(title="Litter box clean",   duration_minutes=10, priority="medium"))
    fresh_luna.add_task(Task(title="Evening walk",       duration_minutes=20, priority="high",
                             frequency="daily"))
    fresh_owner.add_pet(fresh_mochi)
    fresh_owner.add_pet(fresh_luna)

    fresh_scheduler = Scheduler(owner=fresh_owner)
    fresh_scheduler.build_schedule()

    print()
    for line in fresh_scheduler.explain_plan():
        print(line)


if __name__ == "__main__":
    main()