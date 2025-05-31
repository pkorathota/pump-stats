# pump-stats
Get stats from DAB Esybox pump with DConnect and store in a DB

Needs three environment variables with private stuff
```
DAB_USER
DAB_PASS
DAB_SERIAL
```

SQLite DB schema is
```
CREATE TABLE pump_status (date_time integer primary key,
                          current_pressure integer,
                          motor_power integer,
                          current_flow integer,
                          motor_temp integer,
                          motor_start integer,
                          flow_counter integer,
                          energy_counter integer,
                          total_energy integer);
```
