import React,{Component} from 'react';
import axios from 'axios'
// import fs from 'fs'

export default function VideoForm(){

  const selectedFile = React.useRef(null)
  const formatTo = React.useRef("mp4")
  const numberCopy = React.useRef(null)
  const delayQueuing = React.useRef(null)

  const apiUrl = "http://192.168.49.2:30667/upload"
	
	const onFileChange = event => selectedFile.current = event.target.files;

  const handleChange= event => formatTo.current = event.target.value;

	const onNumberChange = event => numberCopy.current = event.target.value;

  const onDelayChange = event => delayQueuing.current = event.target.value;
  

  const onFileUpload = async () => {
    const formData = new FormData();
    formData.append(
      "file",
      selectedFile.current
    );
    formData.append(
      "formatTo",
      formatTo.current
    );
    formData.append(
      "numberOfCopy",
      numberCopy.current
    );
    formData.append(
      "delay",
      delayQueuing.current
    );
    var config = {
      method: 'post',
      url: apiUrl,
      headers: { 
        "Content-Type": "multipart/form-data"
      },
      data : formData
    };

    axios(config)
    .then(function (response) {
      const res = JSON.stringify(response.data);
      window.location.href = res.statusUrl;
    })  
    .catch(function (error) {
      console.log(error);
    });
  };

return (
  <div className='flex flex-col'>

    <div className="my-2">
      <input type="file" id="fileToConvert" name="fileToConvert" accept=".mp4, .mov, .webm" onChange={onFileChange} multiple/>
    </div>

    <div className="my-2">
      <label>
        <p>Number of time you want the files :</p>
        <input type="number" onChange={onNumberChange}></input>
      </label>
    </div>

    <div className="my-2">
      <label>
      <p>Delay between each file in ms: </p>
      <input type="number" ref={delayQueuing} onChange={onDelayChange}></input>
      </label>
    </div>

    <div className="my-2">
      <label>
        Format to convert to : 
        <select ref={formatTo} onChange={handleChange}>
          <option value="mp4">mp4</option>
          <option value="mov">mov</option>
          <option value="webm">webm</option>
        </select>
      </label>
    </div>

    <div className='border-2 border-black w-min my-2 px-1 rounded-full'>
      <button onClick={onFileUpload}>
      Upload
      </button>
    </div>
    
  </div>
);
}
