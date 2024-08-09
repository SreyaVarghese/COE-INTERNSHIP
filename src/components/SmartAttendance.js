import React, { useState } from 'react';
import './SmartAttendance.css';
import axios from 'axios';
const SmartAttendance = () => {
  const [webcamStarted, setWebcamStarted] = useState(false);
  const [photoCaptured, setPhotoCaptured] = useState(false);
  const [annotatedFrame, setAnnotatedFrame] = useState(null);
  const [message, setMessage] = useState('');
  const [recognizedNames, setRecognizedNames] = useState([]);
  //const [attendanceList, setAttendanceList] = useState([]);

  const startWebcam = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/start_webcam');
      if (response.data.status === 'success') {
        setWebcamStarted(true);
        setMessage("Session started successfully!");
      } else {
        setMessage(response.data.message);
      }
    } catch (error) {
      console.error(error);
      setMessage('Failed to session!');
    }
  };

  const capturePhoto = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/capture_frame');
      if (response.data.status === 'success') {
        setAnnotatedFrame(response.data.file_path);
        setRecognizedNames(response.data.recognized_names);
        setPhotoCaptured(true);
        setMessage('Photo captured successfully');
      } else {
        setMessage('Failed to capture photo');
      }
    } catch (error) {
      console.error(error);
      setMessage('Failed to capture photo');
    }
  };

  const updateAttendance = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/update_attendance');
      if (response.data.status === 'success') {
        setMessage(`Attendance updated. Unknown names: ${response.data.unknown_names}, Duplicate names: ${response.data.duplicate_names}`);
      } else {
        setMessage(response.data.message);
      }
    } catch (error) {
      console.error(error);
      setMessage('Failed to update attendance');
    }
  };

 const uploadImage = async (event) => {
   event.preventDefault();
   const formData = new FormData();
   formData.append('image', event.target.image.files[0])
   try {
     const response = await axios.post('http://127.0.0.1:5000/upload_image', formData, {
       headers: {
         'Content-Type': 'multipart/form-data'
       }
     });
     if (response.data.status === 'success') {
       setAnnotatedFrame(response.data.annotated_image);
       setRecognizedNames(response.data.recognized_names);
       setMessage('Image processed successfully');
     } else {
       setMessage(response.data.message);
     }
   } catch (error) {
     console.error(error);
     setMessage('Failed to process image');
   }
 };


  const endSession = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/end_session');
      if (response.data.status === 'success') {
        setWebcamStarted(false);
        setPhotoCaptured(false);
        setAnnotatedFrame(null);
        setRecognizedNames([]);
        setMessage('Session ended successfully');
      } else {
        setMessage(response.data.message);
      }
    } catch (error) {
      console.error(error);
      setMessage('Failed to end session');
    }
  };

  return (
    <div className="container" style={{padding:80}}>
      <h1 style={{fontSize:60}}>Smart Attendance System</h1>
      {!webcamStarted ? (
        <button style={{fontSize:20}} onClick={startWebcam}>Start Session</button>
      ) : (
        <>
          <button style={{fontSize:20}} onClick={capturePhoto}>Capture Photo</button>
          <button style={{fontSize:20}} onClick={updateAttendance}>Update Attendance</button>
          <form onSubmit={uploadImage}>
            <input style={{fontSize:20}} type="file" name="image" accept="image/*" />
            <button style={{fontSize:20}} type="submit">Upload Image</button>
          </form>

          <button style={{fontSize:20}} onClick={endSession}>End Session</button>
        </>
      )}
      <p>{message}</p>
      {annotatedFrame && (
        <div>
          <h2>Annotated Frame:</h2>
          <img src={`http://127.0.0.1:5000/static/uploads/${annotatedFrame}`} alt="Annotated Frame" />
        </div>
      )}
      {recognizedNames.length > 0 && (
        <div>
          <h2 style={{fontSize:35}}>Recognized Names:</h2>
          <ul style={{fontSize:20}}>
            {recognizedNames.map((name, index) => (
              <li style={{fontSize:35}} key={index}>{name}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default SmartAttendance;
