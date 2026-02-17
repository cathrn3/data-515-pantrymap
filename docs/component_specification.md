# Component Specification

## Software Components

### 1. Data Manager

**What it does:** Retrieves and filters food bank and transit data from static datastores. Provides application-specific features like querying data subsets based on user filters and geographic location.

**Inputs:**
- User filters (dictionary specifying filter values like service type, hours)
- Geographic parameters (latitude, longitude, radius)
- Query type (all food banks, nearest N food banks, routes for location)

**Outputs:**
- Filtered array of food bank objects with IDs, GIS data, and details
- Array of transit route objects with IDs and GIS data
- Data validation status

**Implementation components:**
- `getFoodBanks` - retrieves and filters food bank data
- `getBusRoutes` - retrieves transit routes for a given location

---

### 2. Location Services

**What it does:** Handles user location input, validates addresses, and calculates distances to food banks. Determines the nearest food banks based on user location.

**Inputs:**
- User address (string)
- Food bank location data (array of objects with coordinates)
- Number of results desired (e.g., 5 nearest)

**Outputs:**
- Boolean indicating if address is valid
- Geocoded coordinates (latitude, longitude)
- Ranked array of nearest food banks with distances

**Implementation components:**
- `locationVerification` - validates user addresses
- `getNearestFoodBanks` - calculates and ranks food banks by proximity

---

### 3. Visualization Manager

**What it does:** Displays food bank locations and transit routes as interactive maps and lists. Handles user interactions like zooming, clicking markers, and filtering displayed data.

**Inputs:**
- Food bank location data (filtered array with GIS data)
- Transit route data (array with GIS geometries)
- Map events (click, zoom, pan)
- User filters and display preferences

**Outputs:**
- Interactive map object (OpenLayers instance)
- Rendered list of food banks with detailed information
- Updated visualizations based on user interactions

**Implementation components:**
- `mapDisplay` - renders interactive map with markers and routes
- `foodBankDisplay` - displays food bank details in side pane

---

### 4. Route Planning Engine

**What it does:** Calculates optimal transit routes from user locations to selected food banks. Determines travel time, number of transfers, and provides step-by-step directions using transit schedule data.

**Inputs:**
- Origin coordinates (user location)
- Destination coordinates (selected food bank)
- Transit network data (stops, routes, schedules)
- User preferences (max transfers, preferred transit modes)

**Outputs:**
- Optimal route with step-by-step directions
- Estimated travel time
- Number of transfers required
- List of transit lines to take
- Alternative routes if available

**Implementation components:**
- `calculateRoute` - computes optimal path through transit network
- `getDirections` - generates step-by-step instructions for the route

---

## Interactions to Accomplish Use Cases

### Use Case 1: System Displays Accurate Map of Operational Food Banks Matching User Needs

**Scenario:** User wants to see food banks on a map that match their specific needs (e.g., dietary restrictions, operating hours).

**Interaction Flow:**

1. User sets filters in UI (e.g., "halal food", "open weekends")
2. UI sends filters to Data Manager (`getFoodBanks`)
3. Data Manager queries datastore and returns filtered food bank array
4. UI requests transit routes from Data Manager (`getBusRoutes`) for each food bank
5. Data Manager returns transit route data
6. UI passes data to Visualization Manager (`mapDisplay`)
7. Visualization Manager creates interactive map with food bank markers and transit routes
8. UI passes food bank details to Visualization Manager (`foodBankDisplay`)
9. Visualization Manager renders side pane with food bank information
10. User sees map and list; can interact (zoom, click) to explore

**Interaction Diagram:**

```
User
  │
  │ (1) Set filters
  ├─────────────►  UI
  │                 │
  │                 │ (2) Get filtered food banks
  │                 ├──────────────►  Data Manager
  │                 │                (getFoodBanks)
  │                 │                      │
  │                 │ (3) Filtered array   │
  │                 │ ◄────────────────────┤
  │                 │
  │                 │ (4) Get transit routes
  │                 ├──────────────►  Data Manager
  │                 │                (getBusRoutes)
  │                 │                      │
  │                 │ (5) Route data       │
  │                 │ ◄────────────────────┤
  │                 │
  │                 │ (6) Render map
  │                 ├──────────────►  Visualization Manager
  │                 │                (mapDisplay)
  │                 │                      │
  │                 │ (7) Map object       │
  │                 │ ◄────────────────────┤
  │                 │
  │                 │ (8) Render list
  │                 ├──────────────►  Visualization Manager
  │                 │                (foodBankDisplay)
  │                 │                      │
  │                 │ (9) List component   │
  │                 │ ◄────────────────────┤
  │                 │
  │ (10) Display map & list
  │ ◄───────────────┤
```

---

### Use Case 2: System Displays List of Closest Food Banks Based on User's Location

**Scenario:** User enters their address to find the 5 nearest food banks.

**Interaction Flow:**

1. User enters address in UI
2. UI sends address to Location Services (`locationVerification`)
3. Location Services validates address; returns true/false
4. If valid, UI requests all food banks from Data Manager (`getFoodBanks`)
5. Data Manager returns food bank array
6. UI sends address and food banks to Location Services (`getNearestFoodBanks`)
7. Location Services geocodes address, calculates distances, returns 5 nearest food banks
8. UI requests transit routes from Data Manager for the 5 food banks
9. Data Manager returns route data
10. UI sends data to Visualization Manager with user location
11. Visualization Manager displays map centered on user with 5 nearest food banks
12. Visualization Manager displays ranked list showing distance and details

**Interaction Diagram:**

```
User
  │
  │ (1) Enter address
  ├─────────────►  UI
  │                 │
  │                 │ (2) Validate address
  │                 ├──────────────►  Location Services
  │                 │                (locationVerification)
  │                 │                      │
  │                 │ (3) Valid: true      │
  │                 │ ◄────────────────────┤
  │                 │
  │                 │ (4) Get all food banks
  │                 ├──────────────►  Data Manager
  │                 │                (getFoodBanks)
  │                 │                      │
  │                 │ (5) Food bank array  │
  │                 │ ◄────────────────────┤
  │                 │
  │                 │ (6) Find 5 nearest
  │                 ├──────────────►  Location Services
  │                 │                (getNearestFoodBanks)
  │                 │                      │
  │                 │                      │ Calculate distances
  │                 │                      │ Sort and filter
  │                 │                      │
  │                 │ (7) 5 nearest banks  │
  │                 │ ◄────────────────────┤
  │                 │
  │                 │ (8) Get routes for 5
  │                 ├──────────────►  Data Manager
  │                 │                (getBusRoutes)
  │                 │                      │
  │                 │ (9) Route data       │
  │                 │ ◄────────────────────┤
  │                 │
  │                 │ (10) Render map + user location
  │                 ├──────────────►  Visualization Manager
  │                 │                      │
  │                 │ (11) Map with 5 food banks
  │                 │ (12) Ranked list
  │                 │ ◄────────────────────┤
  │                 │
  │ Display results │
  │ ◄───────────────┤
```

---

### Use Case 3: User Gets Transit Directions to Selected Food Bank

**Scenario:** User selects a food bank from the map or list and wants detailed transit directions from their location.

**Interaction Flow:**

1. User clicks on a food bank marker or list item
2. UI requests user's current location from Location Services
3. Location Services returns geocoded coordinates
4. UI sends origin (user location) and destination (food bank) to Route Planning Engine
5. Route Planning Engine requests transit network data from Data Manager
6. Data Manager returns transit stops, routes, and schedule data
7. Route Planning Engine calculates optimal route:
   - Finds nearest transit stops to origin and destination
   - Determines best transit connections
   - Calculates travel time including walking and waiting
8. Route Planning Engine returns route with step-by-step directions
9. UI sends route data to Visualization Manager
10. Visualization Manager highlights the route on the map
11. Visualization Manager displays turn-by-turn directions in side pane
12. User sees walking directions, which buses to take, where to transfer, and estimated arrival time

**Interaction Diagram:**

```
User
  │
  │ (1) Click food bank
  ├─────────────►  UI
  │                 │
  │                 │ (2) Get user location
  │                 ├──────────────►  Location Services
  │                 │                      │
  │                 │ (3) Coordinates      │
  │                 │ ◄────────────────────┤
  │                 │
  │                 │ (4) Calculate route (origin, destination)
  │                 ├──────────────────────────────►  Route Planning Engine
  │                 │                                         │
  │                 │                                         │ (5) Get transit data
  │                 │                                         ├────────────►  Data Manager
  │                 │                                         │                    │
  │                 │                                         │ (6) Transit network│
  │                 │                                         │ ◄──────────────────┤
  │                 │                                         │
  │                 │                                         │ (7) Calculate:
  │                 │                                         │   - Nearest stops
  │                 │                                         │   - Best connections
  │                 │                                         │   - Travel time
  │                 │                                         │
  │                 │ (8) Route with directions               │
  │                 │ ◄───────────────────────────────────────┤
  │                 │
  │                 │ (9) Display route
  │                 ├──────────────►  Visualization Manager
  │                 │                      │
  │                 │                      │ (10) Highlight route on map
  │                 │                      │ (11) Show turn-by-turn directions
  │                 │                      │
  │                 │ (12) Map + directions│
  │                 │ ◄────────────────────┤
  │                 │
  │ View directions │
  │ ◄───────────────┤
```

---

## Summary

The PantryMap system uses four main components:
- **Data Manager** handles data retrieval and filtering
- **Location Services** validates addresses and calculates proximity
- **Visualization Manager** displays results on interactive maps and lists
- **Route Planning Engine** calculates optimal transit routes and provides directions

These components work together to help users find food banks that match their needs, show the nearest options based on location, and provide detailed transit directions to reach them.
