# Test Concept

The project needs to reach at least 80% code coverage and include tests from all levels of the **test automation pyramid**.

![Test Automation Pyramid](assets/images/TestPyramid.png)

## GitHub Pipeline for Test Execution
The GitHub Pipeline executes the tests every time new code is pushed to the repository. The tests suite contains unit tests, integration tests, system tests and architecture tests. For extra insights into the system the pipeline triggers static code analysis with an external sonar qube instance as well. The pipeline fails and prevents merges in pull requests if any of the pipeline stages fail.  

The pipeline test steps are split up between the front and backend to separate the concerns. The written tests are split up in different folders in the specific domain as well. 

The results of the tests and static code analysis are added as a criteria for accepting pull request. A pull request may only be merged if all unit, integration, system, architecture, and static analysis checks pass successfully and the configured coverage threshold of 80% is reached.

**Exit criteria for merging pull requests:**
|Description|
|---|
|All automated tests must pass.|
|Coverage is greater than 80%.|
|SonarQube does not flag any security issues or critical issues. Ranking SonarCube Score A on the given code changes is a pass.|
|No architecture test rules are violated by the code changes.|
|The code changes must be approved by a different project member.|


## Unit Tests
The unit tests aim for a high branch and line coverage. The main focus lies on testing edge cases to catch errors due to abnormal inputs or conditions. To test a specific module without its dependencies mocking is used where required. The tests and test data are designed by the developers. The test data must make sense and add value to the tests suite by either specifying good or bad behaviour and testing edge cases. Each developer is responsible for adding tests for new functionalities to maintain a high code coverage with useful and adequate tests.

By formulating good and bad results of the function calls it is checked that the behaviour of the called function is not changed by a code change. This is done with black box tests in which only the inputs and outputs are compared and must be deterministic across runs.

## Integration Tests
As integration tests are on a higher level than unit tests they combine different modules to system components. Integration tests validate the interaction between multiple modules and ensure that interfaces between components function correctly.

Integration tests are part of the automated CI tests suite. 

## System Tests
### e2e Tests
The End-to-End Tests are created with a tool called Playwright. Playwright enables us to automatically test the front end of our application via its chromium based browser.

### Smoke Tests
A smoke test verifies that the application starts up and is reachable. The tests suite contains smoke tests for the gas station service to check the ongoing compatibility with the Tankerkönig API.

## Architecture Tests
Architecture tests ensure that certain namespaces are not allowed to import or use another namespace. This enforces separation of concerns and promotes modularity and abstraction. 

The diagram below displays the allowed and forbidden namespace imports of the backend application. Routers form the entry point of the backend application and use services to provide functionality to callers.
```puml
[routers]
[services]
[dtos]
[repositories]
[schemas]

[services] -[#red]up-> [routers]: <color:red>forbidden</color>
[schemas] -[#red]up-> [routers]: <color:red>forbidden</color>
[dtos] -[#red]up-> [routers]: <color:red>forbidden</color>
[dtos] -[#red]left-> [services]: <color:red>forbidden</color>
[repositories] -[#red]up-> [routers]: <color:red>forbidden</color>
[repositories] -[#red]up-> [services]: <color:red>forbidden</color>

[routers] -down-> [services]
[services] -down-> [repositories]
[services] -right-> [dtos]
[routers] -down-> [dtos]
[repositories] -down-> [schemas]
```
## Static Code Analysis
Static code analysis with SonarQube creates metrics for checking the code quality. These metrics include: coverage, errors, common shortcomings, maintainability grade, cognitive complexity, number of functions per class, lines of code per class and package security analysis. The static code analysis is integrated in the GitHub pipeline. If SonarQube discovers issues, the pipeline fails and prevents the pull request from being merged. 

The goal is to maintain high code quality, readability, maintainability, and security by following the quality standards enforced through SonarQube which takes industry standards into account.

Link to SonarQube Cloud: https://sonarcloud.io/project/overview?id=SQS-THRO_Tanker24