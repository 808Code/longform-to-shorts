import asyncio
import sieve
import os
import subprocess
import shutil

from typing import Literal
from async_autocrop import AutoCropper



AspectRatioOptions = Literal["1:1", "4:3", "3:4", "4:5", "5:4", "9:16"]

metadata = sieve.Metadata(
    title="Long form video repurposing tool.",
    description="Given a video generate multiple shorts that are highlights of the video.",
    tags=["Video", "Audio"],
    image=sieve.Image(
        path="logo.jpg"
    ),
    readme=open("README.md", "r").read(),
)

@sieve.function(
    name="longform_to_shorts",
    system_packages=["ffmpeg"],
    python_version="3.10.12",
    metadata=metadata
)
async def longform_to_shorts(
    file: sieve.File,
    transcript_analysis_prompt : str = "",
    autocrop_prompt: str = "person",
    autocrop_negative_prompt: str = "",
    min_scene_length: int = 0,
    aspect_ratio: AspectRatioOptions = '9:16',
    return_highlight_metadata : bool = False,

):
    transcript_analysis_settings = {
        "transcription_backend": "groq-whisper",
        "llm_backend": "gpt-4o-2024-08-06",
        "prompt": transcript_analysis_prompt,
        "generate_summary": False,
        "generate_title": False,
        "generate_tags": False,
        "generate_chapters": False,
        "generate_highlights": True,
        "generate_sentiments": False,
        "custom_chapters": [""],
        "custom_chapter_mode": "extended",
        "max_summary_length": 5,
        "max_title_length": 10,
        "num_tags": 5,
        "target_language": "",
        "speaker_diarization": False,
        "use_vad": False,
        "denoise_audio": False,
        "return_as_json_file": False,
        "min_chapter_length": 0,
        "use_azure": False,
        "custom_vocabulary": {"": ""}
    }

    print("Starting...")

    transcript_analysis = sieve.function.get("sieve/transcript-analysis")
    transcript_analysis_output = transcript_analysis.push(file, **transcript_analysis_settings)
    print("Generating highlights.")

    highlights_output_object = {}
    for output_object in transcript_analysis_output.result():
        if 'highlights' in output_object:
            highlights_output_object = output_object
            print(f"Total {len(highlights_output_object['highlights'])} highlights generated.")
            break

    output_dir = "highlight_clips"
    os.makedirs(output_dir, exist_ok=True)

    highlight_metadatas = []
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
        
        highlight_metadatas.append({'start' : start_time, 'end' : end_time, 'title' : highlight['title'], 'score': score, 'file' : output_file}) 
        auto_cropper = AutoCropper(
            autocrop_prompt = autocrop_prompt,
            autocrop_negative_prompt = autocrop_negative_prompt,
            min_scene_length = min_scene_length,
            aspect_ratio = aspect_ratio,
            return_highlight_metadata = return_highlight_metadata,
            highlight_metadatas = highlight_metadatas
        )

    async for result in auto_cropper.process_crop_results():
        yield result
    
    print("Completed cropping all highlights.")
    try:
        shutil.rmtree(output_dir)
        print(f"Deleted folder: {output_dir}")
    except Exception as e:
        print(f"Error while deleting folder {output_dir}: {e}")
    return

    

# if __name__ == "__main__":
#     async def run_main():
#         file = sieve.File(url="https://storage.googleapis.com/sieve-prod-us-central1-public-file-upload-bucket/1298ba8e-e767-4585-b6ba-89d1408544f1/b0044379-d1c3-40a4-bf73-d134260c9a55-input-file.mp4")
#         async for output in longform_to_shorts(file):
#             print("Final output:", output)

#     asyncio.run(run_main())
