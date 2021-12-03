# Description
Implementation of the different component of a kubernetes cluster making video conversion

# API
This api allows to upload one video and tell which format you want to send back.
Then provides a link to download the converted file.

# Encoder
Video encoder worker. It receives a message from a pod, fetches the video file in a local storage change format and write it in another local storage.
