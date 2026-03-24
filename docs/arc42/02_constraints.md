# 2. Constraints for Tanker24
The identified architecture constraints can be structured in technical and organizational constraints as well as conventions.

## Technical Constraints
|Id|Description|
|---|---|
|TC-1|Tanker24 shall not call the tankerkoenig API exactly on hour changes as per their terms and conditions.|
|TC-2|Tanker24 shall only call the tankerkoenig API when the user requests a data point as per their terms and conditions.|
|TC-3|Tanker24 shall only use the following programming languages: C#, Python, TypeScript, Java|
|TC-4|Tanker24 shall start-up after running two commands at most.|


## Organizational Constraints
|Id|Description|
|---|---|
|OC-1|Tanker24 shall display it's documentation on readthedocs.io.|
|OC-2|Tanker24 shall use static code analysis.|
|OC-3|Tanker24 shall define ADRs for all important architecture decisions.|

## Conventions
|Id|Description|
|---|---|
|Conv-1|The documentation shall follow the arc42 documentation template.|
|Conv-2|The code shall follow common coding styles managed by the static code analysis tool.|
|Conv-3|Merging code into the main branch shall require a code review from at least one person.|
|Conv-4|Issues shall include a description, a user story (optional) and measurable acceptance criteria.|
|Conv-5|Pull request shall include a short description of the changes and if existing a reference to the solved issue.|