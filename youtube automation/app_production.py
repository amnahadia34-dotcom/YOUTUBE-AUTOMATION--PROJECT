"""
Production-Grade FastAPI Backend
Integrates all AI services with modern API design, WebSockets, and authentication
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, UploadFile, File, Query
from fastapi.security import HTTPBearer, HTTPAuthCredentialBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import asyncio
from datetime import datetime
from utils.logger import logger
from config.settings import DEBUG, ENVIRONMENT
from database.manager import db
from database.models import VideoStatusEnum, TaskStatusEnum
from models.schemas import TaskRequest

# Import services
from services.security import auth_manager, rate_limiter, api_key_manager, secure_file_manager
from services.topic_intelligence import topic_engine
from services.script_psychology import script_engine
from services.ai_media_orchestrator import ai_orchestrator, WorkflowConfig
from services.learning_loop import learning_loop

# ========== REQUEST/RESPONSE MODELS ==========

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user_id: str
    message: str


class TopicRequest(BaseModel):
    """Request for topic/trend analysis"""
    niche: Optional[str] = None
    num_topics: int = Field(default=10, ge=1, le=50)


class TopicResponse(BaseModel):
    topics: List[Dict[str, Any]]
    analysis_timestamp: str


class GenerateContentRequest(BaseModel):
    """Request to generate content autonomously"""
    topic: str
    content_type: str = "full_video"
    language: str = "english"
    auto_upload: bool = False
    generate_shorts: bool = True
    auto_thumbnail: bool = True
    target_retention: float = 75.0


class WorkflowStatusResponse(BaseModel):
    """Workflow status response"""
    workflow_id: str
    status: str  # processing, completed, failed
    stages: Dict[str, Any]
    progress: float
    timestamp: str


# ========== APPLICATION SETUP ==========

app = FastAPI(
    title="AI Media Operating System",
    description="Production-grade AI-powered YouTube automation platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEBUG else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    expose_headers=["*"]
)

# ========== AUTHENTICATION DEPENDENCY ==========

def verify_token(token: str = Depends(HTTPBearer())) -> Dict:
    """Verify JWT token"""
    try:
        payload = auth_manager.verify_token(token.credentials)
        return payload
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def check_rate_limit(user_id: str = Depends(verify_token)) -> str:
    """Check rate limiting"""
    if not rate_limiter.is_allowed(user_id.get("user_id")):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )
    return user_id.get("user_id")


# ========== HEALTH & SYSTEM ==========

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Media Operating System 🚀",
        "version": "2.0.0",
        "environment": ENVIRONMENT,
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }


# ========== AUTHENTICATION ENDPOINTS ==========

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """User login - returns JWT token"""
    
    try:
        # TODO: Verify credentials against database
        # This is a simplified example
        
        token = auth_manager.create_token(
            user_id="user123",
            email=request.email
        )
        
        logger.info(f"User logged in: {request.email}")
        
        return LoginResponse(
            token=token,
            user_id="user123",
            message="Login successful"
        )
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=400, detail="Login failed")


# ========== TOPIC & INTELLIGENCE ENDPOINTS ==========

@app.post("/api/v1/topics/detect", response_model=TopicResponse)
async def detect_viral_topics(
    request: TopicRequest,
    user_id: str = Depends(check_rate_limit)
):
    """Detect viral topics and opportunities"""
    
    try:
        logger.info(f"Detecting viral topics for user: {user_id}")
        
        opportunities = await topic_engine.detect_viral_topics(
            user_id,
            niche=request.niche,
            num_topics=request.num_topics
        )
        
        topics_data = [
            {
                "topic": opp.topic,
                "keyword": opp.keyword,
                "viral_score": opp.viral_score,
                "opportunity_score": opp.opportunity_score,
                "virality_tier": opp.virality_tier.value,
                "search_volume": opp.search_volume,
                "growth_rate": opp.growth_rate,
                "competition_level": opp.competition_level,
                "predicted_ctr": opp.predicted_ctr,
                "predicted_retention": opp.predicted_retention,
                "recommended_content_types": opp.recommended_content_types
            }
            for opp in opportunities
        ]
        
        return TopicResponse(
            topics=topics_data,
            analysis_timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error detecting topics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/topics/niche-recommendations")
async def get_niche_recommendations(user_id: str = Depends(check_rate_limit)):
    """Get AI niche recommendations"""
    
    try:
        recommendations = await topic_engine.get_niche_recommendations(user_id)
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting niche recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/learning-state")
async def get_learning_state(user_id: str = Depends(check_rate_limit)):
    """Get AI learning state for user"""
    
    try:
        learning_state = db.get_learning_state(user_id)
        
        return {
            "user_id": user_id,
            "high_performing_title_patterns": learning_state.high_performing_title_patterns,
            "effective_pacing_styles": learning_state.effective_pacing_styles,
            "average_performance_score": learning_state.average_performance_score,
            "total_videos_analyzed": learning_state.total_videos_analyzed
        }
        
    except Exception as e:
        logger.error(f"Error getting learning state: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== CONTENT GENERATION ENDPOINTS ==========

@app.post("/api/v1/content/generate-autonomous")
async def generate_content_autonomous(
    request: GenerateContentRequest,
    user_id: str = Depends(check_rate_limit)
):
    """Start autonomous content generation workflow"""
    
    try:
        logger.info(f"Starting autonomous content generation for user: {user_id}")
        
        # Get user's primary channel
        channels = db.get_user_channels(user_id)
        if not channels:
            raise HTTPException(status_code=400, detail="No YouTube channel configured")
        
        channel_id = channels[0].id
        
        # Create workflow config
        workflow_config = WorkflowConfig(
            user_id=user_id,
            channel_id=channel_id,
            topic=request.topic,
            content_type=request.content_type,
            autonomous_mode=True,
            auto_upload=request.auto_upload,
            generate_shorts=request.generate_shorts,
            auto_thumbnail=request.auto_thumbnail,
            target_retention=request.target_retention,
            language=request.language
        )
        
        # Start workflow
        workflow_result = await ai_orchestrator.start_autonomous_workflow(workflow_config)
        
        return {
            "workflow_id": workflow_result.get("user_id"),
            "status": workflow_result.get("status"),
            "stages": workflow_result.get("stages"),
            "timestamp": workflow_result.get("start_time")
        }
        
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/content/generate-script")
async def generate_script(
    topic: str = Query(...),
    video_type: str = Query("full_video"),
    duration: int = Query(600),
    language: str = Query("english"),
    user_id: str = Depends(check_rate_limit)
):
    """Generate high-retention script only"""
    
    try:
        from services.script_psychology import HookType, PacingStyle
        
        script_result = await script_engine.generate_high_retention_script(
            topic=topic,
            video_type=video_type,
            duration_seconds=duration,
            hook_type=HookType.CURIOSITY_GAP,
            pacing_style=PacingStyle.FAST_PACED,
            target_retention=75.0,
            audience="general",
            tone="energetic",
            language=language
        )
        
        return {
            "script": script_result["script"],
            "hook": script_result.get("hook", {}).get("hook_text", ""),
            "retention_strategy": script_result.get("retention_strategy"),
            "psychological_triggers": script_result.get("psychological_triggers", [])
        }
        
    except Exception as e:
        logger.error(f"Error generating script: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== VIDEO MANAGEMENT ENDPOINTS ==========

@app.get("/api/v1/videos")
async def list_videos(
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    user_id: str = Depends(check_rate_limit)
):
    """List user's videos"""
    
    try:
        videos = db.get_user_videos(user_id, limit=limit)
        
        return {
            "videos": [
                {
                    "id": v.id,
                    "title": v.title,
                    "status": v.status.value,
                    "viral_score": v.viral_score,
                    "created_at": v.created_at.isoformat(),
                    "views": v.actual_views,
                    "ctr": v.actual_ctr
                }
                for v in videos
            ],
            "total": len(videos)
        }
        
    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/videos/{video_id}")
async def get_video(
    video_id: str,
    user_id: str = Depends(check_rate_limit)
):
    """Get video details"""
    
    try:
        video = db.get_video(video_id)
        if not video or video.user_id != user_id:
            raise HTTPException(status_code=404, detail="Video not found")
        
        analytics = db.get_video_analytics_history(video_id, days=30)
        
        return {
            "id": video.id,
            "title": video.title,
            "description": video.description,
            "status": video.status.value,
            "progress": video.progress_percent,
            "viral_score": video.viral_score,
            "created_at": video.created_at.isoformat(),
            "analytics": [
                {
                    "views": a.views,
                    "ctr": a.ctr,
                    "retention": a.avg_view_percentage,
                    "recorded_at": a.recorded_at.isoformat()
                }
                for a in analytics
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== WEBSOCKET PROGRESS UPDATES ==========

@app.websocket("/ws/workflow/{workflow_id}")
async def websocket_workflow_updates(websocket: WebSocket, workflow_id: str):
    """WebSocket endpoint for real-time workflow progress"""
    
    await websocket.accept()
    
    try:
        while True:
            # Get current status
            video = db.get_video(workflow_id)
            
            if video:
                update = {
                    "workflow_id": workflow_id,
                    "status": video.status.value,
                    "progress": video.progress_percent,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await websocket.send_json(update)
            
            # Update every 2 seconds
            await asyncio.sleep(2)
            
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()


# ========== ANALYTICS ENDPOINTS ==========

@app.post("/api/v1/analytics/record")
async def record_video_analytics(
    video_id: str = Query(...),
    views: int = Query(...),
    likes: int = Query(...),
    comments: int = Query(...),
    shares: int = Query(...),
    ctr: float = Query(...),
    user_id: str = Depends(check_rate_limit)
):
    """Record video performance metrics"""
    
    try:
        video = db.get_video(video_id)
        if not video or video.user_id != user_id:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Record analytics
        db.record_video_analytics(
            video_id=video_id,
            views=views,
            likes=likes,
            comments=comments,
            shares=shares,
            ctr=ctr
        )
        
        # Update actual performance
        video.actual_views = views
        video.actual_likes = likes
        video.actual_comments = comments
        video.actual_ctr = ctr
        
        # Trigger learning analysis
        asyncio.create_task(learning_loop.analyze_video_performance(video_id, user_id))
        
        return {"status": "recorded", "video_id": video_id}
        
    except Exception as e:
        logger.error(f"Error recording analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/recommendations")
async def get_ai_recommendations(user_id: str = Depends(check_rate_limit)):
    """Get personalized AI recommendations"""
    
    try:
        recommendations = await learning_loop.get_personalized_recommendations(user_id)
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== FILE UPLOAD ENDPOINTS ==========

@app.post("/api/v1/upload/video")
async def upload_video(
    file: UploadFile = File(...),
    user_id: str = Depends(check_rate_limit)
):
    """Upload video file"""
    
    try:
        # Validate
        file_size = len(await file.read())
        await file.seek(0)
        
        if not secure_file_manager.validate_upload(
            file.filename, "video", file_size
        ):
            raise HTTPException(status_code=400, detail="Invalid file")
        
        # Save file
        filename = secure_file_manager.sanitize_filename(f"{user_id}_{file.filename}")
        path = f"uploads/{filename}"
        
        with open(path, 'wb') as f:
            f.write(await file.read())
        
        return {"filename": filename, "path": path, "size": file_size}
        
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== ERROR HANDLERS ==========

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return {
        "error": True,
        "detail": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=DEBUG
    )
