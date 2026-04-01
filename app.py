import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler
 
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Your daily pet care planning assistant")
 
# Initialise session state once on first load
if "owner" not in st.session_state:
    st.session_state.owner = None
if "schedule_result" not in st.session_state:
    st.session_state.schedule_result = None
 
# Owner Setup 
st.subheader("👤 Owner Setup")
 
with st.form("owner_form"):
    col1, col2 = st.columns(2)
    with col1:
        owner_name = st.text_input("Your name", value="Jordan")
    with col2:
        available_minutes = st.number_input(
            "Minutes available today", min_value=10, max_value=480, value=120, step=10
        )
    submitted_owner = st.form_submit_button("Save Owner")
 
if submitted_owner:
    existing_pets = st.session_state.owner.pets if st.session_state.owner else []
    st.session_state.owner = Owner(
        name=owner_name,
        available_minutes=int(available_minutes),
        pets=existing_pets,
    )
    st.success(f"Owner saved: {owner_name} ({available_minutes} min available)")
 
if st.session_state.owner:
    owner = st.session_state.owner
    st.info(
        f"**{owner.name}** — {len(owner.get_pets())} pet(s) — "
        f"{owner.available_minutes} min available today"
    )
else:
    st.warning("Please save your owner info above before adding pets.")
    st.stop()
 
st.divider()
 
# Add a Pet
st.subheader("Add a Pet")
 
with st.form("pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    submitted_pet = st.form_submit_button("Add Pet")
 
if submitted_pet:
    existing_names = [p.name for p in owner.get_pets()]
    if pet_name in existing_names:
        st.warning(f"A pet named **{pet_name}** already exists.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species, age=int(age)))
        st.success(f"Added **{pet_name}** the {species}!")
 
if owner.get_pets():
    st.markdown("**Your pets:**")
    for pet in owner.get_pets():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"🐾 {pet.name} — {pet.species}, {pet.age} yr — {len(pet.get_tasks())} task(s)")
        with col2:
            if st.button("Remove", key=f"remove_pet_{pet.name}"):
                owner.remove_pet(pet.name)
                st.rerun()
else:
    st.info("No pets yet — add one above.")
 
st.divider()
 
# Add Tasks
st.subheader("Add a Care Task")
 
pet_names = [p.name for p in owner.get_pets()]
 
if not pet_names:
    st.info("Add a pet first before adding tasks.")
else:
    with st.form("task_form"):
        col1, col2 = st.columns(2)
        with col1:
            selected_pet = st.selectbox("Which pet?", pet_names)
            task_title   = st.text_input("Task title", value="Morning walk")
            task_notes   = st.text_input("Notes (optional)", value="")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
        submitted_task = st.form_submit_button("Add Task")
 
    if submitted_task:
        target_pet = next((p for p in owner.get_pets() if p.name == selected_pet), None)
        if target_pet:
            target_pet.add_task(Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                notes=task_notes.strip() or None,
            ))
            st.success(f"Added task **{task_title}** for {selected_pet}!")
 
    st.markdown("**Current tasks by pet:**")
    any_tasks = False
    for pet in owner.get_pets():
        if pet.get_tasks():
            any_tasks = True
            with st.expander(f"🐾 {pet.name} — {len(pet.get_tasks())} task(s)"):
                for task in pet.get_tasks():
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        status = "✅" if task.completed else "⬜"
                        note   = f" _{task.notes}_" if task.notes else ""
                        st.write(f"{status} **{task.title}** — {task.duration_minutes} min | {task.priority.upper()}{note}")
                    with col2:
                        if st.button("Remove", key=f"remove_task_{pet.name}_{task.title}"):
                            pet.remove_task(task.title)
                            st.rerun()
    if not any_tasks:
        st.info("No tasks added yet.")
 
st.divider()
 
# Generate Schedule 
st.subheader("Generate Daily Schedule")
 
all_pending  = owner.get_all_pending_tasks()
total_needed = sum(task.duration_minutes for _, task in all_pending)
 
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Pets", len(owner.get_pets()))
with col2:
    st.metric("Pending tasks", len(all_pending))
with col3:
    st.metric("Total time needed", f"{total_needed} min")
 
if st.button("Generate Schedule", type="primary"):
    if not all_pending:
        st.warning("No pending tasks to schedule. Add some tasks first!")
    else:
        scheduler = Scheduler(owner=owner)
        scheduler.build_schedule()
        st.session_state.schedule_result = scheduler.get_summary()
        st.rerun()
 
if st.session_state.schedule_result:
    result = st.session_state.schedule_result
 
    st.markdown("---")
    st.markdown(f"### Schedule for **{result['owner_name']}**")
    st.caption(f"{result['total_minutes_used']} min used of {result['available_minutes']} min available")
    st.progress(min(result['total_minutes_used'] / result['available_minutes'], 1.0))
 
    if result["scheduled"]:
        st.markdown("#### Scheduled Tasks")
        for item in result["scheduled"]:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{item['task']}** for {item['pet']}")
                if item["notes"]:
                    st.caption(f"{item['notes']}")
            with col2:
                st.write(f"{item['start']} → {item['end']}")
            with col3:
                priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                st.write(f"{priority_color.get(item['priority'], '⚪')} {item['priority'].upper()}")
    else:
        st.warning("No tasks could be scheduled within the available time.")
 
    if result["skipped"]:
        st.markdown("#### Skipped Tasks")
        for item in result["skipped"]:
            st.write(f"**{item['task']}** for {item['pet']} ({item['duration']} min) — {item['reason']}")
 
    if st.button("Clear Schedule"):
        st.session_state.schedule_result = None
        st.rerun()