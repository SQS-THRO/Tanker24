# 11. Risks and technical debt
This page lists all identified risks and technical debts from the system by priority. If possible there is a suggestion on how to mitigate, minimize, avoid or reduce the risk.

## Tankerkönig Gas Station API
As the Terms and Conditions of Tankerkönig state, the API is provided on best will basis. That means the API might stop working at any point in time for any amount of time. Without the up to date price data our application, Tanker24, is no longer able to deliver two of the main uses cases (UC1 and UC2).  
**Mitigate:** Contact Tankerkönig and get permission to replicate their database on a regular basis to at least cache the locations of the gas stations.  
**Mitigate:**  Implement the gas station service as an interface to easily switch the data provider. This losely coupled architecture will lead to a resilient and maintainable application.

