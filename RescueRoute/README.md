# RescueRoute – Emergency Vehicle Route Optimization

RescueRoute finds a shortest route between the available Chandigarh hubs using
Dijkstra's algorithm (A* currently uses the same shortest-path implementation).
It displays the route on a Leaflet map and now integrates Oracle Database with
PL/SQL to calculate ETA and save route history.

## Project structure

- `server.py` – Flask backend and route API
- `algorithm.py` – graph and shortest-path algorithms
- `database.py` – Python-to-Oracle integration using `python-oracledb`
- `templates/index.html` – web interface and map
- `database/oracle_setup.sql` – creates the history table, sequence, PL/SQL function and procedure
- `requirements.txt` – Python dependencies
- `.env.example` – Oracle configuration example

## 1. Install Python packages

Open a terminal in the `RescueRoute` folder:

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## 2. Set up Oracle Database

1. Install and start Oracle Database (Oracle Free / XE) and SQL Developer.
2. Open `database/oracle_setup.sql` in SQL Developer.
3. Connect using the schema/user in which you want the project tables.
4. Run the complete script (F5 / Run Script).
5. Confirm that `ROUTE_HISTORY`, `ROUTE_HISTORY_SEQ`, `FN_CALCULATE_ETA`,
   and `SP_SAVE_ROUTE` were created.

The script creates:
- `ROUTE_HISTORY` – stores source, destination, algorithm, route, distance, ETA,
  explored nodes and timestamp.
- `FN_CALCULATE_ETA` – PL/SQL function that calculates ETA from distance and speed.
- `SP_SAVE_ROUTE` – PL/SQL procedure that inserts each calculated route.
- `ROUTE_HISTORY_SEQ` – generates unique route IDs.

## 3. Configure the Oracle connection

Set these environment variables before starting Flask. Replace the sample
values with your own Oracle credentials.

Windows PowerShell:

```powershell
$env:ORACLE_USER="your_oracle_username"
$env:ORACLE_PASSWORD="your_oracle_password"
$env:ORACLE_DSN="localhost:1521/FREEPDB1"
```

For Oracle XE, the service name may be `localhost:1521/XEPDB1`.
Use the actual service name configured on your computer.

macOS/Linux:

```bash
export ORACLE_USER="your_oracle_username"
export ORACLE_PASSWORD="your_oracle_password"
export ORACLE_DSN="localhost:1521/FREEPDB1"
```

Do not commit real database passwords to source control.

## 4. Run the project

```bash
python server.py
```

Open http://127.0.0.1:5000 in your browser, select a source and destination,
and click **Compute Optimal Route**.

## 5. Verify database records

After calculating a route, run this in SQL Developer:

```sql
SELECT route_id, source_node, destination_node, algorithm_name,
       route_path, distance_km, eta_minutes, nodes_explored, created_at
FROM route_history
ORDER BY created_at DESC;
```

## Important notes

- The route calculation works even if Oracle is not configured. In that case,
  the API returns a fallback ETA and explains that the route was not saved.
- To enable PL/SQL persistence, Oracle must be running, the SQL setup script
  must have been executed, and the environment variables must be correct.
- The map uses sample graph distances and demonstration coordinates. They are
  not live traffic or emergency-dispatch navigation data.
- Run `python server.py` (not `app.py`); `app.py` belongs to a separate
  healthcare demo included in the uploaded archive and is not part of RescueRoute.
