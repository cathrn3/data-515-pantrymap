# PantryMap: Accessible Food Bank Locator

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![.github/workflows/build_test.yml](https://github.com/cathrn3/data-515-pantrymap/actions/workflows/build_test.yml/badge.svg)](https://github.com/cathrn3/data-515-pantrymap/actions/workflows/build_test.yml)
[![Coverage Status](https://coveralls.io/repos/github/cathrn3/data-515-pantrymap/badge.svg?branch=main)](https://coveralls.io/github/cathrn3/data-515-pantrymap?branch=main)


**PantryMap** is a research-driven tool designed to improve emergency food accessibility in Seattle. By integrating food bank data with public transportation schedules, we aim to bridge the gap between food resources and the communities that need them most.

---

##  Project Overview

### Questions of Interest
1. **What is the current state of emergency food accessibility in Seattle?**
   - Where are operational emergency food banks and meals in Seattle today?
   - How accessible are they via public transportation?

2. **How can we make more accessible emergency food banks?**
   - Can we find the best locations for new food banks to serve under-served areas?
   - Which existing food banks lack sufficient public transportation access?

### Key Features
- **Interactive Map**: Visualize operational food banks and meal sites across Seattle.
- **Smart Filtering**: Filter by operation times, service types, and specific community needs.
- **Transit Integration**: Get real-time public transportation routes to your selected food bank.

---

##  Tech Stack & Data

### Technologies
- **Backend/Logic**: Python, Pandas, GeoPandas
- **Visualization**: Bokeh, Folium, Plotly
- **Web App**: Bokeh server (`bokeh serve`)
- **Environment**: Conda / Pip

### Data Sources
1. **[Emergency Food and Meals (King County)](https://data.seattle.gov/Community-and-Culture/Emergency-Food-and-Meals-Seattle-and-King-County/kkzf-ntnu/about_data)**: Comprehensive list of food resources.
2. **[Puget Sound Consolidated GTFS](https://www.soundtransit.org/help-contacts/business-information/open-transit-data-otd/otd-downloads)**: Regional public transportation schedules.

---

##  Getting Started

### Prerequisites
- [Conda](https://docs.conda.io/en/latest/) or [Mamba](https://mamba.readthedocs.io/en/latest/) (recommended)
- Python 3.8+

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/cathrn3/data-515-pantrymap.git
   cd data-515-pantrymap
   ```

2. **Set up the environment:**
   ```bash
   conda env create -n <env name> -f environment.yml
   conda activate <env name>
   ```
   *Or using pip:*
   ```bash
   pip install -r requirements.txt
   ```

3. **Install pantry map package**
   ```bash
   pip install -e .
   ```

4. **Run the application:**
   ```bash
   bokeh serve src/pantry_map/main.py --show
   ```

---

##  Team Members
- **Stuti Gaonkar**
- **Sowmya Dhadheech**
- **Catherine Wu**
- **Jolene Pern**

---

##  License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

