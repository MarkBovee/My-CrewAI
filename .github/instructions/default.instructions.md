---
applyTo: '**'
---
# Coding Assistant Instructions (Spec-Driven)

The assistant has freedom to design and implement solutions, but must always work like a professional developer:
define expectations, plan steps, implement clean code, and verify results.

---

## 🔹 Quick Reference (Checklist)

1. **Spec** → Define expected results (what success looks like).  
2. **Plan** → Outline steps and validation points.  
3. **Tasks** → Break down concrete coding tasks.  
4. **Implement** → Write full working code (no placeholders).  
5. **Verify** → Self-check that results match the plan.  

---

## Workflow

### 1. Spec (Expected Results)
- Start by writing down what the correct outcome should look like.
- Define success in measurable terms (e.g., files downloaded without errors, files exist, files contain content).
- If the outcome is unclear, ask clarifying questions.

### 2. Plan (Steps & Checks)
- Outline the logical plan to achieve the expected result.
- Define checkpoints and validation points.
- Include how results will be verified.

### 3. Tasks (Implementation Plan)
- Break the plan into concrete coding tasks.
- Map each task directly to the expected outcome.
- Use the vscode tasks option for github copilot if available to show the breakdown and progress.

### 4. Implement (Code / Logic)
- Write full working code with no placeholders.
- Follow professional standards and include basic error handling.
- Only change what is needed; preserve everything else.

### 5. Verify (Self-Check / Test)
- Perform a professional self-check of the code.
- Confirm that the expected results match the plan.
- For tasks like downloading, check that:
  - There are no runtime errors.
  - Files exist after execution.
  - Files are not empty.
  - Content is as expected.
- If checks cannot be run here, describe how to verify them.

---

## Output Format
Always present work in this order:

1. **Spec (Expected Results)**  
2. **Plan (Steps & Validation Points)**  
3. **Tasks (Implementation Breakdown)**  
4. **Code (Full Files or Patches)**  
5. **Verification (Professional Self-Check)**  

Use fenced code blocks with correct language tags.  
For multiple files, provide each file in full.

---

## Clarifications
- If expectations or validations are ambiguous → ask.  
- Do not guess hidden requirements.  
- Keep it light: do not add extras unless explicitly requested.
- Always clean up unused code files after completing tasks.