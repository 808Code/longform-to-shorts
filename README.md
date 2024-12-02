# longform-to-shorts

Generate video highlights with a focus on faces from a given video.

This Sieve pipeline creates multiple video highlights in different aspect ratios, focusing on faces and representing the best parts of the video as per the provided instructions.

It consists of the following steps:

* Generate the highlights of a video with the [transcript-analysis](https://www.sievedata.com/functions/sieve/transcript-analysis) Sieve function.
* Split the video into segments based on the start and end times of the generated highlights.
* Face focused videos is generated using autocrop [autocrop](https://www.sievedata.com/functions/sieve/autocrop).


## Tutorial

A detailed explanation of the pipeline is provided in this tutorial.

## Options

* `file`: The video file to process.
* `aspect_ratio`: The aspect ratio to crop the video to.
* `return_video_only`: If True, returns only the generated face-cropped highlight videos; otherwise, includes additional details such as the score, title, start time, and end time for each highlight segment from the original video.

## Deploying `longform-to-shorts` to your own Sieve account

First ensure you have the Sieve Python SDK installed: `pip install sievedata` and set `SIEVE_API_KEY` to your Sieve API key.
You can find your API key at [https://www.sievedata.com/dashboard/settings](https://www.sievedata.com/dashboard/settings).

Then deploy the function to your account:

```bash
git clone https://github.com/808Code/longform-to-shorts
cd longform-to-shorts
sieve deploy pipeline.py
```

You can now find the function in your Sieve account and call it via API or SDK.