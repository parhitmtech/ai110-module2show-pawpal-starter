"""
Temporary demo script - tests the Pawpal logic in the terminal without streamlit.
"""

from pawpal_system import Task, Pet, Owner, Scheduler

def main():
    print("\n" + "=" * 55)
    print(" PawPal+ — Terminal Demo")
    print("=" * 55)

    # Create owner
    jordan = Owner(name="Jordan", available_minutes=90)
    print(f"\nOwner created: {jordan}")

    # Create pets
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna  = Pet(name="Luna",  species="cat", age=5)

    jordan.add_pet(mochi)
    jordan.add_pet(luna)

    print(f"\nPet added: {mochi}")
    print(f"Pet added: {luna}")

    # Add tasks for Dog Mochi
    mochi.add_task(Task(
        title="Morning walk",
        duration_minutes=30,
        priority="high",
        notes="Use the park route"
    ))

    mochi.add_task(Task(
        title="Breakfast feeding",
        duration_minutes=10,
        priority="high"
    ))

    mochi.add_task(Task(
        title="Training session",
        duration_minutes=20,
        priority="medium",
        notes="Practice 'stay' command"
    ))

    mochi.add_task(Task(
        title="Grooming brush",
        duration_minutes=15,
        priority="low"
    ))

    # Add tasks for Luna Cat
    luna.add_task(Task(
        title="Medication",
        duration_minutes=5,
        priority="high",
        notes="Half tablet with food"
    ))

    luna.add_task(Task(
        title="Breakfast feeding",
        duration_minutes=10,
        priority="high"
    ))

    luna.add_task(Task(
        title="Playtime",
        duration_minutes=20,
        priority="medium"
    ))

    luna.add_task(Task(
        title="Litter box clean",
        duration_minutes=10,
        priority="medium"
    ))

    # Show all tasks before shceduling

    print("\nAll tasks across all pets:")
    for pet, task in jordan.get_all_tasks():
        print(f"   [{pet.name}]  {task}")

    # Run scheduler
    print(f"\nRunning scheduler "
          f"({jordan.available_minutes} min available)...\n")
    
    scheduler = Scheduler(owner=jordan)
    scheduler.build_schedule()

    # Print explanation
    for line in scheduler.explain_plan():
        print(line)

    # Mark first task complete and show status

    if scheduler.schedule:
        first = scheduler.schedule[0]
        first.task.mark_completed()
        print(f"\nMarked as done: '{first.task.title}' for {first.pet.name}")
        print(f"   Task status: {first.task}")

    # Summary dict for Actual Streamlit
    print("\nSummary dict (for Streamlit):")
    summary = scheduler.get_summary()
    print(f"   Owner         : {summary['owner_name']}")
    print(f"   Available     : {summary['available_minutes']} min")
    print(f"   Scheduled     : {len(summary['scheduled'])} tasks "
          f"({summary['total_minutes_used']} min)")
    print(f"   Skipped       : {len(summary['skipped'])} tasks")
 
    print("\n" + "=" * 55 + "\n")

if __name__ == "__main__":
    main()