# Test Concept

The project needs to reach at least 80% code coverage and include tests from all levels of the **test automation pyramid**.

![Test Automation Pyramid](assets/images/TestPyramid.png)


## Github Pipeline for Test Execution
The Github Pipeline executes the tests everytime new code is pushed to the repository. The tests suite contains unit tests, integration tests, system tests and architecture tests. For extra insights into the system the pipeline triggers static code analysis with an external sonar qube instance as well. The pipeline fails and prevents merges in pull requests if any of the pipeline stages fail.

## Unit Tests

## Integration Tests

## System Tests
### e2e Tests
The End-to-End Tests are created with a tool called Playwright. Playwright enables us to automatically test the front end of our application via its chromium based browser.

### Smoke Tests

## Architecture Tests

## Static Code Analysis