"""
QUICK START GUIDE - Getting Your AI Media Operating System Running

This guide walks you through setting up and running your upgraded AI automation platform.
"""

# ========== STEP 1: ENVIRONMENT SETUP ==========

"""
1. Create .env file in project root:

OPENAI_API_KEY=sk-...
YOUTUBE_API_KEY=...
REPLICATE_API_KEY=... (optional)
RUNWAYML_API_KEY=... (optional)
ELEVENLABS_API_KEY=... (optional)

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

DATABASE_URL=sqlite:///./database/media_os.db
DEBUG=False
ENVIRONMENT=production
"""

# ========== STEP 2: INSTALL DEPENDENCIES ==========

"""
pip install -r requirements.txt
"""

# ========== STEP 3: INITIALIZE DATABASES ==========

from database.database import init_db

init_db()
print("✅ Databases initialized")


# ========== STEP 4: START SERVICES ==========

"""
Terminal 1 - Redis:
redis-server

Terminal 2 - Celery Worker:
celery -A celery_app worker --loglevel=info

Terminal 3 - FastAPI Backend:
uvicorn app:app --reload --host 0.0.0.0 --port 8000

Terminal 4 - Streamlit Frontend:
cd frontend
streamlit run app14.py
"""

# ========== STEP 5: FIRST VIDEO GENERATION ==========

import asyncio
import os
from services.orchestration_service import get_orchestration_service

async def create_first_video():
    """Create your first AI-generated video"""
    
    orchestration = get_orchestration_service()
    
    # Start the autonomous pipeline
    result = await orchestration.start_autonomous_pipeline({
        "topic": "The Future of AI in 2024",
        "language": "english",
        "duration": 300,  # 5 minutes
        "enable_dubbing": False,  # Set to True for multilingual
        "auto_upload": False,  # Set to True for YouTube upload
        "schedule_publish": False,
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "task_id": "first_video_test"
    })
    
    if result["status"] == "completed":
        print("✅ Video generation complete!")
        print(f"Video: {result['output'].get('video_path')}")
        print(f"Thumbnail: {result['output'].get('thumbnail_path')}")
        print(f"SEO Data: {result['output'].get('seo')}")
    else:
        print("❌ Video generation failed")
        print(result.get("error"))

# Run it
asyncio.run(create_first_video())

# ========== STEP 6: MONITOR PROGRESS ==========

from services.orchestration_service import get_orchestration_service

orchestration = get_orchestration_service()

# Check all active tasks
tasks = orchestration.get_all_active_tasks()
for task in tasks:
    print(f"Task {task['task_id']}: {task['progress']}%")

# ========== STEP 7: ACCESS DASHBOARD ==========

"""
Open browser to http://localhost:8501

The Streamlit dashboard provides:
- One-click video generation
- Real-time progress monitoring
- Analytics and performance tracking
- Settings and API key management
"""

# ========== ADVANCED: CUSTOM AGENT USAGE ==========

from agents.research_agent import ResearchAgent
from agents.script_agent import ScriptAgent
from agents.seo_agent import SEOAgent

async def advanced_workflow():
    """Advanced example using individual agents"""
    
    # Create agents
    research = ResearchAgent()
    script = ScriptAgent()
    seo = SEOAgent()
    
    # Research phase
    research_task = {
        "topic": "Quantum Computing",
        "language": "english"
    }
    research_result = await research.execute_task(
        await research._think(research_task),
        research_task
    )
    print("✅ Research complete")
    
    # Scripting phase (uses research results)
    script_task = {
        "topic": "Quantum Computing",
        "research_data": research_result.get("research_data", {}),
        "duration": 300
    }
    script_result = await script.execute_task(
        await script._think(script_task),
        script_task
    )
    print("✅ Script generated")
    
    # SEO phase
    seo_task = {
        "topic": "Quantum Computing",
        "research_data": research_result.get("research_data", {})
    }
    seo_result = await seo.execute_task(
        await seo._think(seo_task),
        seo_task
    )
    print("✅ SEO optimization complete")
    
    print(f"Estimated CTR: {seo_result['seo_optimization'].get('estimated_ctr', 0):.2%}")
    print(f"Viral Probability: {seo_result['seo_optimization'].get('viral_probability', 0):.2%}")

# asyncio.run(advanced_workflow())

# ========== USING MEMORY SERVICE ==========

from services.memory_service import get_memory_service

memory = get_memory_service()

# Save a video record after publishing
memory.save_video_record({
    "video_id": "ABC123",
    "topic": "AI Future",
    "title": "The Future of AI",
    "published_at": "2024-01-15",
    "ctr": 0.08,
    "watch_time_minutes": 3.5,
    "retention_percentage": 52,
    "likes": 150,
    "comments": 45,
    "shares": 12
})

# Get best performing topics
best_topics = memory.get_best_performing_topics(5)
print("🏆 Best Performing Topics:")
for topic in best_topics:
    print(f"  - {topic['topic']}: {topic['avg_ctr']:.2%} CTR")

# Get audience interests
interests = memory.get_audience_interests(5)
print("👥 Top Audience Interests:")
for interest in interests:
    print(f"  - {interest['topic']}: {interest['interest_score']:.1f}")

# ========== MULTILINGUAL DUBBING ==========

from services.dubbing_service import get_dubbing_service

async def create_multilingual_version():
    """Create dubbed versions in multiple languages"""
    
    dubbing = get_dubbing_service()
    
    result = await dubbing.create_multilingual_versions(
        video_path="renders/video.mp4",
        original_script="Your original script here...",
        original_audio_path="renders/audio.mp3",
        languages=["urdu", "hindi", "spanish"]
    )
    
    if result["status"] == "success":
        print("✅ Multilingual versions created:")
        for lang, data in result["dubbed_videos"].items():
            print(f"  - {lang}: {data.get('dubbed_video_path')}")

# asyncio.run(create_multilingual_version())

# ========== GENERATE SHORTS ==========

from services.shorts_service import get_shorts_service

async def generate_shorts():
    """Convert video to vertical shorts"""
    
    shorts = get_shorts_service()
    
    result = await shorts.generate_shorts_from_video(
        video_path="renders/video.mp4",
        num_shorts=3,
        max_duration=60
    )
    
    if result["status"] == "success":
        print(f"✅ Generated {result['total_shorts']} shorts:")
        for short in result['shorts']:
            print(f"  - {short['path']}")

# asyncio.run(generate_shorts())

# ========== SEO & VIRALITY PREDICTION ==========

from agents.seo_agent import SEOAgent

async def predict_video_performance():
    """Predict CTR and viral probability"""
    
    seo = SEOAgent()
    
    # Predict CTR
    ctr = await seo.predict_ctr(
        title="The Future of AI: What You Need to Know",
        thumbnail="path/to/thumbnail.jpg",
        script="Your script preview..."
    )
    
    # Predict virality
    viral_prob = await seo.predict_virality({
        "topic": "AI",
        "hook_strength": 0.9,
        "novelty": 0.8,
        "emotional_appeal": 0.85
    })
    
    print(f"📊 Predictions:")
    print(f"  - Expected CTR: {ctr:.2%}")
    print(f"  - Viral Probability: {viral_prob:.2%}")

# asyncio.run(predict_video_performance())

# ========== CONFIGURATION TIPS ==========

"""
GPU ACCELERATION:
- Set ENABLE_GPU_RENDERING=True in config/settings.py
- Install: pip install torch torchvision cuda-python
- Significantly speeds up video rendering

PRODUCTION DEPLOYMENT:
- Set ENVIRONMENT=production in .env
- Use PostgreSQL instead of SQLite
- Deploy on cloud (AWS, GCP, Azure)
- Use S3/GCS for video storage
- Set up load balancer for FastAPI

MONITORING:
- Check logs/ directory for detailed logs
- Use Streamlit dashboard for real-time monitoring
- Set up alerts for failed tasks

OPTIMIZATION:
- Adjust VIDEO_BITRATE for quality vs size
- Use ENABLE_GPU_RENDERING for faster processing
- Implement caching in memory_service
- Profile code for bottlenecks
"""

# ========== COMMON ERRORS & SOLUTIONS ==========

"""
Error: "OPENAI_API_KEY not found"
Solution: Add OPENAI_API_KEY to .env file

Error: "Redis connection refused"
Solution: Make sure Redis is running (redis-server)

Error: "MoviePy not available"
Solution: pip install moviepy

Error: "Video rendering too slow"
Solution: 
- Reduce VIDEO_RESOLUTION in settings
- Enable GPU rendering
- Use Replicate API instead of local rendering

Error: "Memory database locked"
Solution: Close other connections to database, restart service
"""

print("✅ Quick Start Guide Complete!")
print("📖 For full documentation, see SYSTEM_UPGRADE_README.md")
print("🚀 Start creating videos with: python -c 'asyncio.run(create_first_video())'")
