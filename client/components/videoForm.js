import React,{Component} from 'react';

export default class VideoForm extends Component {
	state = {
	  selectedFile: null
	};

  apiUrl = "http://localhost:5100/upload"
	
	onFileChange = event => { this.setState({ selectedFile: event.target.files[0] });};
	
  onFileUpload = async () => {
    const formData = new FormData();
    formData.append(
      "file",
      this.state.selectedFile,
      this.state.selectedFile.name
    );
    var requestOptions = {
      method: 'POST',
      mode: 'no-cors',
      body: formData,
      redirect: 'follow'
    };
    const res = await fetch(this.apiUrl, requestOptions)
    .then(response => response.text())
    .then(result => console.log(result))
    .catch(error => console.log('error', error));
    const data = await res;
    console.log(data)
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
        <p>{this.fileData()}</p>
        </div>
      </div>
    );
    }
  }
