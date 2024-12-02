import asyncio
import sieve
import asyncio


class AutoCropper:
    def __init__(self, 
                 aspect_ratio, 
                 return_video_only,
                 highlights,
                 ):
        
        self.highlights = highlights
        self.return_video_only = return_video_only
        self.aspect_ratio = aspect_ratio

    async def autocrop(self, highlight):
        
        """
        Crops a video with focus on faces to an desired aspect ratio.
        :param highlight: A Json object that represents a highlight video without face crop, including its start time, end time, and score.
        :return: The Json object that represents a highlight video with face crop, including its start time, end time, and score.
        """ 
                
        file_path = highlight['file']
        file = sieve.File(path=file_path)
        autocrop = sieve.function.get("sieve/autocrop")
        
        output = autocrop.push(file, return_video = True, aspect_ratio = self.aspect_ratio)
        print(f"Cropping started for {file_path}...")

        result = await asyncio.to_thread(lambda: list(output.result()))

        for output_object in result:
            print(f"Cropping completed for {file_path}.")
            if self.return_video_only:
                return sieve.Video(path = output_object.path)            
            else:
                del highlight['file']
                return {**highlight, 'video': sieve.Video(path = output_object.path)}
            

    async def process_all_highlights(self):
        """
        Asynchronously processes multiple video highlights for cropping.
        This method yields each result from cropping a highlight as they complete.

        :yield: A json object that represents a highlight video with face crop, including its start time, end time, and score.
        """
        tasks = [self.autocrop(highlight) for highlight in self.highlights]

        for task in asyncio.as_completed(tasks):
            result = await task
            yield result
