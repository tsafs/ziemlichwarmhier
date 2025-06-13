## Task: Aggregate Daily Temperature Data from DWD Files

### Objective
Develop a Python script to process extracted DWD daily climate files, aggregate daily maximum (TXK) and minimum (TNK) temperature values, calculate their means, and store the results in a database linked to each station ID.

---

### Input Data

- **Location:** `data/` folder
- **File Pattern:** `tageswerte_KL_<station_id>_<startdate>_<enddate>_hist/produkt_klima_tag_<startdate>_<enddate>_<station_id>.txt`
- **Format:** Semicolon-separated text files with columns including `STATIONS_ID`, `TXK` (daily max), and `TNK` (daily min).

---

### Processing Steps

1. **File Selection**
   - Accept a user-specified list of extracted files to process.

2. **Parsing**
   - For each file:
     - Read the file and extract columns: `STATIONS_ID`, `TXK`, `TNK`.
     - Ignore rows where `TXK` or `TNK` is `-999` (missing data).

3. **Aggregation**
   - For each station:
     - Calculate the mean of all valid `TXK` (daily max) values.
     - Calculate the mean of all valid `TNK` (daily min) values.

4. **Database Storage**
   - Store the results in a database table with columns:
     - `station_id`
     - `mean_TXK`
     - `mean_TNK`
   - Ensure each entry is linked to the station's metadata (including GPS coordinates) via `station_id`.

---

### Requirements

- Use efficient data processing libraries (e.g., pandas).
- Use an ORM (e.g., SQLAlchemy) or direct SQL for database interaction.
- Handle missing or invalid data gracefully.
- Add logging for processed files and errors.
- Provide a summary report after processing.

---

### Example Output Table

| station_id | mean_TXK | mean_TNK |
|------------|----------|----------|
| 00314      | 18.2     | 7.5      |
| ...        | ...      | ...      |

---

### Notes

- Station metadata (including GPS coordinates) is stored in a separate table and should be linked via `station_id`.
- Optionally, extend the script to process additional statistics or time windows as needed.