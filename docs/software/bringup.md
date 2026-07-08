
# Bringup sequence

1. Run Python repo validation.
2. Launch description only in RViz.
3. Launch Gazebo simulation with fake controllers.
4. Start safety node in `SAFE_IDLE` with no hardware.
5. Connect safety MCU; verify e-stop and watchdog.
6. Connect one actuator fixture; validate limits.
7. Connect perception sensors; record data only.
8. Enable upper-body stand; no free-standing robot yet.
