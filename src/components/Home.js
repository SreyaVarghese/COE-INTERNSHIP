import React from "react";
import "./Home.css";

const Home = () => {
  return (
    <div>

      <div className="content">
        <h2 style={{fontSize:60}}>Welcome to our Attendance System</h2>
        <p style={{fontSize:25}}>
          Manage attendance effortlessly with our smart system. Click below to
          get started.
        </p>
        <p style={{fontSize:25}}>
          This system leverages advanced facial recognition technology to
          automate the process of attendance marking. Upload an image and let
          our smart system recognize and mark attendance for you.
        </p>
        <a style={{fontSize:25}} href="/attendance">Get Started</a>
      </div>
      <div className="footer">
        <p >&copy; 2024 Smart Attendance System. All rights reserved.</p>
      </div>
    </div>
  );
};
export default Home;
