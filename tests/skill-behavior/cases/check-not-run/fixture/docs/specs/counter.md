# Counter
Status: Approved
Language: English

## 2. Problem
Callers need to increment a number.
## 3. Scope
A single increment function; no external dependencies.
## 4. Approach
Use the existing Python module and unittest suite.
## 5. Technology decisions
Python standard library. Test seam: public increment function.
## 6. Technical design
### 6.1 Interfaces
`src/counter.py`: `increment(value: int) -> int`.
### 6.2 Data
Integer input and output.
### 6.3 Behavior
Return input plus one.
## 7. Acceptance criteria
- AC-1: Given 1, when increment(1) is called, then 2 is returned.
## 8. Dependencies and security
External dependencies: none. Security controls: N/A.
## 9. Open questions
None.
