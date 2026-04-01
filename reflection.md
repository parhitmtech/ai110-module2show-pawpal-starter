# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

I chose four classes:

- Task: holds a single care activity with its duration and priority
        Responsible for knowing whether it has been completed

- Pet: holds the pet's profile and owns a list of tasks
       Responsible for managing which tasksbelong to this pet.

- Owner: hold's the owner's profile and owns a lit of pets
         Responsible for tracking available time and which pets they care for

- Scheduler: takes a Pet and the owner's available time and produces and ordered daily plan. Responsible for all scheduling decisions and for explaining why each task was or wasn't included.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, the design changed in two ways. First, a fifth class called ScheduledItem was added that was not in the original UML. The original design assumed tasks would be returned directly with start times attached as extra data, but this made the code messy. ScheduledItem cleanly wraps a Task with a start time and provides formatted time string methods, which made the scheduler output far more readable. Second, the Task class gained two new fields in Phase 4 which were frequency and due_date, which were not in the original design. These were added to support recurring tasks. The original Task was stateless about time but the updated version tracks when it is next due and automatically rolls the due date forward when marked complete.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers two constraints 'available time in minutes' and 'task priority'. Available time is a hard constraint since no task is scheduled if it would exceed the owner's available minutes for the day. Priority is the primary ordering constraint. High priority tasks are always scheduled before medium, and medium before low. Within the same priority level, shorter tasks are scheduled first to fit more tasks into the available window. The decision to make time a hard constraint and priority the ordering key reflects the real-world scenario keeping in mind that a pet owner has a fixed amount of time and must ensure the most important care happens first.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler only detects conflicts between tasks that have already been placed in the schedule but it does not predict or prevent conflicts before scheduling. This means if two tasks are manually injected with overlapping times, the scheduler will warn about them but will not automatically fix them. This is a reasonable tradeoff for this scenario because the scheduler's primary job is greedy sequential assignment, which by design produces non-overlapping slots. Conflict detection is a safety net for edge cases rather than the core mechanism, and keeping it as a reporting tool rather than an auto-resolver keeps the logic simple and transparent.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI at pretty much every stage of the project. In Phase 1, I used it for design brainstorming, generating the UML diagram, and translating it into Python class skeletons. In Phase 2, I used it to sketch the full implementation of all four classes and generate the complete test suite. In Phase 3, I used it to write the Streamlit connection logic, specifically the session state pattern for persisting the Owner object across rerenders. In Phase 4, I used it to implement the new algorithmic methods 'sort_by_time', 'filter_tasks', 'detect_conflicts', and the recurring task logic in 'mark_complete'. The most useful prompts I created were specific and context-grounded, for example, asking how the Scheduler should retrieve tasks from the Owner's pets given the existing class structure, rather than asking for a scheduler in the abstract.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One moment where I did not accept AI suggestion as-is was the conflict detection implementation. The first version suggested checking only tasks belonging to the same pet, on the assumption that cross-pet conflicts were not meaningful. I rejected this because in a single-owner scenario, the owner is the bottleneck. They cannot physically do two tasks at the same time regardless of which pet the tasks belong to. I updated the check to compare all pairs of scheduled items regardless of pet. I verified this by manually constructing a schedule with an intentional overlap between tasks for different pets and confirming the warning appeared correctly in the terminal output.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tried to cover task completion and status changes in my test suite, adding and removing tasks from pets, adding and removing pets from owners, filtering pending versus completed tasks, the scheduler's greedy selection staying within available time, high priority tasks appearing before low priority tasks, skipped tasks appearing when time runs out, sequential start time assignment with no gaps, the explain_plan output returning readable strings, mark_all_complete updating all scheduled tasks, and completed tasks not being rescheduled. These tests matter because the scheduler's correctness depends on every layer beneath it working properly. If 'pet.get_pending_tasks' returns the wrong tasks, the scheduler produces the wrong schedule regardless of its own logic being correct.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I have high confidence in the core scheduling logic. The 33 tests cover the primary behaviors and several edge cases. The areas where I am not so confident are the recurring task logic under edge conditions (for example, a daily task completed multiple times in the same day), and the conflict detection when tasks have identical start times (a zero-duration edge case). If there was more time the next tests would be: marking a recurring task complete twice in one session, scheduling with zero available minutes, adding two tasks with identical titles to the same pet, and verifying that filter_tasks with multiple simultaneous filters returns the correct intersection.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The most satisfying part according to me is the separation between the logic layer and the UI layer. Because pawpal_system.py has no dependency on Streamlit, every class and method can be tested and reasoned about independently. The 33 tests run very quickly and give immediate confidence that the backend is correct before I even open the Ui. This separation also made Phase 3 straightforward for me. Connecting the UI to the backend was a matter of calling existing methods rather than rewriting logic inside the Streamlit callbacks.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I think that the scheduling algorithm is greedy and non-optimal. It fills time slots sequentially by priority without looking ahead, which means it can miss combinations of tasks that would fit better together. For example, if a 30-minute high-priority task and a 25-minute medium-priority task are the only tasks remaining and 30 minutes are available, the greedy algorithm schedules the high-priority task and skips the medium one, even though a smarter approach might consider the medium task too. A dynamic programming approach to the 0/1 knapsack problem would produce a globally optimal schedule, which would be the first redesign in the next iteration. But, I think for that I will first have to thoroughly understand the knapsack algorithm.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that AI is most useful as an implementation accelerator when the developer has already made the design decisions. Every time we ask a specific, well-scoped question like 'how should this method interact with that class?', 'what is the correct overlap condition for two time intervals?', the AI output is immediately useful. Every time we ask a vague question, the output requires more revision. The judgment about what to build and why has to come from the developer first. AI fills in the how.