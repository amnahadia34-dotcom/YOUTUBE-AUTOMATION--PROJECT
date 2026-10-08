import os
import numpy as np
from moviepy.editor import *
from moviepy.video.fx import resize, fadein, fadeout
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import glob
import random

class SAASVideoGenerator:
    def __init__(self, images_folder, output_file="ai_voice_agent_demo.mp4", music_file=None):
        """
        Initialize the video generator
        
        Args:
            images_folder: Path to folder containing screenshot images
            output_file: Output video filename
            music_file: Path to background music MP3 file (optional)
        """
        self.images_folder = images_folder
        self.output_file = output_file
        self.music_file = music_file
        self.resolution = (1920, 1080)
        self.fps = 24
        self.video_duration = 55  # Target duration in seconds
        
        # Text overlays for the video
        self.text_overlays = [
            ("AI Voice Agent Platform", 3, 'top'),
            ("24/7 Intelligent Voice Automation", 2.5, 'center'),
            ("Never Miss A Lead", 2, 'center'),
            ("Real-Time Call Handling", 2.5, 'center'),
            ("Live Speech-To-Text", 2, 'center'),
            ("Automatic Appointment Booking", 2.5, 'center'),
            ("Smart Lead Qualification", 2, 'center'),
            ("Advanced Analytics", 2, 'center'),
            ("Performance Tracking", 2, 'center'),
            ("Answer. Qualify. Convert.", 2.5, 'center'),
            ("24/7 AI Workforce", 2, 'center')
        ]
        
    def load_images(self):
        """Load all images from the specified folder"""
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']
        images = []
        
        for ext in image_extensions:
            images.extend(glob.glob(os.path.join(self.images_folder, ext)))
        
        images.sort()
        print(f"Found {len(images)} images in {self.images_folder}")
        
        if len(images) == 0:
            raise Exception(f"No images found in {self.images_folder}. Please add PNG/JPG files.")
        
        return images
    
    def create_image_clip_with_effects(self, image_path, duration):
        """Create an image clip with zoom, pan, and fade effects"""
        # Load image
        img_clip = ImageClip(image_path, duration=duration)
        
        # Resize to fit resolution maintaining aspect ratio
        img_ratio = img_clip.w / img_clip.h
        target_ratio = self.resolution[0] / self.resolution[1]
        
        if img_ratio > target_ratio:
            new_height = self.resolution[1]
            new_width = int(self.resolution[1] * img_ratio)
        else:
            new_width = self.resolution[0]
            new_height = int(self.resolution[0] / img_ratio)
        
        img_clip = img_clip.resize(height=new_height)
        
        # Create zoom effect with smooth animation
        def zoom_effect(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]
            
            # Smooth zoom curve
            progress = t / duration
            zoom = 1 + (0.15 * np.sin(np.pi * progress))
            
            new_h = int(h * zoom)
            new_w = int(w * zoom)
            
            # Resize frame
            from PIL import Image as PILImage
            pil_img = PILImage.fromarray(frame)
            pil_img = pil_img.resize((new_w, new_h), PILImage.LANCZOS)
            frame = np.array(pil_img)
            
            # Crop to target resolution
            h_offset = (new_h - self.resolution[1]) // 2
            w_offset = (new_w - self.resolution[0]) // 2
            
            if h_offset > 0:
                frame = frame[h_offset:h_offset + self.resolution[1], :]
            if w_offset > 0:
                frame = frame[:, w_offset:w_offset + self.resolution[0]]
            
            return frame
        
        zoom_clip = VideoClip(make_frame=lambda t: zoom_effect(img_clip.get_frame, t), 
                              duration=duration)
        
        # Apply fade in and out
        zoom_clip = zoom_clip.fadein(0.5).fadeout(0.5)
        
        return zoom_clip
    
    def create_text_clip(self, text, duration, position='center'):
        """Create a professional text overlay"""
        # Create text image
        text_color = (255, 255, 255)
        shadow_color = (0, 0, 0)
        
        # Dynamic font size based on text length
        font_size = 60 if len(text) < 20 else 48
        
        try:
            # Try to use a nice font if available
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Create temporary image to measure text size
        temp_img = Image.new('RGBA', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Add padding
        padding = 40
        bg_width = text_width + padding * 2
        bg_height = text_height + padding
        
        # Create text overlay with background
        overlay = Image.new('RGBA', (bg_width, bg_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Draw semi-transparent background
        draw.rectangle([(0, 0), (bg_width, bg_height)], fill=(0, 0, 0, 180))
        
        # Draw text with shadow
        shadow_offset = 2
        draw.text((padding + shadow_offset, padding // 2 + shadow_offset), 
                 text, font=font, fill=shadow_color)
        draw.text((padding, padding // 2), text, font=font, fill=text_color)
        
        # Add subtle gradient effect
        for i in range(3):
            gradient_overlay = Image.new('RGBA', (bg_width, bg_height), (0, 0, 0, 0))
            gradient_draw = ImageDraw.Draw(gradient_overlay)
            gradient_draw.rectangle([(i * 20, 0), (bg_width - i * 20, bg_height)], 
                                   fill=(255, 255, 255, 20))
            overlay = Image.alpha_composite(overlay, gradient_overlay)
        
        # Convert to numpy array
        overlay_array = np.array(overlay)
        
        # Create clip
        text_clip = ImageClip(overlay_array, duration=duration, transparent=True)
        
        # Position the text
        if position == 'top':
            pos = ('center', 100)
        elif position == 'bottom':
            pos = ('center', self.resolution[1] - 150)
        else:
            pos = ('center', 'center')
        
        text_clip = text_clip.set_position(pos)
        
        # Add subtle scale animation
        def scale_effect(get_frame, t):
            frame = get_frame(t)
            if t < 0.3:
                scale = 0.8 + (t / 0.3) * 0.2
                pil_img = Image.fromarray(frame)
                new_size = (int(pil_img.width * scale), int(pil_img.height * scale))
                pil_img = pil_img.resize(new_size, Image.LANCZOS)
                # Center the scaled image
                new_frame = np.zeros((frame.shape[0], frame.shape[1], 4), dtype=np.uint8)
                x_offset = (frame.shape[1] - new_size[0]) // 2
                y_offset = (frame.shape[0] - new_size[1]) // 2
                new_frame[y_offset:y_offset+new_size[1], x_offset:x_offset+new_size[0]] = np.array(pil_img)
                return new_frame
            return frame
        
        text_clip = text_clip.fl(scale_effect)
        
        return text_clip
    
    def create_transition(self, duration=0.5):
        """Create a white flash transition"""
        return ColorClip(size=self.resolution, color=(255, 255, 255), duration=duration).fadein(0.2).fadeout(0.2)
    
    def generate_video(self):
        """Generate the complete video"""
        print("Loading images...")
        images = self.load_images()
        
        # Calculate duration per image
        num_images = len(images)
        duration_per_image = self.video_duration / num_images
        
        clips = []
        text_index = 0
        
        print(f"Creating video with {num_images} images, {duration_per_image:.1f} seconds each...")
        
        for i, img_path in enumerate(images):
            print(f"Processing image {i+1}/{num_images}: {os.path.basename(img_path)}")
            
            # Create image clip with effects
            img_clip = self.create_image_clip_with_effects(img_path, duration_per_image)
            
            # Add text overlay for this image (if we have text left)
            if text_index < len(self.text_overlays):
                text, display_duration, position = self.text_overlays[text_index]
                # Show text for part of the image duration
                if display_duration < duration_per_image:
                    text_clip = self.create_text_clip(text, display_duration, position)
                    # Position text at beginning of clip
                    text_clip = text_clip.set_start(0)
                    img_clip = CompositeVideoClip([img_clip, text_clip])
                text_index += 1
            
            clips.append(img_clip)
            
            # Add transition between clips (except after last)
            if i < num_images - 1:
                transition = self.create_transition(0.5)
                clips.append(transition)
        
        # Concatenate all clips
        print("Concatenating clips...")
        final_video = concatenate_videoclips(clips, method="compose")
        
        # Ensure exact duration
        if final_video.duration > self.video_duration:
            final_video = final_video.subclip(0, self.video_duration)
        
        # Add background music if provided
        if self.music_file and os.path.exists(self.music_file):
            print(f"Adding background music: {self.music_file}")
            try:
                audio = AudioFileClip(self.music_file)
                # Loop audio if needed
                if audio.duration < final_video.duration:
                    audio = audio.loop(duration=final_video.duration)
                else:
                    audio = audio.subclip(0, final_video.duration)
                
                # Reduce music volume for voice-over effect
                audio = audio.volumex(0.3)
                final_video = final_video.set_audio(audio)
            except Exception as e:
                print(f"Warning: Could not add music - {e}")
        
        # Write video file
        print(f"Rendering video to {self.output_file}...")
        print("This may take a few minutes depending on the number of images...")
        
        final_video.write_videofile(
            self.output_file,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac' if self.music_file else None,
            bitrate='5000k',
            preset='medium',
            threads=4
        )
        
        print(f"✓ Video generated successfully: {self.output_file}")
        print(f"  Duration: {final_video.duration:.1f} seconds")
        print(f"  Resolution: {self.resolution[0]}x{self.resolution[1]}")
        print(f"  FPS: {self.fps}")

def main():
    """Main function to run the video generator"""
    print("=" * 60)
    print("AI Voice Agent SaaS Demo Video Generator")
    print("=" * 60)
    print()
    
    # Get input folder path
    images_folder = input("Enter the path to folder containing screenshots: ").strip()
    
    # Remove quotes if present
    images_folder = images_folder.strip('"').strip("'")
    
    # Check if folder exists
    if not os.path.exists(images_folder):
        print(f"Error: Folder '{images_folder}' does not exist!")
        print("Please create a folder and add your screenshot images (PNG/JPG files)")
        return
    
    # Ask for music file (optional)
    music_file = input("Enter path to background music MP3 (optional, press Enter to skip): ").strip()
    if music_file and not os.path.exists(music_file):
        print(f"Warning: Music file '{music_file}' not found - continuing without music")
        music_file = None
    
    # Ask for output file name
    output_file = input("Enter output video filename (default: ai_voice_agent_demo.mp4): ").strip()
    if not output_file:
        output_file = "ai_voice_agent_demo.mp4"
    if not output_file.endswith('.mp4'):
        output_file += '.mp4'
    
    print()
    print("Generating professional SaaS demo video...")
    print("This will include:")
    print("  ✓ Smooth zoom-in/out effects")
    print("  ✓ Cinematic camera movements")
    print("  ✓ Professional text overlays")
    print("  ✓ Fade transitions")
    print("  ✓ 1920x1080 resolution")
    print()
    
    try:
        # Create generator and generate video
        generator = SAASVideoGenerator(images_folder, output_file, music_file)
        generator.generate_video()
        
        print()
        print("🎉 Video creation complete!")
        print(f"📹 Watch your demo at: {output_file}")
        
    except Exception as e:
        print(f"❌ Error generating video: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have installed required packages:")
        print("   pip install moviepy pillow numpy")
        print("2. Ensure your images are valid PNG/JPG files")
        print("3. Check that you have enough disk space")

if __name__ == "__main__":
    main()