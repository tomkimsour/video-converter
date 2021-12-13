import Head from 'next/head'
import VideoForm from '../components/videoForm'

const siteTitle = "Video converter"

export default function Home({ allPostsData }) {
  return (
    <>
      <Head>
        <title>{siteTitle}</title>
      </Head>
      <h1>Video converter</h1>
    <VideoForm/>
    </>
  )
}