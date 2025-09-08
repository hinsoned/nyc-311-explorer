# NYC 311 Complaints Analysis (Phase 1)

Author: Edward Hinson  
Project: NYC-311 Data Project – Phase 1  

This project explores NYC 311 service requests, focusing on **NYPD complaints in Manhattan between 2020–2023**.  
It pulls raw data directly from the [NYC Open Data API](https://data.cityofnewyork.us/), cleans and structures it with Python and pandas, and generates a cleaned dataset ready for further analysis.

---

## 📊 Project Goals
- Learn how to pull and filter data from a public API (Socrata).  
- Clean and prepare the NYC 311 dataset for analysis.  
- Explore complaint patterns by type, time of year, and reporting channel.  
- Save a cleaned dataset for reuse in later project phases.

---

## 📂 Data Source
- **Dataset**: [311 Service Requests from 2010 to Present](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9)  
- **Dataset ID**: `erm2-nwe9`  
- **API**: Socrata Open Data API (SODA)  

Filtering applied in this phase:
- Borough = `MANHATTAN`  
- Agency = `NYPD`  
- Years = 2020–2023  

---

## ⚙️ Requirements
This project uses Python and the following libraries:
- `pandas`  
- `sodapy`  

You can install dependencies with:
```bash
pip install -r requirements.txt


