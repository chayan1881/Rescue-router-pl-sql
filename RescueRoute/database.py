"""Oracle Database access layer for RescueRoute.

Configure Oracle credentials with environment variables. The app can still
calculate routes when Oracle is not configured; route history will be unavailable.
"""
import os

try:
    import oracledb
except ImportError:
    oracledb = None


def _connect():
    if oracledb is None:
        raise DatabaseUnavailable(
            "Oracle driver is not installed. Run: pip install -r requirements.txt"
        )

    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")  # Example: localhost:1521/FREEPDB1

    if not all((user, password, dsn)):
        raise DatabaseUnavailable(
            "Oracle is not configured. Set ORACLE_USER, ORACLE_PASSWORD and ORACLE_DSN."
        )

    return oracledb.connect(user=user, password=password, dsn=dsn)


class DatabaseUnavailable(Exception):
    """Raised when Oracle cannot be reached or is not configured."""


def save_route(source, destination, algorithm, path, distance_km,
               fallback_eta, nodes_explored):
    """Save a computed route using the PL/SQL stored procedure."""
    connection = None
    try:
        connection = _connect()
        cursor = connection.cursor()

        eta_var = cursor.var(oracledb.NUMBER)
        route_id_var = cursor.var(oracledb.NUMBER)

        # ETA is calculated inside Oracle by the PL/SQL function.
        eta = cursor.callfunc(
            "fn_calculate_eta", oracledb.NUMBER, [distance_km, 40]
        )

        cursor.callproc(
            "sp_save_route",
            [
                source, destination, algorithm, path, distance_km,
                eta, nodes_explored, route_id_var
            ]
        )
        connection.commit()

        route_id = route_id_var.getvalue()
        cursor.close()
        return {
            "connected": True,
            "saved": True,
            "route_id": int(route_id) if route_id is not None else None,
            "eta": round(float(eta), 2),
            "message": "Route saved in Oracle using PL/SQL."
        }
    except Exception as exc:
        if connection:
            connection.rollback()
        return {
            "connected": False,
            "saved": False,
            "eta": fallback_eta,
            "message": f"Oracle save unavailable; using calculated route only. {exc}"
        }
    finally:
        if connection:
            connection.close()


def get_recent_routes(limit=10):
    connection = None
    try:
        connection = _connect()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT route_id, source_node, destination_node, algorithm_name,
                   route_path, distance_km, eta_minutes, nodes_explored, created_at
            FROM route_history
            ORDER BY created_at DESC
            FETCH FIRST :limit ROWS ONLY
            """,
            limit=int(limit)
        )
        rows = cursor.fetchall()
        columns = [item[0].lower() for item in cursor.description]
        result = []
        for row in rows:
            item = dict(zip(columns, row))
            if item.get("created_at"):
                item["created_at"] = item["created_at"].isoformat()
            result.append(item)
        cursor.close()
        return result
    except Exception as exc:
        raise DatabaseUnavailable(str(exc)) from exc
    finally:
        if connection:
            connection.close()
