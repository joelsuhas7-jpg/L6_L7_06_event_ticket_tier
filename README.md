# L6 L7 Event Ticket Tier Lab

Lab 6: Code and Branch Coverage Analysis.

The application and coverage test suites are in the `Lab 6/` directory. The starter application is preserved from the assigned course repository.

## Run the tests

From `Lab 6/` install dependencies with `python -m pip install pytest coverage`.

Line coverage: `coverage erase && coverage run --source=event_ticket_tier -m pytest CodeCoverageTest_PES2UG24CS069_application.py && coverage report -m`

Branch coverage: `coverage erase && coverage run --branch --source=event_ticket_tier -m pytest BranchCoverageTest_PES2UG24CS069_application.py && coverage report -m`
