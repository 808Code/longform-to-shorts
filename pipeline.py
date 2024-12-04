import sieve

from typing import Literal


transcript_analysis = sieve.function.get("sieve/transcript-analysis")
autocrop = sieve.function.get("sieve/autocrop")    
    
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
    python_version="3.10.12",
    metadata=metadata
)
def longform_to_shorts(
    file: sieve.File,
    aspect_ratio: AspectRatioOptions = '9:16',
    ):
    """
    Generates face focused highlight videos

    :param aspect_ratio: The aspect ratio to crop the video to.
    :param return_video_only: If set to `True`, only highlight videos with face-focused cropping are returned; otherwise, the response includes all generated videos along with their score, title, start time, and end time.
    :yield: A tuple containing a face focused highlight video along with its metadata.
    """

    print("Starting...")

    transcript_analysis_output = transcript_analysis.push(file, generate_highlights = True)    
    print("Generating highlights")

    highlights = get_highlights(transcript_analysis_output)
    print("Highlights generated")
    
    autocrop_outputs = apply_autocrops(file, highlights, aspect_ratio)
    print("Applying autocrop")

    for complete_autocrop_job in poll_autocrop_jobs(autocrop_outputs):
        yield complete_autocrop_job
 

def get_highlights(transcript_analysis_output):
    HIGHLIGHTS_INDEX = 5   
    transcript_analysis_object = transcript_analysis_output.result() 
    highlights = list(transcript_analysis_object)[HIGHLIGHTS_INDEX]['highlights']
    return highlights

def apply_autocrops(file, highlights, aspect_ratio):
    autocrop_outputs = []
    for highlight in highlights:
        output = autocrop.push(
            file, 
            return_video = True, 
            start_time = highlight['start_time'], 
            end_time = highlight['end_time'], 
            aspect_ratio = aspect_ratio
        )
        autocrop_outputs.append((output, highlight))
    return autocrop_outputs

def poll_autocrop_jobs(autocrop_outputs):
    for autocrop_output, highlight in autocrop_outputs:
        for autocrop_output_object in autocrop_output.result():
            print("Autocrop completed on a video")
            yield (sieve.File(path = autocrop_output_object.path), highlight)
    
if __name__ == "__main__":
    file = sieve.File(url="https://storage.googleapis.com/sieve-prod-us-central1-public-file-upload-bucket/c4d968f5-f25a-412b-9102-5b6ab6dafcb4/2abf06c9-05a7-45a7-b3fd-bc1b4d4ae800-tmpz1wbqhxm.mp4")
    for item in longform_to_shorts(file = file):
        print(item)