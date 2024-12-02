import asyncio
import sieve
import os
import subprocess
import shutil

from typing import Literal
from async_autocrop import AutoCropper


metadata = sieve.Metadata(
    title="Long form video repurposing",
    description="Given a video generate multiple shorts that are highlights of the video.",
    code_url = 'https://github.com/808Code/longform-to-shorts',
    tags=["Video", "Audio"],
    image=sieve.Image(
        path="logo.jpg"
    ),
    readme=open("README.md", "r").read(),
)


AspectRatioOptions = Literal["1:1", "4:3", "3:4", "4:5", "5:4", "9:16"]

@sieve.function(
    name="longform-to-shorts",
    system_packages=["ffmpeg"],
    python_version="3.10.12",
    metadata=metadata
)
def longform_to_shorts(
    file: sieve.File,
    aspect_ratio: AspectRatioOptions = '9:16',
    return_video_only : bool = False,
):
    """
    Generate highlights with a new aspect ratio, focusing on faces from the given video.
    :param file: The video file to process.
    :param aspect_ratio: The aspect ratio to crop the video to.
    :param return_video_only: If True, returns only generated highlight videos with face focus cropping else includes the generated videos along with its score, title, start time, and end time of each highlight segment from the original video.
    """

    for item in sync_generator(get_longform_to_shorts, **{
        'file': file,
        'aspect_ratio': aspect_ratio,
        'return_video_only' : return_video_only,
    }):
        yield item

async def get_longform_to_shorts(
    file: sieve.File,
    aspect_ratio: AspectRatioOptions = '9:16',
    return_video_only : bool = False,
):

    print("Starting...")

    transcript_analysis = sieve.function.get("sieve/transcript-analysis")
    transcript_analysis_output = transcript_analysis.push(file, generate_highlights = True)
    
    print("Highlight generations have started.")
    highlights_dir = "highlight_clips"    
    highlights = generate_highlights(transcript_analysis_output, highlights_dir)
    
    print("Highlights generation has completed.")
    

    auto_cropper = AutoCropper(
        aspect_ratio = aspect_ratio,
        return_video_only = return_video_only,
        highlights = highlights
        )

    
    print("Highlights autocrop has started.")
    async for result in auto_cropper.process_all_highlights():
        yield result
    
    print("Highlights autocrop has completed.")
    
    try:
        shutil.rmtree(highlights_dir)
        print(f"Deleted folder: {highlights_dir}")
    except Exception as e:
        print(f"Error while deleting folder {highlights_dir}: {e}")
    return

# Synchronous wrapper to consume an asynchronous generator
def sync_generator(async_gen_func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async_gen = async_gen_func(*args, **kwargs)
    try:
        while True:
            yield loop.run_until_complete(async_gen.__anext__())
    except StopAsyncIteration:
        pass
    finally:
        loop.close()


def generate_highlights(transcript_analysis_output, output_dir):    
    
    os.makedirs(output_dir, exist_ok=True)
    highlights_output_object = {}
    for output_object in transcript_analysis_output.result():
        if 'highlights' in output_object:
            highlights_output_object = output_object
            print(f"Total {len(highlights_output_object['highlights'])} highlights generated.")
            break

    highlights = []
    for highlight in highlights_output_object['highlights']:
        valid_filename_title = highlight['title'].replace(" ", "_").replace("'", "").replace("?", "").replace(":", "")
        score = highlight['score']
        start_time = highlight['start_time']
        end_time = highlight['end_time']
        output_file = f"{output_dir}/{valid_filename_title}_highlight.mp4"   

        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-ss", str(start_time),
            "-i", file.path,                                
            "-to", str(end_time),            
            "-c", "copy",                    
            output_file                      
        ]
        try:
            subprocess.run(ffmpeg_command, check=True)
            print(f"Successfully created clip: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while processing {highlight['title']} with start at {str(start_time)} and end at {str(end_time)}.")
            raise e
        
        highlights.append({'start' : start_time, 'end' : end_time, 'title' : highlight['title'], 'score': score, 'file' : output_file}) 
    return highlights


if __name__ == "__main__":
    file = sieve.File(url="https://storage.googleapis.com/sieve-prod-us-central1-public-file-upload-bucket/1298ba8e-e767-4585-b6ba-89d1408544f1/b0044379-d1c3-40a4-bf73-d134260c9a55-input-file.mp4")
    for item in longform_to_shorts(file = file):
        print(item)