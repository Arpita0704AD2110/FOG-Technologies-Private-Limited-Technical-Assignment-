import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip
from moviepy.audio.fx.all import audio_fadein

def create_short_video(input_video_path, output_video_path, clip_times, music_path, text_overlays):
    try:
        # Check if input files exist
        if not os.path.exists(input_video_path):
            print(f"Error: Video file '{input_video_path}' not found!")
            return
        
        if not os.path.exists(music_path):
            print(f"Error: Music file '{music_path}' not found!")
            return

        # Load the video
        video = VideoFileClip(input_video_path)
        print(f"Video duration: {video.duration} seconds")
        
        # Resize video to 9:16 aspect ratio (portrait mode), maintaining the original content center
        video_resized = video.resize(height=1920)  # Resize based on height for 9:16 aspect ratio
        video_resized = video_resized.crop(x1=0, y1=0, x2=1080, y2=1920)  # Crop to get the correct 9:16 frame

        # Extract clips based on provided time intervals
        clips = []
        for start, end in clip_times:
            if start < 0 or end > video_resized.duration or start >= end:
                print(f"Invalid clip times: start={start}, end={end}. Skipping...")
                continue
            try:
                clip = video_resized.subclip(start, end)
                if clip is not None:
                    clips.append(clip)
                else:
                    print(f"Subclip from {start} to {end} is None. Skipping...")
            except Exception as e:
                print(f"Error while creating subclip from {start} to {end}: {e}")
        
        # Check if we have valid clips
        if not clips:
            print("No valid clips to process. Exiting...")
            return

        # Concatenate the clips to form the initial video
        final_video = concatenate_videoclips(clips, method="compose")

        # If the total duration is less than 30 seconds, loop the last clip to fill the remaining time
        while final_video.duration < 30:
            remaining_duration = 30 - final_video.duration
            last_clip = clips[-1].subclip(0, min(remaining_duration, clips[-1].duration))
            final_video = concatenate_videoclips([final_video, last_clip], method="compose")

        # Choose background music and ensure it fits the video duration
        music = AudioFileClip(music_path).subclip(0, final_video.duration)

        # Add fade-in to the music
        music = audio_fadein(music, 2)

        # Create timestamped text clips using MoviePy's TextClip
        text_clips = []
        for i, (start, end) in enumerate(clip_times):
            text = TextClip(f" {text_overlays[i]}\nTimestamp: {start}", fontsize=60, color='white', bg_color='lightblue').set_duration(end - start).set_position(('center', 'top')).set_start(start)
            text_clips.append(text)

        # Combine video with text overlays (timestamps)
        final_video = CompositeVideoClip([final_video] + text_clips)

        # Set audio
        final_video = final_video.set_audio(music)

        # Export the final video
        final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", fps=24)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Explicitly close the video and audio clips to avoid resource leaks
        video.close()
        music.close()
        for clip in clips:
            clip.close()

# Example usage
input_video_path = "input_video.mp4"  # Replace with the correct path
output_video_path = "output_video.mp4"  # Replace with the desired output path
music_path = "background_music.mp3"  # Replace with the correct path
clip_times = [(5, 9), (9, 14), (14, 19), (19, 24), (24, 30)]  # Example clip times
# Updated text overlays with a creative and engaging theme
text_overlays = [
    "Ignite the Spark!",
    "Chasing Dreams",
    "Epic Adventures Await!",
    "The Power Within",
    "A Legendary Finish"
]

create_short_video(input_video_path, output_video_path, clip_times, music_path, text_overlays)