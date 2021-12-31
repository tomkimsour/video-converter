import React,{Component} from 'react';
import axios from 'axios'
// import fs from 'fs'

export default class VideoForm extends Component {
	state = {
	  selectedFile: null
	};

  apiUrl = "http://35.228.87.238:5000/upload"
	
	onFileChange = event => { this.setState({ selectedFile: event.target.files[0] });};
	
  onFileUpload = async () => {
    const formData = new FormData();
    formData.append(
      "file",
      this.state.selectedFile,
      this.state.selectedFile.name
    );
      
    var config = {
      method: 'post',
      url: 'http://35.228.87.238:5000/upload',
      headers: { 
        "Content-Type": "multipart/form-data"
      },
      data : formData
    };

    axios(config)
    .then(function (response) {
      console.log(JSON.stringify(response.data));
    })  
    .catch(function (error) {
      console.log(error);
    });
  };

	fileData = () => {
    if (this.state.selectedFile) {
      return (
      <div>
        <h2>File Details:</h2>
        <ul>
          <li>File Name: {this.state.selectedFile.name} </li>
          <li>File Type: {this.state.selectedFile.type}</li>			
        </ul>
      </div>
      );
    } else {
      return (
      <div>
        <br />
        <h4>Please select a file to convert</h4>
      </div>
      );
    }
	};
	
	render() {
    return (
      <div>
        <div className="flex-col justify-center ">
          <input type="file" id="fileToConvert" name="fileToConvert" accept=".mp4, .mov" onChange={this.onFileChange} />
          <button onClick={this.onFileUpload}>
          Upload!
          </button>
        {this.fileData()}
        </div>
      </div>
    );
    }
  }
