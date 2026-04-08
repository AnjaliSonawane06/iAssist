## What changed & why

**Task / Issue link:**
<!-- Link to the task in your project (Frappe Desk) -->

**Summary of changes:**
<!-- Briefly explain what was changed. Focus on the why, not just the what. -->

**Type of change:**
- [ ] Bug fix
- [ ] New feature / enhancement
- [ ] Configuration change (DocType, field, workflow, print format, etc.)
- [ ] Refactor / code cleanup
- [ ] Other (describe below)

---

## Risk & impact

**Which modules / doctypes are affected?**
<!-- e.g. Sales Order, Stock Entry, Custom Script on Purchase Invoice -->

**Could this break any existing functionality?**
- [ ] No impact on existing behaviour
- [ ] Low risk — minor change, isolated area
- [ ] Medium risk — touches shared logic or multiple doctypes
- [ ] High risk — core workflow, permissions, or data migration involved

**If medium or high risk, describe the potential impact:**
<!-- What could go wrong? What depends on this code? -->

**Has this been tested on a staging / demo site?**
- [ ] Yes
- [ ] No (explain why below)

---

## Testing evidence

**Test cases written?**
- [ ] Yes — test cases have been written and are passing
- [ ] Not applicable for this change (explain below)

**How was this manually tested?**
<!-- Describe the steps you followed to verify the change works as expected -->
1. 
2. 
3. 

**Screenshots / screen recordings (if UI change):**
<!-- Attach before/after screenshots or a short recording if the change affects any form, list view, print format, or dashboard -->

---

## Task completion checklist

Before marking this PR as ready for review, confirm the following:

- [ ] Code follows the project's coding conventions and Frappe framework patterns
- [ ] No hardcoded values, credentials, or environment-specific config left in the code
- [ ] All custom fields / doctypes have proper naming (no test or temp names)
- [ ] `bench migrate` has been run and no errors thrown
- [ ] No `console.log`, `print`, or debug statements left in the code
- [ ] Relevant permissions have been checked (roles, field-level permissions)
- [ ] If a background job or scheduler is involved, it has been tested end-to-end
- [ ] Release notes have been updated for this change
- [ ] PR title clearly describes the change (not "fix" or "update") [Follow convention](http://karma-runner.github.io/4.0/dev/git-commit-msg.html)
- [ ] This PR is focused — it does one thing and does not bundle unrelated changes

---

## Reviewer notes

<!-- Anything specific you want the reviewer to focus on, areas you are uncertain about, or context that would help the review -->
