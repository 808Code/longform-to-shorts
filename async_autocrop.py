import asyncio
import sieve

import asyncio
import sieve


class AutoCropper:
    def __init__(self, 
                 autocrop_prompt, 
                 autocrop_negative_prompt, 
                 min_scene_length, 
                 aspect_ratio, 
                 return_highlight_metadata, 
                 highlight_metadatas, 
                 **kwargs):
        
        self.settings = {
            "active_speaker_detection": True,
            "return_video": True,
            "start_time": 0,
            "end_time": -1,
            "speed_boost": False,
            "smart_edit": False,
            "visualize": False,
            "include_subjects": False,
            "include_non_active_layouts": False,
            "single_crop_only": False,
            "crop_movement_speed": 0.1,
            "crop_sampling_interval": 3,
            "return_scene_data": False,
        }

        self.settings.update({
            "prompt": autocrop_prompt,
            "negative_prompt": autocrop_negative_prompt,
            "min_scene_length": min_scene_length,
            "aspect_ratio": aspect_ratio,
        })
        
        self.highlight_metadatas = highlight_metadatas
        self.return_highlight_metadata = return_highlight_metadata

    def set_highlight_metadatas(self, highlight_metadatas):
        self.highlight_metadatas = highlight_metadatas

    async def autocrop(self, file_data):
        file_path = file_data['file']
        file = sieve.File(path=file_path)
        autocrop = sieve.function.get("sieve/autocrop")
        output = autocrop.push(file, **self.settings)
        print(f"Cropping started for {file_path}...")

        result = await asyncio.to_thread(lambda: list(output.result()))

        for output_object in result:
            print(f"Cropping completed for {file_path}.")
            if self.return_highlight_metadata:
                return {**file_data, 'video': sieve.Video(path=output_object.path)}
            else:
                return sieve.Video(path=output_object.path)

    async def async_crop_handler(self):
        tasks = [self.autocrop(file_data) for file_data in self.highlight_metadatas]

        for task in asyncio.as_completed(tasks):
            result = await task
            yield result

    async def process_crop_results(self):
        async for result in self.async_crop_handler():
            yield result



# async def main():
#     highlight_metadatas = [
#         {'file': '/root/longform_to_shorts/test1.mp4', 'index': 1},
#         {'file': '/root/longform_to_shorts/test2.mp4', 'index': 2},
#         {'file': '/root/longform_to_shorts/test3.mp4', 'index': 3},
#         {'file': '/root/longform_to_shorts/test4.mp4', 'index': 4},
#     ]

#     auto_cropper = AutoCropper(
#             autocrop_prompt = "person",
#             autocrop_negative_prompt = "",
#             min_scene_length = 0,
#             aspect_ratio = '9:16',
#             return_highlight_metadata = False,
#             highlight_metadatas = highlight_metadatas
#         )


#     async for result in auto_cropper.process_crop_results():
#         yield result

# if __name__ == "__main__":
#     async def run_main():
#         async for output in main():
#             print("Final output:", output)

#     asyncio.run(run_main())
