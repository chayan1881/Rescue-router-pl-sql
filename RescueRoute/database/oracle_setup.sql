-- RescueRoute: Oracle Database + PL/SQL setup
-- Run this script in SQL Developer while connected to your project schema.
-- Example local Oracle Free service: localhost:1521/FREEPDB1

CREATE TABLE route_history (
    route_id          NUMBER PRIMARY KEY,
    source_node       VARCHAR2(80) NOT NULL,
    destination_node  VARCHAR2(80) NOT NULL,
    algorithm_name    VARCHAR2(20) NOT NULL,
    route_path        VARCHAR2(1000) NOT NULL,
    distance_km       NUMBER(10,2) NOT NULL,
    eta_minutes       NUMBER(10,2) NOT NULL,
    nodes_explored    NUMBER(10) DEFAULT 0 NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE SEQUENCE route_history_seq START WITH 1 INCREMENT BY 1 NOCACHE;

-- PL/SQL function: calculate estimated travel time.
CREATE OR REPLACE FUNCTION fn_calculate_eta (
    p_distance_km IN NUMBER,
    p_speed_kmph  IN NUMBER
) RETURN NUMBER
IS
BEGIN
    IF p_distance_km < 0 OR p_speed_kmph <= 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Distance must be non-negative and speed must be positive.');
    END IF;

    RETURN ROUND((p_distance_km / p_speed_kmph) * 60, 2);
END;
/

-- PL/SQL procedure: store every successful route request.
CREATE OR REPLACE PROCEDURE sp_save_route (
    p_source_node      IN  VARCHAR2,
    p_destination_node IN  VARCHAR2,
    p_algorithm_name   IN  VARCHAR2,
    p_route_path       IN  VARCHAR2,
    p_distance_km      IN  NUMBER,
    p_eta_minutes      IN  NUMBER,
    p_nodes_explored   IN  NUMBER,
    p_route_id         OUT NUMBER
)
IS
BEGIN
    p_route_id := route_history_seq.NEXTVAL;

    INSERT INTO route_history (
        route_id, source_node, destination_node, algorithm_name,
        route_path, distance_km, eta_minutes, nodes_explored
    ) VALUES (
        p_route_id, p_source_node, p_destination_node, p_algorithm_name,
        p_route_path, p_distance_km, p_eta_minutes, p_nodes_explored
    );
END;
/

-- Optional verification:
-- SELECT * FROM route_history ORDER BY created_at DESC;
-- SELECT fn_calculate_eta(10, 40) AS eta_minutes FROM dual;
