// App.js
import React, { useState } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './components/Home';
import AboutUs from './components/AboutUs';
import Team from './components/Team';
import SmartAttendance from './components/SmartAttendance';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
const App = () => {
   return (
    <Router>
      <Navbar />
      <div className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<AboutUs />} />
          <Route path="/team" element={<Team />} />
          <Route path="/attendance" element={<SmartAttendance />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
