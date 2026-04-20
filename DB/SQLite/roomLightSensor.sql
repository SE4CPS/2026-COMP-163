CREATE TABLE IF NOT EXISTS Room(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  size TEXT,
  windowsCount INTEGER,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Sensor(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS RoomSensorValue(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sensorId INTEGER,
  roomId INTEGER,
  luxValue DECIMAL(5,2),
  luxValueTs DATETIME UNIQUE
);

INSERT INTO Room (size, windowsCount, name) VALUES ('14', 0, 'CTC 114');
INSERT INTO Sensor (name) VALUES ('B1'), ('B2');

INSERT INTO RoomSensorValue(sensorId, roomId, luxValue, luxValueTs) VALUES 
(1, 1, 10, '2026-04-20 09:08:00'), 
(2, 1, 15, '2026-04-20 09:11:00'),
(1, 1, 10, '2026-04-19 09:08:00'), 
(2, 1, 15, '2026-04-18 09:08:00'),
(1, 1, 10, '2026-04-16 09:08:00'), 
(2, 1, 15, '2026-04-17 09:08:00'),
(1, 1, 10, '2026-04-15 09:08:00'), 
(2, 1, 15, '2026-04-14 09:08:00'),
(1, 1, 10, '2026-04-13 09:08:00'), 
(2, 1, 15, '2026-04-12 09:08:00');

SELECT s.name AS Sensor, COUNT(*) 
FROM ROOM r INNER JOIN RoomSensorValue rsv ON rsv.roomId = r.id INNER JOIN Sensor s ON rsv.sensorId = s.id
GROUP BY s.name;
