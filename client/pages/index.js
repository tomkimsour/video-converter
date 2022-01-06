import Head from 'next/head'
import VideoForm from '../components/videoForm'
import React from 'react'

const siteTitle = "Video converter"

export default function Home({ allPostsData }) {
  return (
    <>
      <Head>
        <title>{siteTitle}</title>
      </Head>
      <div className='flex justify-center font-mono'>
        <div className='border-2 border-sky-100 bg-slate-200 w-7/12 mt-52 p-9 shadow-2xl rounded-lg'>
          <h1 className='text-xl mb-2 underline underline-offset-2'>
            Video converter
          </h1>
          <VideoForm/>
        </div>
      </div>
    </>
  )
}