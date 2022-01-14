import React, {useEffect, useState} from 'react'
import axios from 'axios'

export default function VideoStatus(props){

    const [status,setStatus] = useState("sending"); 
    // const [statusText,setStatusText] = useState(<p>{status}</p>)
    let statusId = null 
    const [isFinished,setIsFinished] = useState(false)

    let statusUrl = "";

    const sleep = (milliseconds) => {
        return new Promise(resolve => setTimeout(resolve, milliseconds))
    }

    const updateStatus = async () => {
        while (statusId != "5" ){
            let res = await axios.get(statusUrl)
            if (res.data.status_id != statusId){
                statusId = res.data.status_id;
                setStatus(res.data.status);
            }
            await sleep(3000);
        }
        setIsFinished(true);
    }

    const sendForm = async () =>{
        await sleep(props.delay);
        if (props.config != undefined){
            const res = await axios(props.config);
            setStatus(res.data.status);
            statusId = res.data.status_id;
            statusUrl = res.data.status_url;
            updateStatus();
        }
    }

    useEffect(() => {
        // setIsFinished(false)
        sendForm();
    },[props]);

    return (
        <li>
            {!isFinished ?(
                <p>{props.number} - {status}</p>
                
            ):(
                <a href={status} target="_blank">Download Link</a>
            )}
        </li>
    )

}