# Background
Our project focuses on surfacing geospatial relationships between food banks and transportation accessibility in Seattle. One of our goals is to build a user-facing tool that helps individuals identify the most suitable food bank based on their specific needs, eligibility requirements, and proximity to public transit. By allowing users to explore locations, apply filters, and view relevant details, the tool aims to make food access information more practical and actionable.

Beyond supporting individual decision-making, the project also seeks to examine broader spatial patterns. We aim to visually explore questions such as: "How accessible are existing food banks?" and "Where might a new food bank be located to better serve under-resourced areas?"

To achieve these goals, we plan to build an interactive web-based map that displays food bank locations alongside public transit routes. The visualization will allow users to explore spatial patterns, apply filters (e.g., by population served), and interact directly with map elements (e.g., clicking markers to retrieve additional information). Because the application involves layered geospatial rendering (points and polylines), dynamic updates in response to user input, and integration with Python-based data processing workflows, a specialized Python visualization framework is necessary.

The selected library must support the following core functionalities:
- Interactive map rendering with base tiles
- Display of point data (food bank markers) and polyline data (transit routes)
- Dynamic updates to map layers based on user-selected filters
- Event handling for user interactions (e.g., clicking markers)
- Integration with UI components such as dropdown filters and text inputs

# Python libraries
In this technology review, we evaluate two Python libraries that provide robust support for interactive map visualizations and assess their suitability for implementing this application.

## Plotly Dash
- Name: Dash
- Author/Maintainer: Plotly Inc.
- Summary: Plotly dash is an open-source, low-code framework develped for rapidly building analytical web applications. It allows developers to create dashboards and map-based applications entirely in Python, without requiring direct JavaScript coding. Dash integrates seamlessly with Plotly’s plotting library, enabling interactive charts, maps, and other visualizations.
- Pros:
    - Open source and well documented; easy to use
    - Lightweight server setup
    - Great support for geospatial data
    - Strong integration with Plotly maps and charts, allowing high-quality, visually rich plots with minimal effort
    - Binds interactive components (dropdowns, graphs, sliders, text inputs) with  Python code through "callbacks"
    - Easy to scale app up to hundreds of users
- Cons:
    - Less performant at large datasets; already noticed some latency plotting all the route lines in the demo
    - Stateless, so heavier per-user computations (e.g., real-time route planning or dynamic network calculations) require repeating computations, storing data in the browser, or caching server-side
    - Complex multi-step interactions are more cumbersome compared to frameworks with persistent sessions

## Bokeh
- Name: Bokeh
- Author/Maintainer: Anaconda Inc. (maintained by the Bokeh development community)
- Summary: Bokeh is an open-source, powerful Python visualization library and server framework for building interactive web applications. It enables developers to create sophisticated, enterprise-grade dashboards and geospatial applications entirely in Python with server-side rendering. Unlike client-side frameworks, Bokeh maintains persistent server sessions, making it ideal for complex applications requiring real-time computations, multi-step interactions, and stateful data management.
- Pros:
    - Open source and well documented
    - ColumnDataSource and CDSView make filtering large datasets fast and memory-efficient
    - Native support for geospatial data with integrated tile providers
    - Efficient for multi-step and per-user computations since Python state is maintained per session
    - Supports linking multiple visualizations to a single data source
    - Handles map tiles, markers, polylines, and dynamic updates efficiently
- Cons:
    - Less beginner-friendly than Dash; more Python and Bokeh-specific concepts to learn
    - Fewer pre-built UI components than Dash/Plotly ecosystem
    - Layouts and widget linking require more boilerplate and manual configuration
    - Running a server per user session can increase resource usage for large-scale deployments

## Comparison
|  Feature    | Dash    | Bokeh(?)  |
| ----------- | ----------- | ----------- |
| Setup | Easy to initialize app. App layout is intuitive to set up, and adding multiple components to the dashboard is simple. | Requires creating a Bokeh server application for full interactivity. Slightly more boilerplate than Dash, especially when setting up layouts and linking widgets to plots. Initial configuration is more manual. |
| Data handling | Able to take dictionaries, lists, and DataFrames, but there are no easy ways to connect graphs to the same underlying dataset. However, it has a deeper integration with DataFrames, allowing syntactic sugar such as automatic plot generation or data selection. | Also able to take dictionaries, lists, and DataFrames, but uses "ColumnDataSource" as the central data structure. It can be passed to multiple graphs, which results in a shared dataset, linked between all visualisations. In addition, the data source can easily be updated, making dashboards relying on very large datasets much quicker to update. |
| Map Rendering | Default tile layers are provided from dash-leaflet library. There is support for the option of using custom tiles as well. | Uses figure() with tile providers (e.g., CARTODB, OSM). Tile setup requires specifying coordinate systems (Web Mercator), which adds extra steps. More manual configuration compared to dash-leaflet. |
| Markers and Polylines | Markers and polylines can be added via dl.GeoJSON or dl.Polyline from coordinate (latitude and longitude) data. However, we noticed some minor latency in the demo when rendering multiple polylines. | Markers and lines can be added via glyph methods, using the data connect to the ColumnDataSource. Handles multiple polylines efficiently, especially in server mode. |
| Event handling | Uses Python callback functions decorated with @app.callback to react to user interactions. Events such as clicking a marker, selecting a dropdown value, or entering text in an input box can trigger reactive updates to components. The callback structure is clear but can become verbose when many inputs and outputs are connected. | Can also use Python callbacks, in a Bokeh server context. Due to Tornado’s WebSockets, Bokeh allows for constantly-connected sessions and can be easily used for multiple back and forth interactions.|
| Dashboard filters | Filters can be applied using dropdowns, checklists, sliders, or radio buttons. These components are easily integrated into callbacks to dynamically filter displayed data. When the filter is applied, the callback returns a new figure, which replaces the old figure. | Filters are also applied using callbacks. Using CDSView to filter is very efficient, especially for large interactive dashboards, as it only updates the visualization layer without needing to change the underlying data source. In addition, the view applied the filter across all visualizations which share the same data source, without needing to duplicate any data. |
| User inputs | Supports various input components including text inputs, dropdowns, sliders, and buttons. User inputs can trigger recomputation of data (e.g., calculating the 5 closest food banks) through callbacks. | Supports various input components, which can trigger updates through callbacks as well. User inputs persist within a session when using Bokeh server. This allows storing intermediate results or multi-step computations without recomputing everything. Better suited for workflows requiring ongoing user state. |
| Performance | Performs well for small - medium size datasets, but is less performant with large dataset. Each callback recomputes outputs, which can introduce latency for expensive calculations unless optimization techniques (e.g., memoization or caching) are used.| Generally performs smoothly for dynamic visual updates, especially when using persistent sessions. Better suited for applications involving heavier or multi-step computations per user. |

## Final choice
We chose to use Bokeh over Dash for our use case for the following reasons:
- Linked visualizations and side panel updates: One planned feature is a side panel that displays additional details for each food bank based on applied filters. Using CDSView, Bokeh allows all visualizations that share the same underlying data to update efficiently whenever a filter changes, without duplicating data or recalculating everything.
- Per-user proximity calculations: We want to compute the five closest food banks to a user-provided address. In Dash, these distances would need to be recalculated every time a filter changes or a new input triggers a callback. In Bokeh, persistent user sessions allow us to store calculated distances for each user, so filters can be applied dynamically without recomputing every distance.
- Route planning engine: As a stretch goal, we aim to implement transit route planning, including multi-step computations such as route calculation, transfer optimization, and step-by-step directions. In Dash, every update would require recomputation and sending new figures to the client. In Bokeh, route data can be stored in ColumnDataSource objects and updated incrementally, with CDSView controlling what is displayed. Persistent sessions allow caching partial computations per user, making stepwise interactions and dynamic updates much more efficient, especially if we want to do any real time route planning.

Overall, Bokeh’s performance and per-user interactivity benefits make it a better fit for our use case, even though Dash is generally simpler and easier to work with.

## Areas of concern
- Deployment: Since Dash is built on top of Flask, a Dash app is straightforward to deploy like any standard Flask app. In contrast, deploying a Bokeh application requires running a Bokeh server, which adds some additional setup and complexity.
- Scalability: Dash’s stateless design makes it easier to scale to many concurrent users. While Bokeh handles per-user sessions well, very large numbers of concurrent users may require careful server resource management to avoid high memory usage, since each session maintains its own data state.