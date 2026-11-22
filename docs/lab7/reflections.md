# Lab 7 reflections

## Minh

I used the Feedback + Control idea of acknowledging explicit feedback by showing a confirmation only after the API saves the rating. From Errors + Graceful Failure, I would add a retry action that keeps the student's original question when the assistant is temporarily unavailable.

[Feedback + Control](https://pair.withgoogle.com/guidebook-v2/chapter/feedback-controls/) · [Errors + Graceful Failure](https://pair.withgoogle.com/guidebook-v2/chapter/errors-failing/)

## Thang

Following the Google PAIR Guidebook on *Feedback + Control* and *Errors + Graceful Failure*, we implemented explicit fallback escalation to the Training Office (room I.101) and clear status notes whenever retrieval confidence is insufficient or the LLM is degraded, preventing silent failures or hallucinations. In the future, I would add inline feedback control allowing users to edit or steer the query context directly and receive guided suggestions when their question falls outside the indexed student handbook.
