from typing import Literal
import sieve
import os
import subprocess
import shutil


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

def longform_to_shorts(
    file: sieve.File,
    transcript_analysis_prompt : str = "",
    autocrop_prompt: str = "person",
    autocrop_negative_prompt: str = "",
    min_scene_length: int = 0,
    aspect_ratio: AspectRatioOptions = '9:16'

):
    #TODO: remove unnecessary setting.
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
        "target_language": target_language,
        "speaker_diarization": False,
        "use_vad": False,
        "denoise_audio": False,
        "return_as_json_file": False,
        "min_chapter_length": 0,
        "use_azure": False,
        "custom_vocabulary": {"": ""}
    }

    autocrop_settings = {
        "active_speaker_detection": True,
        "aspect_ratio": aspect_ratio,
        "return_video": True,
        "start_time": 0,
        "end_time": -1,
        "speed_boost": False,
        "smart_edit": False,
        "visualize": False,
        "include_subjects": False,
        "include_non_active_layouts": False,
        "prompt": autocrop_prompt,
        "negative_prompt": autocrop_negative_prompt,
        "single_crop_only": False,
        "crop_movement_speed": 0.1,
        "crop_sampling_interval": 3,
        "return_scene_data": False,
        "min_scene_length": min_scene_length,
    }

    transcript_analysis = sieve.function.get("sieve/transcript-analysis")
    transcript_analysis_output = transcript_analysis.push(file, **transcript_analysis_settings)
    print("Generating highlights.")


    for output_object in transcript_analysis_output.result():
        if 'highlights' in output_object:
            highlights_output_object = output_object
            print("Highlights generated.")
            # yield highlights_output_object
            break

    output_dir = "highlight_clips"
    os.makedirs(output_dir, exist_ok=True)

    autocrop_outputs = []
    for highlight in highlights_output_object['highlights']:
        title = highlight['title'].replace(" ", "_").replace("'", "").replace("?", "").replace(":", "")
        score = highlight['score']
        start_time = highlight['start_time']
        end_time = highlight['end_time']
        output_file = f"{output_dir}/{title}_highlight.mp4"   

        ffmpeg_command = [
            "ffmpeg",
            "-y",                            
            "-i", file.path,                 # Original video
            "-ss", str(start_time),          
            "-to", str(end_time),            
            "-c", "copy",                    # Copy streams without re-encoding
            output_file                      
        ]
        try:
            subprocess.run(ffmpeg_command, check=True)
            print(f"Successfully created clip: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while processing {title} with start at {str(start_time)} and end at {str(end_time)}.")
            raise e
        
        autocrop = sieve.function.get("sieve/autocrop")
        autocrop_outputs.append({'highlight' : autocrop.push(sieve.File(path = output_file), **autocrop_settings), 'title' : title, 'score': score}) 
        
    for autocrop_output in autocrop_outputs:
        for output_object in autocrop_output['highlight'].result():
            print(f'''Completed cropping the video with title {autocrop_output['title']}.''')
            autocrop_output['url'] = sieve.Video(path = output_object.path)
            del autocrop_output['highlight']
            yield autocrop_output
    
    print("Completed cropping all highlights.")
    try:
        shutil.rmtree(output_dir)
        print(f"Deleted folder: {output_dir}")
    except Exception as e:
        print(f"Error while deleting folder {output_dir}: {e}")
    return

    

if __name__=="__main__":
    file = sieve.File(url="https://storage.googleapis.com/sieve-prod-us-central1-public-file-upload-bucket/6080b622-6e32-4281-90ae-6afbdc8506d7/8b7ac40b-3a44-48f1-b17b-35eba04e30a7-input-file.mp4")
    for result in longform_to_shorts(file):
        print(result)
