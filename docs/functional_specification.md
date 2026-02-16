## Background

During periods of uncertainty, emergency food banks and meal programs play a vital role in sustaining communities. However, their impact depends on how visible and accessible they are. Many individuals rely on public transportation, making transit access a key factor in reaching those in need. To address this, we aim to build an interactive web application that allows users to find nearby, operational emergency food resources and view the public transportation routes that can take them there.

## User Profile
- Can browse the web
- Located in Seattle and King County
- Does not need any technical skills

## Data sources

### 1. Emergency Food and Meals Seattle and King County
- **Content:** A list of emergency food (meals, food banks, etc.) available in Seattle and King County.
- **Source:** https://data.seattle.gov/Community-and-Culture/Emergency-Food-and-Meals-Seattle-and-King-County/kkzf-ntnu/about_data
- **Use:** Identify available emergency food to display within web app. 

### 2. Puget Sound Consolidated GFTS Schedule
- **Content:** Single, merged GFTS Schedule file set for the region. 
- **Source:** Sound Transit - Open Transit Data (OTD) https://www.soundtransit.org/help-contacts/business-information/open-transit-data-otd/otd-downloads
- **Use:** King County public transportation data

## Use cases

Objective: System displays accurate map of operational food banks and meals matching user needs
User: accesses map
System: displays all operational food banks and meals 
User: selects a filter on type of food bank, operation time, or service requirements
System: shows subset of locations on map
User: selects an individual location
System: shows more text information on that location, and displays public transportation routes to that location

Objective: System displays list of closest food banks and meals to a user based on user's lcoation
User: inputs location into search bar
System: Highlights 5 closest food banks and meals to the user on the map, and displays list beside map
User: selects an individual location
System: shows more text information on that location, and displays public transportation routes to that location