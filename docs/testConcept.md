# Test Concept

The project needs to reach at least 80% code coverage and include tests from all levels of the **test automation pyramid**.

![Test Automation Pyramid](assets/images/TestPyramid.png)


## Github Pipeline for Test Execution
The Github Pipeline executes the tests everytime new code is pushed to the repository. The tests suite contains unit tests, integration tests, system tests and architecture tests. For extra insights into the system the pipeline triggers static code analysis with an external sonar qube instance as well. The pipeline fails and prevents merges in pull requests if any of the pipeline stages fail.  

The pipeline test steps are split up between the front and backend to separate the concerns. The written tests are split up in different folders in the specific domain as well. 

## Unit Tests
The unit tests aim for a high branch and line coverage. The main focus lies on testing edge cases to catch errors due to abnormal inputs or conditions. To test a specific module with out its dependies mocking is used where required.  

By formulating good and bad results of the function calls it checked that the behaviour of the called function is not changed by a code change. This is done with black box tests in which only the inputs and outputs are compared and must be deterministically across runs.

## Integration Tests
As integration tests are on a higher level than unit tests they combine different modules to system components. These specific components should be tested with integration tests to check that they work together properly.  

The integration tests are mixed in in the test suite. 

## System Tests
### e2e Tests
The End-to-End Tests are created with a tool called Playwright. Playwright enables us to automatically test the front end of our application via its chromium based browser.

### Smoke Tests
A smoke tests simply tests that the application starts up and is reachable. The test suite contains smoke tests for the gas station service to check the on going compatibility with the Tankerkönig API.

## Architecture Tests
Architecture tests ensure that certain namespaces are not allowed to import or use another namespace. This enforces separation of concerns and promotes modularity and abstraction. 

The diagram below displays the allowed and forbidden namespace imports of the backend application. The routers are in the center of the application and use services to provide functionality to callers.
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
Static code analysis with SonarQube creates metrics for checking the code quality. These metrics include: coverage, errors, common short commings, maintainability grade, cognitive complexity, number of functions per class, lines of code per class and package security analysis. The static code analysis is integrated in the Github pipeline. If SonarQube discovers issues the pipeline fails and prevents merge requests.  

The goal is to follow the industry standards controlled by SonarQube and reaching a good status.