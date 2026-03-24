# 8. Crosscutting concepts

## 8.1 Integration of gas station data endpoints
Tanker24 relies on the API provided by Tankerkönig which is forwarding the API provided by the german federal cartel office. We can not use the API published by the federal cartel office directly as it requires a license. 

As Tankerkönig specifies in their terms and conditions that there is no guarantee for the reliability and availability of the endpoint. Therefore Tanker24 implements the gas station data service in such a way that the data provider could easily be swapped if the endpoint is unavailable to continuously provide the offered services to the users of Tanker24.

!!! note  
    There is no other free and open source data provider for this type of data.