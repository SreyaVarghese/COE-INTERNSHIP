import React, { useState } from 'react';

const ImageInput = ({ onImageUpload }) => {
  const [image, setImage] = useState(null);

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleUpload = () => {
    if (image) {
      onImageUpload(image);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleImageChange} accept="image/*" />
      <button onClick={handleUpload}>Upload and Mark Attendance</button>
    </div>
  );
};

export default ImageInput;
