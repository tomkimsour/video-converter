import React, { useState, useRef, useEffect } from 'react';
import VideoStatus from './videoStatus';

export default function VideoForm(){

  const selectedFile = useRef(null)
  const formatTo = useRef("")
  const numberCopy = useRef(1)
  const delayQueuing = useRef(1000)

  const [videoStatusList, setVideoStatusList] = useState([]);

  const apiUrl = "http://34.88.103.252:5000/upload"

  let config = {}
	
	const onFileChange = event => selectedFile.current = event.target.files[0];

  const handleChange= event => formatTo.current = "."+event.target.value;

	const onNumberChange = event => numberCopy.current = event.target.value;

  const onDelayChange = event => delayQueuing.current = parseInt(event.target.value);
  
  const addStatusBox = () => {
    let temp = []
    let delay = 0
    for (let index = 0; index < numberCopy.current; index++) {
      temp = temp.concat([[index,config,delay]])
      delay = delay + delayQueuing.current
    }
    setVideoStatusList(temp)
  };

  const createFormData =  () => {
    setVideoStatusList([])
    const formData = new FormData();
    formData.append(
      "file",
      selectedFile.current,
    );
    formData.append(
      "formatTo",
      formatTo.current
    );
    return formData
  }
   
  const onFileUpload = () => {
    let fd = createFormData()
    let conf = {
      method: 'post',
      url: apiUrl,
      headers: { 
        "Content-Type": "multipart/form-data"
      },
      data : fd 
    };
    config= conf;
    addStatusBox();
  };

return (
  <div className='flex flex-col'>
    <div className="my-2">
      <input type="file" id="fileToConvert" name="fileToConvert" accept=".mp4, .mov, .mkv, .webm" onChange={onFileChange}/>
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
          <option value="mkv">mkv</option>
        </select>
      </label>
    </div>

    <div className='border-2 border-black w-min my-2 px-1 rounded-full'>
      <button onClick={onFileUpload}>
      Upload
      </button>
    </div>
    <hr/>
    <ul>
    {videoStatusList.map(data=> <VideoStatus key={data[0]} number={data[0]} config={data[1]} delay={data[2]}/>)}
    </ul>
  </div>
);
}
