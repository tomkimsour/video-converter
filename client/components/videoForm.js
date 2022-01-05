import React,{Component} from 'react';
import axios from 'axios'
// import fs from 'fs'

export default class VideoForm extends Component {
	state = {
	  selectedFile: null
	};

  apiUrl = "http://35.228.143.25:5000/upload"
	
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
      url: 'http://35.228.143.25:5000/upload',
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

	render() {
    return (
      <div>
        <div className="columns-3">
          <input type="file" id="fileToConvert" name="fileToConvert" accept=".mp4, .mov, .webm" onChange={this.onFileChange} />
          <button onClick={this.onFileUpload}>
          Upload!
          </button>
        </div>
      </div>
    );
    }
  }
