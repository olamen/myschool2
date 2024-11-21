// src/components/AttendanceList.js
import React, { useEffect, useState } from 'react';
import api from '../api';

const AttendanceList = () => {
  const [attendances, setAttendances] = useState([]);

  useEffect(() => {
    const fetchAttendances = async () => {
      try {
        const response = await api.get('/attendances/');
        setAttendances(response.data);
      } catch (error) {
        console.error("Error fetching attendances:", error);
      }
    };

    fetchAttendances();
  }, []);

  return (
    <div>
      <h1>Attendance List</h1>
      <ul>
        {attendances.map((attendance) => (
          <li key={attendance.id}>{attendance.student} - {attendance.status}</li>
        ))}
      </ul>
    </div>
  );
};

export default AttendanceList;
