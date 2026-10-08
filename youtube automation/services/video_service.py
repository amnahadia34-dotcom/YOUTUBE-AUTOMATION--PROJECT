import os
import re
import json
import uuid
import logging
import requests
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from moviepy.editor import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
    vfx
)
from moviepy.audio.fx.all import audio_loop
from config.settings import PEXELS_API_KEY
from services.huggingface_video_service import generate_ai_video, should_use_ai_video


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =====================================================
# CONFIGURATION
# =====================================================

print("Memory safe mode enabled")
logger.info(f"video_service initialized with PEXELS_API_KEY: {bool(PEXELS_API_KEY)}")
CACHE_DIR = "cache/video_clips"
OUTPUT_DIR = "output"
WIDTH = 854  # Reduced from 1280 for memory safety
HEIGHT = 480  # Reduced from 720 for memory safety
FPS = 24
MIN_SCENE_DURATION = 2.0
MAX_SCENE_DURATION = 12.0
TEST_MAX_SCENES = 5  # Limit scenes for testing

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =====================================================
# SCRIPT PROCESSING
# =====================================================

def split_script_into_scenes(
    script: str,
    target_scenes: Optional[int] = None
) -> List[str]:
    """
    Split script into intelligent scenes.
    Splits by sentences and groups intelligently.
    Limited to max 5 scenes for memory safety during testing.
    """
    if not script or not script.strip():
        return []
    
    sentences = re.split(r'[.!?]+', script)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return [script.strip()]
    
    if target_scenes is None:
        target_scenes = min(TEST_MAX_SCENES, max(3, len(sentences) // 2))
    
    if len(sentences) <= target_scenes:
        return sentences
    
    scenes = []
    sentences_per_scene = len(sentences) / target_scenes
    
    for i in range(target_scenes):
        start_idx = int(i * sentences_per_scene)
        end_idx = int((i + 1) * sentences_per_scene)
        
        if i == target_scenes - 1:
            end_idx = len(sentences)
        
        scene_text = ". ".join(sentences[start_idx:end_idx])
        if scene_text.strip():
            scenes.append(scene_text.strip())
    
    return scenes[:TEST_MAX_SCENES]


# =====================================================
# KEYWORD EXTRACTION
# =====================================================

def extract_keywords(scene_text: str) -> str:
    """
    Extract search keywords from scene text for stock footage lookup.
    """
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'it', 'this', 'that', 'as',
        'if', 'we', 'you', 'he', 'she', 'they', 'what', 'which', 'who', 'why',
        'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'some',
        'such', 'no', 'nor', 'not', 'only', 'same', 'so', 'than', 'too', 'very'
    }
    verb_words = {
        'changed', 'created', 'became', 'started', 'invested', 'expanded',
        'build', 'built', 'launched', 'grew', 'grow', 'lead', 'leads', 'led',
        'drive', 'drives', 'driving', 'made', 'make', 'makes', 'go', 'goes',
        'doing', 'do', 'did', 'bring', 'brought', 'become', 'becomes', 'is',
        'are', 'was', 'were', 'has', 'had', 'have', 'can', 'could', 'should',
        'will', 'would', 'may', 'might'
    }
    replacements = {
        'ev': 'electric vehicle',
        'ai': 'artificial intelligence',
        'vr': 'virtual reality'
    }
    
    raw_words = re.findall(r"[A-Za-z0-9&]+", scene_text)
    candidates = []
    proper_nouns = []
    for word in raw_words:
        key = word.lower()
        if key in stop_words or key in verb_words or len(key) <= 2:
            continue
        if word[0].isupper() or word.isupper():
            proper_nouns.append(word)
        candidates.append(word)
    
    if proper_nouns:
        query = " ".join(proper_nouns[:2])
        return " ".join(replacements.get(w.lower(), w) for w in query.split())
    
    clean_candidates = [replacements.get(w.lower(), w) for w in candidates]
    if len(clean_candidates) >= 2:
        return ' '.join(clean_candidates[:3])
    if clean_candidates:
        return clean_candidates[0]
    return 'business technology'


def build_ai_scene_prompt(scene_text: str) -> str:
    text = scene_text.strip()
    if not text.endswith('.'):
        text = text + '.'
    return (
        f"{text} cinematic documentary style, professional camera movement, "
        "ultra realistic, 4k, high detail, Netflix style, dramatic lighting"
    )


def generate_visual_keywords(scene_text: str) -> List[str]:
    """Convert narration into 3-5 visual search terms.

    Heuristic-based: prefer people, locations, objects, actions, tech, businesses.
    """
    if not scene_text or not scene_text.strip():
        return ["business technology", "office work", "corporate scene"]

    text = scene_text.strip()
    lower = text.lower()

    # Hand-crafted mappings for strong signals
    mapping = {
        'tesla': ['Tesla factory', 'Tesla car production', 'electric vehicle', 'automotive factory', 'car manufacturing'],
        'elon': ['Elon Musk', 'technology company', 'engineering laboratory', 'tech CEO'],
        'success': ['entrepreneur working', 'office productivity', 'business growth', 'team meeting'],
        'invested': ['investment meeting', 'venture capital office', 'business funding', 'investors meeting'],
        'factory': ['factory manufacturing', 'industrial production', 'production line', 'assembly line'],
        'ancient': ['ancient architecture', 'historical ruins', 'archaeological site', 'ancient civilization'],
        'rome': ['Roman Empire', 'ancient architecture', 'colosseum', 'historical civilization'],
        'technology': ['technology company', 'engineering lab', 'software developers', 'tech startup'],
        'ai': ['artificial intelligence lab', 'machine learning research', 'ai development', 'robotics lab']
    }

    results: List[str] = []

    # 1) trigger mapping by keyword
    for key, phrases in mapping.items():
        if key in lower:
            for p in phrases:
                if p not in results:
                    results.append(p)
            if len(results) >= 5:
                return results[:5]

    # 2) proper nouns (people, brands)
    proper = re.findall(r"\b[A-Z][a-z]{2,}(?:\s[A-Z][a-z]{2,})?\b", scene_text)
    for p in proper:
        if p.lower() in ('the', 'and'):
            continue
        if p not in results:
            results.append(p)
        if len(results) >= 5:
            return results[:5]

    # 3) nouns and important tokens
    tokens = re.findall(r"\b[a-z]{3,}\b", lower)
    weighted = []
    stop = set(['the','that','this','there','where','when','which','what','does','dont'])
    for t in tokens:
        if t in stop:
            continue
        if t.endswith('ing') or t.endswith('ed'):
            weighted.append(f"{t} people")
        else:
            weighted.append(t)
        if len(weighted) >= 10:
            break

    # add weighted tokens as visual phrases
    for w in weighted:
        if len(results) >= 5:
            break
        # make short phrases more visual
        if ' ' in w:
            candidate = w
        else:
            if len(w) > 6:
                candidate = f"{w} scene"
            else:
                candidate = f"{w} footage"
        if candidate not in results:
            results.append(candidate)

    # 4) ensure between 3 and 5 terms
    if len(results) < 3:
        defaults = ['business technology', 'office work', 'corporate scene', 'stock footage']
        for d in defaults:
            if d not in results:
                results.append(d)
            if len(results) >= 3:
                break

    return results[:5]


# =====================================================
# PEXELS API INTEGRATION
# =====================================================

def _get_cache_path(keyword: str) -> str:
    """Generate cache path for downloaded video."""
    safe_keyword = re.sub(r'[^a-z0-9]', '_', keyword.lower())
    return os.path.join(CACHE_DIR, f"{safe_keyword}_{uuid.uuid4().hex[:6]}.mp4")


def _search_pexels_videos(keyword: str, per_page: int = 3) -> List[Dict]:
    """Search Pexels Videos API."""
    if not PEXELS_API_KEY:
        logger.error("PEXELS_API_KEY not set")
        raise RuntimeError("PEXELS_API_KEY not set")

    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": keyword,
        "per_page": per_page,
        "min_width": 1280,
        "min_height": 720
    }

    logger.info(f"Pexels API key loaded: {bool(PEXELS_API_KEY)} | Query: '{keyword}' | Params: {params}")

    response = requests.get(
        "https://api.pexels.com/videos/search",
        headers=headers,
        params=params,
        timeout=10
    )

    logger.info(f"Pexels response status: {response.status_code}")

    if response.status_code != 200:
        # log response body for debugging
        logger.error(f"Pexels API error {response.status_code}: {response.text}")
        raise RuntimeError(f"Pexels API error {response.status_code}: {response.text}")

    data = response.json()
    videos = data.get("videos", [])
    logger.info(f"Pexels returned {len(videos)} videos for query '{keyword}'")
    return videos


def _download_video_from_url(url: str, output_path: str) -> bool:
    """Download video from URL to cache."""
    logger.info(f"Starting download from URL: {url}")
    response = requests.get(url, timeout=60, stream=True)
    logger.info(f"Download response status: {response.status_code} for URL: {url}")
    try:
        response.raise_for_status()
    except Exception as e:
        logger.exception(f"Download response invalid for URL {url}: {e}")
        raise

    try:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logger.info(f"Saved video to {output_path}")
        return True
    except Exception as e:
        logger.exception(f"Failed to save video to {output_path}: {e}")
        raise


def _select_best_video_file(videos: List[Dict], visual_keywords: Optional[List[str]] = None) -> Optional[Dict]:
    """Choose best Pexels video file by orientation, resolution, duration, and keyword relevance."""
    candidates = []
    vk_lower = [k.lower() for k in (visual_keywords or [])]
    for video in videos:
        duration = float(video.get("duration") or 0)
        meta_text = ' '.join(filter(None, [str(video.get('url','')), str(video.get('user', {}).get('name','')), str(video.get('tags',''))])).lower()
        relevance = 0
        for kw in vk_lower:
            if kw and kw in meta_text:
                relevance += 1
        for file in video.get("video_files", []):
            width = int(file.get("width") or 0)
            height = int(file.get("height") or 0)
            if width < 1 or height < 1 or not file.get("link"):
                continue
            landscape = 1 if width >= height else 0
            score = (relevance, landscape, width * height, duration)
            candidates.append((score, file))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def _download_scene_variants(scene: str, max_clips: int = 4) -> List[str]:
    """Download multiple relevant Pexels clips for one scene."""
    variant_paths: List[str] = []
    visual_keywords = generate_visual_keywords(scene)
    logger.info(f"Scene visual keywords: {visual_keywords}")

    seen_urls = set()
    for vk in visual_keywords:
        if len(variant_paths) >= max_clips:
            break
        logger.info(f"Searching Pexels for scene variant: '{vk}'")
        videos = _search_pexels_videos(vk, per_page=8)
        if not videos:
            logger.info(f"No videos returned for keyword '{vk}'")
            continue

        sorted_files = sorted(
            [
                (file, video)
                for video in videos
                for file in video.get("video_files", [])
                if file.get("link") and int(file.get("width", 0)) >= 1280 and int(file.get("height", 0)) >= 720
            ],
            key=lambda item: (
                1 if int(item[0].get("width", 0)) >= int(item[0].get("height", 0)) else 0,
                int(item[0].get("width", 0)) * int(item[0].get("height", 0)),
                float(item[1].get("duration") or 0)
            ),
            reverse=True
        )

        for file, video in sorted_files:
            if len(variant_paths) >= max_clips:
                break
            url = file.get("link")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            logger.info(f"Selected variant URL: {url}")
            output_path = _get_cache_path(vk)
            _download_video_from_url(url, output_path)
            variant_paths.append(output_path)

    if not variant_paths:
        raise RuntimeError(f"No Pexels variants downloaded for scene: {scene}")

    return variant_paths


def download_scene_clips(scenes: List[str]) -> List[List[str]]:
    """
    Download multiple relevant video clips for each scene from Pexels.
    Returns a list of clip path lists per scene.
    """
    scene_clip_groups: List[List[str]] = []
    errors = []

    for idx, scene in enumerate(scenes):
        logger.info(f"Processing scene {idx + 1}/{len(scenes)}")
        try:
            if should_use_ai_video(scene):
                ai_prompt = build_ai_scene_prompt(scene)
                logger.info(f"Scene Type: cinematic/impossible | AI video attempt | Prompt: {ai_prompt}")
                try:
                    ai_path = generate_ai_video(ai_prompt, duration=5)
                    scene_clip_groups.append([ai_path])
                    logger.info(f"AI video generated for scene {idx + 1}: {ai_path}")
                    continue
                except Exception as exc:
                    logger.exception(f"AI generation failed for scene {idx + 1}: {exc}")
                    errors.append(f"scene {idx + 1} AI error: {exc}")

            variants = _download_scene_variants(scene, max_clips=4)
            scene_clip_groups.append(variants)
            logger.info(f"Downloaded {len(variants)} variants for scene {idx + 1}")
        except Exception as exc:
            logger.exception(f"Scene {idx + 1} failed to download variants: {exc}")
            errors.append(f"scene {idx + 1} download error: {exc}")
            scene_clip_groups.append([])

    if not any(scene_clip_groups):
        detail = "; ".join(errors) if errors else "No clips found or downloaded"
        raise RuntimeError(f"No MP4 files saved. Reasons: {detail}")

    return scene_clip_groups


# =====================================================
# VIDEO CLIP BUILDING
# =====================================================

def _apply_ken_burns_effect(
    clip: VideoFileClip,
    duration: float,
    zoom_level: float = 1.05
) -> VideoFileClip:
    """Apply subtle Ken Burns zoom effect (reduced memory footprint)."""
    try:
        # Use MoviePy's built-in zoom effect to avoid creating numpy arrays
        return clip
    
    except Exception as e:
        logger.warning(f"Ken Burns effect skipped: {e}")
        return clip


def _get_clip_for_scene(
    video_path: Optional[str],
    duration: float
) -> Optional[VideoFileClip]:
    """Load and prepare video clip for scene."""
    if not video_path or not os.path.exists(video_path):
        return None
    
    try:
        clip = VideoFileClip(video_path)
        
        if clip.duration < duration:
            clip = clip.loop(duration=duration)
        else:
            clip = clip.subclip(0, duration)
        
        clip = clip.set_duration(duration)
        
        if clip.size != (WIDTH, HEIGHT):
            aspect_ratio = clip.w / clip.h
            target_ratio = WIDTH / HEIGHT
            if aspect_ratio > target_ratio:
                clip = clip.resize(height=HEIGHT)
            else:
                clip = clip.resize(width=WIDTH)
            clip = clip.crop(
                x_center=clip.w / 2,
                y_center=clip.h / 2,
                width=WIDTH,
                height=HEIGHT
            )
        
        clip = clip.without_audio()
        clip = _apply_ken_burns_effect(clip, duration, zoom_level=1.05)
        
        return clip
    
    except Exception as e:
        logger.error(f"Failed to load clip {video_path}: {e}")
        return None


def _create_fallback_clip(duration: float) -> VideoFileClip:
    """Create fallback solid color clip without numpy arrays."""
    # Create a simple colored image and convert to clip
    fallback_img = Image.new("RGB", (WIDTH, HEIGHT), color=(20, 30, 60))
    clip = ImageClip(np.asarray(fallback_img)).set_duration(duration)
    return clip


# =====================================================
# TRANSITIONS
# =====================================================

def _fade_in_effect(clip: VideoFileClip, duration: float = 0.5) -> VideoFileClip:
    """Apply fade-in effect using built-in vfx."""
    try:
        return vfx.fadein(clip, min(0.5, clip.duration * 0.2))
    except Exception:
        return clip


def _fade_out_effect(clip: VideoFileClip, duration: float = 0.5) -> VideoFileClip:
    """Apply fade-out effect using built-in vfx."""
    try:
        return vfx.fadeout(clip, min(0.5, clip.duration * 0.2))
    except Exception:
        return clip


def apply_transitions(clips: List[VideoFileClip]) -> List[VideoFileClip]:
    """Apply fade in/out transitions to clips."""
    if not clips:
        return clips
    
    transitioned = []
    
    for idx, clip in enumerate(clips):
        if idx == 0:
            clip = _fade_in_effect(clip)
        
        if idx == len(clips) - 1:
            clip = _fade_out_effect(clip)
        else:
            clip = _fade_out_effect(clip, duration=0.3)
        
        transitioned.append(clip)
    
    return transitioned


# =====================================================
# SUBTITLES
# =====================================================

def add_subtitle_overlay(
    clip: VideoFileClip,
    subtitle_text: str,
    font_size: int = 32
) -> VideoFileClip:
    """Add subtitle overlay to video clip using PIL (memory-safe)."""
    if not subtitle_text or not subtitle_text.strip():
        return clip
    
    try:
        subtitle_text = subtitle_text.strip()[:100]  # Limit text length
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
        
        max_width = WIDTH - 60
        words = subtitle_text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        
        # Limit to 2 lines max for memory safety
        lines = lines[:2]
        
        text_height = len(lines) * (font_size + 4)
        padding = 8
        subtitle_h = text_height + padding * 2
        
        img = Image.new("RGBA", (WIDTH, subtitle_h), (0, 0, 0, 180))
        draw = ImageDraw.Draw(img)
        y = padding
        
        for line in lines:
            bbox = font.getbbox(line)
            text_w = bbox[2] - bbox[0]
            x = (WIDTH - text_w) / 2
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
            y += font_size + 4
        
        subtitle_clip = ImageClip(np.asarray(img)).set_duration(clip.duration)
        subtitle_clip = subtitle_clip.set_position(('center', HEIGHT - subtitle_h - 10))
        del img  # Explicit cleanup
        return CompositeVideoClip([clip, subtitle_clip])
    
    except Exception as e:
        logger.warning(f"Subtitle overlay failed: {e}")
        return clip


# =====================================================
# MOVIE BUILDING
# =====================================================

def build_movie_clips(
    scenes: List[str],
    video_groups: List[List[str]],
    narration_durations: Optional[List[float]] = None
) -> List[VideoFileClip]:
    """Build movie clips sequentially to reduce memory usage."""
    clips: List[VideoFileClip] = []
    
    for idx, scene in enumerate(scenes):
        group_paths = video_groups[idx] if idx < len(video_groups) else []
        if narration_durations and idx < len(narration_durations):
            duration = narration_durations[idx]
        else:
            duration = max(
                MIN_SCENE_DURATION,
                min(MAX_SCENE_DURATION, len(scene) / 20)
            )

        if not group_paths:
            video_clip = _create_fallback_clip(duration)
            logger.warning(f"Using fallback clip for scene {idx}")
        else:
            if len(group_paths) == 1:
                video_clip = _get_clip_for_scene(group_paths[0], duration)
            else:
                # Use only 2 segments max to reduce memory
                max_segments = min(len(group_paths), 2)
                variant_clips: List[VideoFileClip] = []
                remaining_duration = duration
                
                for clip_index, path in enumerate(group_paths[:max_segments]):
                    segment_duration = max(1.5, min(2.5, remaining_duration / (max_segments - clip_index)))
                    if clip_index == max_segments - 1:
                        segment_duration = remaining_duration
                    if segment_duration <= 0:
                        break

                    sub_clip = _get_clip_for_scene(path, segment_duration)
                    if sub_clip is None:
                        continue

                    sub_clip = sub_clip.without_audio()
                    variant_clips.append(sub_clip)
                    remaining_duration -= sub_clip.duration

                if not variant_clips:
                    video_clip = _create_fallback_clip(duration)
                    logger.warning(f"Using fallback clip for scene {idx} after variant load failure")
                elif len(variant_clips) == 1:
                    video_clip = variant_clips[0].set_duration(duration)
                else:
                    video_clip = concatenate_videoclips(variant_clips, method='chain')
                    if abs(video_clip.duration - duration) > 0.1:
                        video_clip = video_clip.set_duration(duration)
                    # Cleanup variant clips after concatenation
                    for v_clip in variant_clips:
                        try:
                            v_clip.close()
                        except:
                            pass
                    del variant_clips

            if video_clip is None:
                video_clip = _create_fallback_clip(duration)
                logger.warning(f"Created fallback clip for scene {idx}")

        video_clip = add_subtitle_overlay(video_clip, scene[:80])
        clips.append(video_clip)
        logger.info(f"Scene {idx + 1}/{len(scenes)} built (duration: {duration:.1f}s)")
    
    return clips


def build_final_video(
    clips: List[VideoFileClip],
    narration_path: Optional[str] = None,
    background_music_path: Optional[str] = None
) -> VideoFileClip:
    """Assemble final video with audio (memory-safe)."""
    if not clips:
        raise ValueError("No clips provided")
    
    # Concatenate clips with minimal memory overhead
    final_clip = concatenate_videoclips(clips, method='chain')
    audio_clips = []
    
    # Load narration with context manager semantics
    if narration_path and os.path.exists(narration_path):
        try:
            narration = AudioFileClip(narration_path)
            if narration.duration > final_clip.duration:
                narration = narration.subclip(0, final_clip.duration)
            audio_clips.append(narration)
            logger.info(f"Added narration ({narration.duration:.1f}s)")
        except Exception as e:
            logger.error(f"Narration loading failed: {e}")
    
    # Load background music with context manager semantics
    if background_music_path and os.path.exists(background_music_path):
        try:
            music = AudioFileClip(background_music_path)
            music = music.volumex(0.12)
            if music.duration < final_clip.duration:
                music = audio_loop(music, duration=final_clip.duration)
            else:
                music = music.subclip(0, final_clip.duration)
            audio_clips.append(music)
            logger.info(f"Added background music ({music.duration:.1f}s)")
        except Exception as e:
            logger.error(f"Background music loading failed: {e}")
    
    # Composite audio if multiple sources
    if audio_clips:
        try:
            if len(audio_clips) > 1:
                final_audio = CompositeAudioClip(audio_clips)
            else:
                final_audio = audio_clips[0]
            final_clip = final_clip.set_audio(final_audio)
        except Exception as e:
            logger.warning(f"Audio composition failed: {e}")
    
    # Store audio references for cleanup
    final_clip._audio_clips = audio_clips
    return final_clip


# =====================================================
# EXPORT
# =====================================================

def export_video(
    clip: VideoFileClip,
    output_path: Optional[str] = None
) -> str:
    """Export video to MP4 with upscaling to 1280x720 if needed."""
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(OUTPUT_DIR, f"video_{timestamp}.mp4")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        logger.info(f"Exporting video to {output_path} (upscaling {WIDTH}x{HEIGHT} -> 1280x720)")
        
        # Upscale to standard YouTube resolution if needed
        if (WIDTH, HEIGHT) != (1280, 720):
            export_clip = clip.resize(newsize=(1280, 720))
        else:
            export_clip = clip
        
        export_clip.write_videofile(
            output_path,
            fps=FPS,
            codec='libx264',
            audio_codec='aac',
            preset='fast',  # Faster encoding to reduce memory
            threads=2,  # Reduced threads to minimize memory
            verbose=False,
            logger=None
        )
        
        logger.info(f"Video exported successfully: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise
    finally:
        # Comprehensive cleanup
        if (WIDTH, HEIGHT) != (1280, 720):
            try:
                export_clip.close()
            except:
                pass
        
        try:
            clip.close()
        except:
            pass
        
        try:
            if hasattr(clip, 'audio') and clip.audio:
                clip.audio.close()
        except:
            pass
        
        if hasattr(clip, '_audio_clips') and clip._audio_clips:
            for a in clip._audio_clips:
                try:
                    a.close()
                except:
                    pass


# =====================================================
# MAIN GENERATOR
# =====================================================

def generate_video(
    script: str,
    narration_path: Optional[str] = None,
    background_music_path: Optional[str] = None,
    output_path: Optional[str] = None,
    intro_text: Optional[str] = None,
    outro_text: Optional[str] = None
) -> str:
    """
    Generate complete YouTube video from script (memory-safe).
    
    Args:
        script: Full video script
        narration_path: Path to narration audio
        background_music_path: Path to background music
        output_path: Output video path
        intro_text: Optional intro scene text (unused in memory-safe mode)
        outro_text: Optional outro scene text (unused in memory-safe mode)
    
    Returns:
        Path to output video file
    """
    logger.info("Starting video generation (memory-safe mode)...")
    narration_audio = None
    clips = []
    final_clip = None
    
    try:
        scenes = split_script_into_scenes(script)
        logger.info(f"Split into {len(scenes)} scenes (max {TEST_MAX_SCENES} for memory safety)")
        
        clip_paths = download_scene_clips(scenes)
        total_downloaded = sum(len(group) for group in clip_paths)
        logger.info(f"Downloaded {total_downloaded} video clips across {len(clip_paths)} scenes")
        
        # Load narration durations
        narration_durations = None
        if narration_path and os.path.exists(narration_path):
            try:
                narration_audio = AudioFileClip(narration_path)
                narration_durations = [
                    narration_audio.duration / len(scenes)
                    for _ in scenes
                ]
            except Exception as e:
                logger.warning(f"Failed to load narration durations: {e}")
        
        # Build clips sequentially
        clips = build_movie_clips(scenes, clip_paths, narration_durations)
        logger.info(f"Built {len(clips)} video clips")
        
        # Assemble final video
        final_clip = build_final_video(
            clips,
            narration_path=narration_path,
            background_music_path=background_music_path
        )
        
        # Export with cleanup
        output_file = export_video(final_clip, output_path)
        logger.info(f"Video generation complete: {output_file}")
        return output_file
    
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise
    
    finally:
        # Comprehensive cleanup in reverse order
        if final_clip:
            try:
                final_clip.close()
            except:
                pass
        
        for clip in clips:
            try:
                clip.close()
            except:
                pass
        
        if narration_audio:
            try:
                narration_audio.close()
            except:
                pass


# =====================================================
# UTILITY: ADD BACKGROUND MUSIC (LEGACY)
# =====================================================

def add_background_music_to_video(
    video_path: str,
    music_path: str,
    output_path: str
) -> str:
    """Add background music to existing video."""
    if not os.path.exists(video_path):
        raise FileNotFoundError(video_path)
    if not os.path.exists(music_path):
        raise FileNotFoundError(music_path)
    
    try:
        video = VideoFileClip(video_path)
        music = AudioFileClip(music_path).volumex(0.12)
        
        if music.duration < video.duration:
            music = music.speedx(video.duration / music.duration)
        else:
            music = music.subclip(0, video.duration)
        
        if video.audio:
            final_audio = CompositeAudioClip([video.audio, music])
        else:
            final_audio = music
        
        final_video = video.set_audio(final_audio)
        
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=24,
            verbose=False,
            logger=None
        )
        
        video.close()
        music.close()
        final_video.close()
        
        return output_path
    
    except Exception as e:
        logger.error(f"Failed to add background music: {e}")
        raise