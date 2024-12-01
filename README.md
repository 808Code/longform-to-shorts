# longform_to_shorts

Generate vertical video highlights with a focus on faces from a given video.

This Sieve pipeline creates multiple vertical video highlights in different aspect ratios, focusing on faces and representing the best parts of the video as per the provided instructions.

It consists of the following steps:

* Generate highlights of the video with the [transcript-analysis](https://www.sievedata.com/functions/sieve/transcript-analysis) Sieve function.
* Split the video into segments based on the start and end times of the generated highlights.
* Face focused vertical videos is generated using autocrop [autocrop](https://www.sievedata.com/functions/sieve/autocrop).


## Tutorial

A detailed explanation of the pipeline is provided in this tutorial.

## Options

* `file`: The video file to process.
* `transcript_analysis_prompt`: A custom prompt to guide the LLM's analysis. This influences the focus areas, themes, and overall output of the analysis.
* `autocrop_prompt`: A description of the primary subject of focus, such as the most important element in the scene, the main speaker, or the standout object.
* `autocrop_negative_prompt`: A description of elements to avoid focusing on, such as background objects, logos, blurry objects, large crowds, or any irrelevant details (e.g., backdrops, news graphics, or non-visible faces).
* `min_scene_length`: The minimum duration (in seconds) for each scene in the output highlights.
* `return_highlight_metadata`: If True, generates metadata for each of the highlight video, including the score, title, start time, and end time of each highlight segment from the original video else just returns the highlight videos.


## Deploying `longform_to_shorts` to your own Sieve account

First ensure you have the Sieve Python SDK installed: `pip install sievedata` and set `SIEVE_API_KEY` to your Sieve API key.
You can find your API key at [https://www.sievedata.com/dashboard/settings](https://www.sievedata.com/dashboard/settings).

Then deploy the function to your account:

```bash
git clone https://github.com/808Code/longform_to_shorts
cd longform_to_shorts
sieve deploy pipeline.py
```

You can now find the function in your Sieve account and call it via API or SDK.