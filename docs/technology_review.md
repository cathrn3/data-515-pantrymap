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
    - Open source and well documented
    - Easy to use
    - Highly customizable
    - Strong support for geo data
    - Binds interactive components (dropdowns, graphs, sliders, text inputs) with  Python code through "callbacks"
    - Easy to scale app up to hundreds of users
- Cons:
    - Less performant at large datasets; already noticed some latency plotting all the route lines in the demo
    - Stateless, so heavier per-user computations (e.g., real-time route planning or dynamic network calculations) require repeating computations, storing data in the browser, or caching server-side
    - Complex multi-step interactions are more cumbersome compared to frameworks with persistent sessions

## Second library
TODO

## Comparison
|  Feature    | Dash    | Bokeh(?)  |
| ----------- | ----------- | ----------- |

| Setup | Easy to initialize app. App layout is intuitive to set up, and adding multiple components to the dashboard is simple. |  |

| Data handling | Able to take dictionaries, lists and DataFrames, but there are no easy ways to connect graphs to the same underlying dataset. However, it has a deeper integration with DataFrames, allowing syntactic sugar such as automatic plot generation or data selection. | |

| Map Rendering | Default tile layers are provided from dash-leaflet library. There is support for the option of using custom tiles as well. | |

| Markers and Polylines | Markers and polylines can be added via dl.GeoJSON or dl.Polyline from coordinate (latitude and longitude) data. However, we noticed some minor latency in the demo when rendering multiple polylines. | |

| Event handling | Uses Python callback functions decorated with @app.callback to react to user interactions. Events such as clicking a marker, selecting a dropdown value, or entering text in an input box can trigger reactive updates to components. The callback structure is clear but can become verbose when many inputs and outputs are connected. | |

| Dashboard filters | Filters are typically implemented using dropdowns, checklists, sliders, or radio buttons. These components are easily integrated into callbacks to dynamically filter displayed data. Filtering logic must be handled manually in the callback, but the process is straightforward and fully customizable.| |

| User inputs | Supports various input components including text inputs, dropdowns, sliders, and buttons. User inputs can trigger recomputation of data (e.g., calculating the 5 closest food banks) through callbacks. | |

| Performance | Performs well for small - medium size datasets, but is less performant with large dataset. Each callback recomputes outputs, which can introduce latency for expensive calculations unless optimization techniques (e.g., memoization or caching) are used.| |

## Final choice
TODO

## Areas of concern
TODO