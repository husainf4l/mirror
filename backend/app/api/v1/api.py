from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from backend.app.core.auth import verify_password, require_auth
from backend.app.core.livekit_service import livekit_service
from backend.app.core.config import settings
import asyncio
import json

api_router = APIRouter()

@api_router.get("/")
def api_root():
    """API root endpoint"""
    return {"message": "Wedding Mirror API", "version": "1.0.0"}

@api_router.post("/login")
def login(password: str = Form(...)):
    """Handle login form submission - returns JSON for React"""
    if verify_password(password):
        response = JSONResponse({
            "success": True,
            "message": "Login successful"
        })
        response.set_cookie(
            key="mirror_auth",
            value=password,  # Simple: store password as cookie
            max_age=86400,  # 24 hours
            httponly=True,
            secure=False  # Set to True if using HTTPS
        )
        return response
    else:
        return JSONResponse({
            "success": False,
            "error": "Invalid password. Please try again."
        }, status_code=401)

@api_router.post("/logout")
def logout():
    """Logout and clear auth cookie - returns JSON"""
    response = JSONResponse({"success": True, "message": "Logged out successfully"})
    response.delete_cookie(key="mirror_auth")
    return response

@api_router.get("/mirror")
def mirror_display(authenticated: bool = Depends(require_auth)):
    """API endpoint to get mirror state - requires authentication"""
    # Import here to avoid circular imports
    from backend.app.main import current_text, original_text
    return {
        "success": True,
        "current_text": current_text,
        "original_text": original_text
    }

@api_router.post("/livekit/token")
async def get_livekit_token(request: Request):
    """Generate LiveKit access token for joining a room"""
    data = await request.json()
    
    room_name = data.get("room", "mirror-room")
    participant_name = data.get("name", "Anonymous")
    identity = data.get("identity", participant_name)
    
    try:
        connection_details = livekit_service.get_connection_details(
            room_name=room_name,
            participant_name=participant_name,
            identity=identity
        )
        
        return {
            "success": True,
            "token": connection_details["token"],
            "url": connection_details["url"],
            "room": room_name,
            "identity": identity
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@api_router.post("/livekit/viewer-token")
async def get_livekit_viewer_token(request: Request, authenticated: bool = Depends(require_auth)):
    """Generate LiveKit viewer token for admins to view rooms"""
    data = await request.json()
    
    room_name = data.get("room", "mirror-room")
    participant_name = data.get("name", "Admin Viewer")
    identity = data.get("identity", f"admin-{room_name}")
    
    try:
        connection_details = livekit_service.get_viewer_connection_details(
            room_name=room_name,
            participant_name=participant_name,
            identity=identity
        )
        
        return {
            "success": True,
            "token": connection_details["token"],
            "url": connection_details["url"],
            "room": room_name,
            "identity": identity,
            "viewer_mode": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@api_router.get("/livekit/config")
def get_livekit_config():
    """Get LiveKit configuration for frontend"""
    return {
        "url": settings.LIVEKIT_URL,
        "default_room": "mirror-room"
    }

@api_router.get("/events")
async def stream_events(request: Request):
    """Server-sent events for real-time mirror updates"""
    # Import here to avoid circular imports
    from backend.app.main import connected_clients, current_text
    
    async def event_generator():
        client_queue = asyncio.Queue()
        connected_clients.append(client_queue)
        
        try:
            # Send initial connection confirmation
            initial_message = {
                "type": "connected", 
                "message": "Connected to mirror",
                "current_text": current_text
            }
            yield f"data: {json.dumps(initial_message)}\n\n"
            
            # Listen for messages
            while True:
                try:
                    # Wait for message with timeout to send periodic pings
                    message = await asyncio.wait_for(client_queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    ping_message = {"type": "ping", "timestamp": asyncio.get_event_loop().time()}
                    yield f"data: {json.dumps(ping_message)}\n\n"
                    
        except Exception as e:
            print(f"SSE client disconnected: {e}")
        finally:
            # Remove client from connected list
            if client_queue in connected_clients:
                connected_clients.remove(client_queue)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
        }
    )

@api_router.get("/rooms")
def list_rooms(authenticated: bool = Depends(require_auth)):
    """List all active LiveKit rooms"""
    try:
        rooms = livekit_service.list_rooms()
        return {
            "success": True, 
            "rooms": rooms,
            "count": len(rooms)
        }
    except Exception as e:
        return {
            "success": False, 
            "error": str(e),
            "rooms": []
        }

@api_router.delete("/rooms")
def delete_all_rooms(authenticated: bool = Depends(require_auth)):
    """Delete all active LiveKit rooms"""
    return livekit_service.delete_all_rooms()

@api_router.post("/guest/search")
def search_guest(request: Request):
    """Search for a guest in the wedding database"""
    print("\n" + "="*50)
    print("🔍 GUEST SEARCH REQUEST RECEIVED")
    print("="*50)
    
    try:
        import json
        body = asyncio.run(request.body())
        data = json.loads(body.decode())
        guest_name = data.get("name", "").strip().lower()
        
        print(f"📥 Raw request data: {data}")
        print(f"🏷️  Extracted guest name: '{guest_name}'")
        
        if not guest_name:
            print("❌ No name provided in request")
            return JSONResponse({
                "found": False,
                "message": "No name provided"
            }, status_code=400)
        
        # Try to connect to database and search for guest
        try:
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker
            import os
            
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                return JSONResponse({
                    "found": False,
                    "message": "Database not configured"
                })
            
            # Convert async URL to sync URL for synchronous SQLAlchemy
            sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
            
            print(f"🗄️  Connecting to database...")
            print(f"🔗 Original URL: {database_url[:50]}...")
            print(f"🔄 Sync URL: {sync_database_url[:50]}...")
            
            # Create engine with specific settings for PostgreSQL
            engine = create_engine(
                sync_database_url, 
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False  # Set to True for SQL debugging
            )
            Session = sessionmaker(bind=engine)
            session = Session()
            
            print(f"✅ Database connection established!")
            print(f"🎯 Starting search for guest: '{guest_name}'")
            
            # Clean and prepare search terms
            search_name = guest_name.strip()
            search_words = [word.strip() for word in search_name.split() if word.strip()]
            
            print(f"🧹 Cleaned search name: '{search_name}'")
            print(f"📝 Search words: {search_words}")
            print(f"🔢 Number of words: {len(search_words)}")
            
            # Try multiple search strategies in order of preference
            result = None
            search_strategy_used = None
            
            print("\n🔍 SEARCH STRATEGY 1: Exact full name match")
            # Strategy 1: Exact full name match (highest priority)
            if len(search_words) >= 2:
                full_name_queries = [
                    f"{search_words[0]} {search_words[1]}",  # First Last
                    f"{search_words[1]} {search_words[0]}",  # Last First
                    " ".join(search_words)  # All words as provided
                ]
                print(f"📋 Trying full name combinations: {full_name_queries}")
                
                for i, full_name in enumerate(full_name_queries):
                    print(f"   🔸 Attempt {i+1}: Searching for '{full_name}'")
                    query = text("""
                        SELECT first_name, last_name, phone, seat_number, relation, message, story, about
                        FROM guests 
                        WHERE LOWER(TRIM(first_name || ' ' || last_name)) = LOWER(:full_name)
                           OR LOWER(TRIM(last_name || ' ' || first_name)) = LOWER(:full_name)
                        LIMIT 1
                    """)
                    result = session.execute(query, {"full_name": full_name}).fetchone()
                    if result:
                        search_strategy_used = f"Strategy 1 - Full name match: '{full_name}'"
                        print(f"   ✅ FOUND with Strategy 1!")
                        break
                    else:
                        print(f"   ❌ No match for '{full_name}'")
            else:
                print("   ⚠️  Skipped (less than 2 words provided)")
            
            # Strategy 2: Individual name component exact match
            if not result:
                print("\n🔍 SEARCH STRATEGY 2: Individual name component exact match")
                for i, word in enumerate(search_words):
                    print(f"   🔸 Attempt {i+1}: Searching for exact match of '{word}'")
                    query = text("""
                        SELECT first_name, last_name, phone, seat_number, relation, message, story, about
                        FROM guests 
                        WHERE LOWER(TRIM(first_name)) = LOWER(:word)
                           OR LOWER(TRIM(last_name)) = LOWER(:word)
                        LIMIT 1
                    """)
                    result = session.execute(query, {"word": word}).fetchone()
                    if result:
                        search_strategy_used = f"Strategy 2 - Individual name match: '{word}'"
                        print(f"   ✅ FOUND with Strategy 2!")
                        break
                    else:
                        print(f"   ❌ No exact match for '{word}'")
            
            # Strategy 3: Partial name match (fuzzy search)
            if not result:
                print("\n🔍 SEARCH STRATEGY 3: Partial name match (fuzzy search)")
                for i, word in enumerate(search_words):
                    if len(word) >= 3:  # Only search words with 3+ characters
                        print(f"   🔸 Attempt {i+1}: Fuzzy search for '{word}' (contains)")
                        query = text("""
                            SELECT first_name, last_name, phone, seat_number, relation, message, story, about
                            FROM guests 
                            WHERE LOWER(first_name) LIKE LOWER(:partial)
                               OR LOWER(last_name) LIKE LOWER(:partial)
                            ORDER BY 
                                CASE 
                                    WHEN LOWER(first_name) LIKE LOWER(:exact_start) THEN 1
                                    WHEN LOWER(last_name) LIKE LOWER(:exact_start) THEN 2
                                    ELSE 3
                                END
                            LIMIT 1
                        """)
                        result = session.execute(query, {
                            "partial": f"%{word}%",
                            "exact_start": f"{word}%"
                        }).fetchone()
                        if result:
                            search_strategy_used = f"Strategy 3 - Partial match: '{word}'"
                            print(f"   ✅ FOUND with Strategy 3!")
                            break
                        else:
                            print(f"   ❌ No partial match for '{word}'")
                    else:
                        print(f"   ⚠️  Skipped '{word}' (less than 3 characters)")
            
            # Strategy 4: Very flexible search - any part of any name
            if not result:
                print("\n🔍 SEARCH STRATEGY 4: Very flexible search (any part of name)")
                print(f"   🔸 Searching for '{search_name}' anywhere in full name")
                query = text("""
                    SELECT first_name, last_name, phone, seat_number, relation, message, story, about
                    FROM guests 
                    WHERE LOWER(first_name || ' ' || last_name) LIKE LOWER(:search_term)
                       OR LOWER(last_name || ' ' || first_name) LIKE LOWER(:search_term)
                    LIMIT 1
                """)
                result = session.execute(query, {"search_term": f"%{search_name}%"}).fetchone()
                if result:
                    search_strategy_used = f"Strategy 4 - Flexible search: '{search_name}'"
                    print(f"   ✅ FOUND with Strategy 4!")
                else:
                    print(f"   ❌ No flexible match for '{search_name}'")
            
            session.close()
            
            print("\n" + "="*50)
            if result:
                guest_info = {
                    "name": f"{result[0]} {result[1]}" if result[0] and result[1] else guest_name,
                    "first_name": result[0],
                    "last_name": result[1],
                    "phone": result[2],
                    "table_number": result[3],
                    "relationship": result[4],
                    "message": result[5],
                    "story": result[6],
                    "about": result[7]
                }
                
                print("🎉 GUEST FOUND!")
                print(f"👤 Name: {guest_info['name']}")
                print(f"📞 Phone: {guest_info['phone']}")
                print(f"🪑 Seat: {guest_info['table_number']}")
                print(f"👥 Relationship: {guest_info['relationship']}")
                print(f"🎯 Found using: {search_strategy_used}")
                print("="*50)
                
                return JSONResponse({
                    "found": True,
                    "guest": guest_info
                })
            else:
                print("❌ GUEST NOT FOUND!")
                print(f"🔍 Searched for: '{guest_name}'")
                print(f"📝 Search words: {search_words}")
                print("💡 Try checking spelling or using different name variations")
                print("="*50)
                
                return JSONResponse({
                    "found": False,
                    "message": f"Guest '{guest_name}' not found in database"
                })
                
        except Exception as db_error:
            print("\n" + "="*50)
            print("❌ DATABASE ERROR!")
            print(f"🚨 Error: {db_error}")
            print("="*50)
            return JSONResponse({
                "found": False,
                "message": f"Database error: {str(db_error)}"
            })
            
    except Exception as e:
        print("\n" + "="*50)
        print("❌ REQUEST PROCESSING ERROR!")
        print(f"🚨 Error: {str(e)}")
        print("="*50)
        return JSONResponse({
            "found": False, 
            "message": f"Error processing request: {str(e)}"
        }, status_code=500)


# ========================================
# GUEST MANAGEMENT ENDPOINTS
# ========================================

@api_router.get("/guests")
def list_guests(authenticated: bool = Depends(require_auth)):
    """Get all guests from the database"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return JSONResponse({
                "success": False,
                "message": "Database not configured"
            })
        
        # Convert async URL to sync URL
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Import models
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from models import Guest, RelationType
        
        # Get all guests with their relation types
        guests = session.query(Guest).join(RelationType, Guest.relation_type_id == RelationType.id, isouter=True).all()
        
        guests_list = []
        for guest in guests:
            guests_list.append({
                "id": guest.id,
                "first_name": guest.first_name,
                "last_name": guest.last_name,
                "full_name": f"{guest.first_name} {guest.last_name}",
                "phone": guest.phone,
                "seat_number": guest.seat_number,
                "relation": guest.relation,
                "relation_type": guest.relation_type.name if guest.relation_type else None,
                "message": guest.message,
                "story": guest.story,
                "about": guest.about,
                "created_at": guest.created_at.isoformat() if guest.created_at else None,
                "updated_at": guest.updated_at.isoformat() if guest.updated_at else None
            })
        
        session.close()
        
        return JSONResponse({
            "success": True,
            "guests": guests_list,
            "total": len(guests_list)
        })
        
    except Exception as e:
        print(f"Error fetching guests: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error fetching guests: {str(e)}"
        }, status_code=500)


@api_router.post("/guests")
def create_guest(request: Request, authenticated: bool = Depends(require_auth)):
    """Create a new guest"""
    try:
        import json
        body = asyncio.run(request.body())
        data = json.loads(body.decode())
        
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        from datetime import datetime
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        from models import Guest, RelationType
        
        # Get relation type if provided
        relation_type = None
        if data.get("relation_type_id"):
            relation_type = session.query(RelationType).filter_by(id=data["relation_type_id"]).first()
        
        # Create new guest
        new_guest = Guest(
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            phone=data.get("phone"),
            seat_number=data.get("seat_number"),
            relation=data.get("relation"),
            relation_type_id=data.get("relation_type_id"),
            message=data.get("message"),
            story=data.get("story"),
            about=data.get("about"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(new_guest)
        session.commit()
        
        # Get the created guest with ID
        guest_id = new_guest.id
        session.refresh(new_guest)
        session.close()
        
        return JSONResponse({
            "success": True,
            "message": "Guest created successfully",
            "guest_id": guest_id
        })
        
    except Exception as e:
        print(f"Error creating guest: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error creating guest: {str(e)}"
        }, status_code=500)


@api_router.put("/guests/{guest_id}")
def update_guest(guest_id: int, request: Request, authenticated: bool = Depends(require_auth)):
    """Update an existing guest"""
    try:
        import json
        body = asyncio.run(request.body())
        data = json.loads(body.decode())
        
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        from datetime import datetime
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        from models import Guest
        
        # Find the guest
        guest = session.query(Guest).filter_by(id=guest_id).first()
        if not guest:
            session.close()
            return JSONResponse({
                "success": False,
                "message": "Guest not found"
            }, status_code=404)
        
        # Update guest fields
        guest.first_name = data.get("first_name", guest.first_name)
        guest.last_name = data.get("last_name", guest.last_name)
        guest.phone = data.get("phone", guest.phone)
        guest.seat_number = data.get("seat_number", guest.seat_number)
        guest.relation = data.get("relation", guest.relation)
        guest.relation_type_id = data.get("relation_type_id", guest.relation_type_id)
        guest.message = data.get("message", guest.message)
        guest.story = data.get("story", guest.story)
        guest.about = data.get("about", guest.about)
        guest.updated_at = datetime.utcnow()
        
        session.commit()
        session.close()
        
        return JSONResponse({
            "success": True,
            "message": "Guest updated successfully"
        })
        
    except Exception as e:
        print(f"Error updating guest: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error updating guest: {str(e)}"
        }, status_code=500)


@api_router.delete("/guests/{guest_id}")
def delete_guest(guest_id: int, authenticated: bool = Depends(require_auth)):
    """Delete a guest"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        from models import Guest
        
        # Find and delete the guest
        guest = session.query(Guest).filter_by(id=guest_id).first()
        if not guest:
            session.close()
            return JSONResponse({
                "success": False,
                "message": "Guest not found"
            }, status_code=404)
        
        session.delete(guest)
        session.commit()
        session.close()
        
        return JSONResponse({
            "success": True,
            "message": "Guest deleted successfully"
        })
        
    except Exception as e:
        print(f"Error deleting guest: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error deleting guest: {str(e)}"
        }, status_code=500)


@api_router.get("/relation-types")
def list_relation_types(authenticated: bool = Depends(require_auth)):
    """Get all relation types"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        from models import RelationType
        
        relation_types = session.query(RelationType).all()
        
        types_list = []
        for rt in relation_types:
            types_list.append({
                "id": rt.id,
                "name": rt.name,
                "description": rt.description
            })
        
        session.close()
        
        return JSONResponse({
            "success": True,
            "relation_types": types_list
        })
        
    except Exception as e:
        print(f"Error fetching relation types: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error fetching relation types: {str(e)}"
        }, status_code=500)


# ========================================
# VIDEO RECORDING ENDPOINTS
# ========================================

@api_router.get("/videos/{video_id}")
def get_video_recording(video_id: int, authenticated: bool = Depends(require_auth)):
    """Get a specific video recording by ID"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        from models import VideoRecording, Guest
        
        # Get video recording with guest info
        recording = session.query(VideoRecording).filter_by(id=video_id, is_available=True).first()
        
        if not recording:
            session.close()
            return JSONResponse({
                "success": False,
                "message": "Video recording not found"
            }, status_code=404)
        
        # Get guest info if available
        guest_info = None
        if recording.guest_id:
            guest = session.query(Guest).filter_by(id=recording.guest_id).first()
            if guest:
                guest_info = {
                    "id": guest.id,
                    "full_name": guest.full_name,
                    "phone": guest.phone,
                    "seat_number": guest.seat_number,
                    "relation": guest.relation
                }
        
        session.close()
        
        result = recording.to_dict()
        if guest_info:
            result["guest_details"] = guest_info
        
        return JSONResponse({
            "success": True,
            "recording": result
        })
        
    except Exception as e:
        print(f"Error fetching video recording: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error fetching video recording: {str(e)}"
        }, status_code=500)


@api_router.post("/videos")
def create_video_recording(request: Request, authenticated: bool = Depends(require_auth)):
    """Create a new video recording record"""
    try:
        import json
        body = asyncio.run(request.body())
        data = json.loads(body.decode())
        
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        from datetime import datetime
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        from models import VideoRecording
        
        # Parse recording_started_at if provided
        recording_started_at = None
        if data.get("recording_started_at"):
            try:
                recording_started_at = datetime.fromisoformat(data["recording_started_at"].replace("Z", "+00:00"))
            except ValueError:
                recording_started_at = datetime.utcnow()
        
        # Create new video recording
        new_recording = VideoRecording(
            room_id=data.get("room_id", ""),
            video_url=data.get("video_url", ""),
            presigned_url=data.get("presigned_url"),
            egress_id=data.get("egress_id"),
            guest_id=data.get("guest_id"),
            guest_name=data.get("guest_name"),
            guest_phone=data.get("guest_phone"),
            guest_relation=data.get("guest_relation"),
            guest_table=data.get("guest_table"),
            recording_started_at=recording_started_at,
            recording_ended_at=None,  # Will be updated when recording ends
            duration_seconds=data.get("duration_seconds"),
            file_size_bytes=data.get("file_size_bytes"),
            processing_status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(new_recording)
        session.commit()
        
        recording_id = new_recording.id
        session.refresh(new_recording)
        session.close()
        
        return JSONResponse({
            "success": True,
            "message": "Video recording created successfully",
            "recording_id": recording_id
        })
        
    except Exception as e:
        print(f"Error creating video recording: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error creating video recording: {str(e)}"
        }, status_code=500)


@api_router.post("/videos/simple")
def create_simple_video_record():
    """Create a simple video record immediately when recording starts - no auth needed for agent"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        from datetime import datetime
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from models import VideoRecording
        
        # Generate filename for video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recordings/wedding_mirror_{timestamp}.mp4"
        
        # Generate S3 URL
        bucket_name = os.getenv("AWS_BUCKET_NAME", "4wk-garage-media")
        region = os.getenv("AWS_REGION", "me-central-1")
        s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{filename}"
        
        # Generate presigned URL for immediate access
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError
            
            region = os.getenv("AWS_REGION", "me-central-1")
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=region,
            )

            presigned_url = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": bucket_name,
                    "Key": filename,
                },
                ExpiresIn=86400 * 7,  # 7 days
            )
        except Exception as e:
            print(f"Could not generate presigned URL: {e}")
            presigned_url = None

        # Create simple video recording with just date and URL
        new_recording = VideoRecording(
            room_id="mirror-room",
            video_url=s3_url,
            presigned_url=presigned_url,
            recording_started_at=datetime.utcnow(),
            processing_status="recording",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(new_recording)
        session.commit()
        
        recording_id = new_recording.id
        session.refresh(new_recording)
        session.close()
        
        return JSONResponse({
            "success": True,
            "recording_id": recording_id,
            "video_url": s3_url,
            "filename": filename
        })
        
    except Exception as e:
        print(f"Error creating simple video record: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error creating simple video record: {str(e)}"
        }, status_code=500)


@api_router.get("/videos")
def list_video_recordings(authenticated: bool = Depends(require_auth)):
    """Get all video recordings"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from models import VideoRecording
        
        recordings = session.query(VideoRecording).order_by(VideoRecording.created_at.desc()).all()
        
        recordings_list = []
        for recording in recordings:
            recordings_list.append({
                "id": recording.id,
                "room_id": recording.room_id,
                "video_url": recording.video_url,
                "presigned_url": recording.presigned_url,
                "egress_id": recording.egress_id,
                "guest_name": recording.guest_name,
                "guest_id": recording.guest_id,
                "guest_phone": recording.guest_phone,
                "guest_relation": recording.guest_relation,
                "guest_table": recording.guest_table,
                "recording_started_at": recording.recording_started_at.isoformat() if recording.recording_started_at else None,
                "recording_ended_at": recording.recording_ended_at.isoformat() if recording.recording_ended_at else None,
                "file_size_bytes": recording.file_size_bytes,
                "duration_seconds": recording.duration_seconds,
                "status": recording.processing_status,
                "created_at": recording.created_at.isoformat() if recording.created_at else None,
                "updated_at": recording.updated_at.isoformat() if recording.updated_at else None
            })
        
        session.close()
        
        return JSONResponse({
            "success": True,
            "recordings": recordings_list,
            "total": len(recordings_list)
        })
        
    except Exception as e:
        print(f"Error fetching video recordings: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error fetching video recordings: {str(e)}"
        }, status_code=500)


@api_router.get("/videos/room/{room_id}")
def get_videos_by_room(room_id: str):
    """Get all video recordings for a specific room"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from models import VideoRecording
        
        recordings = session.query(VideoRecording).filter_by(room_id=room_id).order_by(VideoRecording.created_at.desc()).all()
        
        recordings_list = []
        for recording in recordings:
            recordings_list.append({
                "id": recording.id,
                "room_id": recording.room_id,
                "video_url": recording.video_url,
                "presigned_url": recording.presigned_url,
                "egress_id": recording.egress_id,
                "guest_name": recording.guest_name,
                "guest_id": recording.guest_id,
                "guest_phone": recording.guest_phone,
                "guest_relation": recording.guest_relation,
                "guest_table": recording.guest_table,
                "recording_started_at": recording.recording_started_at.isoformat() if recording.recording_started_at else None,
                "recording_ended_at": recording.recording_ended_at.isoformat() if recording.recording_ended_at else None,
                "file_size_bytes": recording.file_size_bytes,
                "duration_seconds": recording.duration_seconds,
                "status": recording.processing_status,
                "created_at": recording.created_at.isoformat() if recording.created_at else None,
                "updated_at": recording.updated_at.isoformat() if recording.updated_at else None
            })
        
        session.close()
        
        return JSONResponse({
            "success": True,
            "recordings": recordings_list,
            "total": len(recordings_list),
            "room_id": room_id
        })
        
    except Exception as e:
        print(f"Error fetching videos for room {room_id}: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error fetching videos for room {room_id}: {str(e)}"
        }, status_code=500)


@api_router.get("/videos/guest/{guest_name}")
def get_videos_by_guest(guest_name: str):
    """Get all video recordings for a specific guest"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from models import VideoRecording
        
        # Search by guest name (case insensitive)
        recordings = session.query(VideoRecording).filter(
            VideoRecording.guest_name.ilike(f"%{guest_name}%")
        ).order_by(VideoRecording.created_at.desc()).all()
        
        recordings_list = []
        for recording in recordings:
            recordings_list.append({
                "id": recording.id,
                "room_id": recording.room_id,
                "video_url": recording.video_url,
                "presigned_url": recording.presigned_url,
                "egress_id": recording.egress_id,
                "guest_name": recording.guest_name,
                "guest_id": recording.guest_id,
                "guest_phone": recording.guest_phone,
                "guest_relation": recording.guest_relation,
                "guest_table": recording.guest_table,
                "recording_started_at": recording.recording_started_at.isoformat() if recording.recording_started_at else None,
                "recording_ended_at": recording.recording_ended_at.isoformat() if recording.recording_ended_at else None,
                "file_size_bytes": recording.file_size_bytes,
                "duration_seconds": recording.duration_seconds,
                "status": recording.processing_status,
                "created_at": recording.created_at.isoformat() if recording.created_at else None,
                "updated_at": recording.updated_at.isoformat() if recording.updated_at else None
            })
        
        session.close()
        
        return JSONResponse({
            "success": True,
            "recordings": recordings_list,
            "total": len(recordings_list),
            "guest_name": guest_name
        })
        
    except Exception as e:
        print(f"Error fetching videos for guest {guest_name}: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error fetching videos for guest {guest_name}: {str(e)}"
        }, status_code=500)


@api_router.put("/videos/{recording_id}/complete")
def complete_video_recording(recording_id: int):
    """Mark video recording as completed when reset is called - no auth needed for agent"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        from datetime import datetime
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from models import VideoRecording
        
        recording = session.query(VideoRecording).filter_by(id=recording_id).first()
        if not recording:
            session.close()
            return JSONResponse({
                "success": False,
                "message": "Video recording not found"
            }, status_code=404)
        
        # Update recording as completed
        recording.recording_ended_at = datetime.utcnow()
        recording.processing_status = "completed"
        recording.updated_at = datetime.utcnow()
        
        session.commit()
        session.close()
        
        return JSONResponse({
            "success": True,
            "message": "Video recording marked as completed"
        })
        
    except Exception as e:
        print(f"Error completing video recording: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error completing video recording: {str(e)}"
        }, status_code=500)


@api_router.put("/videos/{recording_id}")
def update_video_recording(recording_id: int, request: Request, authenticated: bool = Depends(require_auth)):
    """Update an existing video recording"""
    try:
        import json
        body = asyncio.run(request.body())
        data = json.loads(body.decode())
        
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        from datetime import datetime
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from models import VideoRecording
        
        recording = session.query(VideoRecording).filter_by(id=recording_id).first()
        if not recording:
            session.close()
            return JSONResponse({
                "success": False,
                "message": "Video recording not found"
            }, status_code=404)
        
        # Update fields
        if "presigned_url" in data:
            recording.presigned_url = data["presigned_url"]
        if "recording_ended_at" in data:
            recording.recording_ended_at = datetime.fromisoformat(data["recording_ended_at"])
        if "file_size_bytes" in data:
            recording.file_size_bytes = data["file_size_bytes"]
        if "duration_seconds" in data:
            recording.duration_seconds = data["duration_seconds"]
        if "status" in data:
            recording.processing_status = data["status"]
        
        recording.updated_at = datetime.utcnow()
        
        session.commit()
        session.close()
        
        return JSONResponse({
            "success": True,
            "message": "Video recording updated successfully"
        })
        
    except Exception as e:
        print(f"Error updating video recording: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error updating video recording: {str(e)}"
        }, status_code=500)


@api_router.delete("/videos/{recording_id}")
def delete_video_recording(recording_id: int, authenticated: bool = Depends(require_auth)):
    """Delete a video recording"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from models import VideoRecording
        
        recording = session.query(VideoRecording).filter_by(id=recording_id).first()
        if not recording:
            session.close()
            return JSONResponse({
                "success": False,
                "message": "Video recording not found"
            }, status_code=404)
        
        session.delete(recording)
        session.commit()
        session.close()
        
        return JSONResponse({
            "success": True,
            "message": "Video recording deleted successfully"
        })
        
    except Exception as e:
        print(f"Error deleting video recording: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error deleting video recording: {str(e)}"
        }, status_code=500)


@api_router.post("/videos/{recording_id}/refresh")
def refresh_presigned_url(recording_id: int):
    """Refresh the presigned URL for a video recording"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        from datetime import datetime
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from models import VideoRecording
        
        recording = session.query(VideoRecording).filter_by(id=recording_id).first()
        if not recording:
            session.close()
            return JSONResponse({
                "success": False,
                "message": "Video recording not found"
            }, status_code=404)
        
        # Generate new presigned URL
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError
            
            # Extract S3 key from video URL
            if "amazonaws.com/" in recording.video_url:
                s3_key = recording.video_url.split("amazonaws.com/")[-1]
            else:
                session.close()
                return JSONResponse({
                    "success": False,
                    "message": "Invalid S3 URL format"
                }, status_code=400)
            
            region = os.getenv("AWS_REGION", "me-central-1")
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=region,
            )

            new_presigned_url = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": os.getenv("AWS_BUCKET_NAME", "4wk-garage-media"),
                    "Key": s3_key,
                },
                ExpiresIn=86400 * 7,  # 7 days
            )
            
            recording.presigned_url = new_presigned_url
            recording.updated_at = datetime.utcnow()
            session.commit()
            session.close()
            
            return JSONResponse({
                "success": True,
                "message": "Presigned URL refreshed successfully",
                "new_presigned_url": new_presigned_url
            })
            
        except Exception as e:
            session.close()
            return JSONResponse({
                "success": False,
                "message": f"Failed to generate presigned URL: {str(e)}"
            }, status_code=500)
        
    except Exception as e:
        print(f"Error refreshing presigned URL: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error refreshing presigned URL: {str(e)}"
        }, status_code=500)


# ========================================
# EXCEL IMPORT/EXPORT ENDPOINTS
# ========================================

@api_router.get("/guests/export")
def export_guests_excel(authenticated: bool = Depends(require_auth)):
    """Export all guests to Excel file"""
    try:
        import pandas as pd
        from io import BytesIO
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        from models import Guest, RelationType
        
        # Get all guests with relation types
        guests = session.query(Guest).join(RelationType, Guest.relation_type_id == RelationType.id, isouter=True).all()
        
        # Prepare data for Excel
        data = []
        for guest in guests:
            data.append({
                "ID": guest.id,
                "First Name": guest.first_name,
                "Last Name": guest.last_name,
                "Phone": guest.phone,
                "Seat Number": guest.seat_number,
                "Relation": guest.relation,
                "Relation Type": guest.relation_type.name if guest.relation_type else "",
                "Message": guest.message,
                "Story": guest.story,
                "About": guest.about,
                "Created": guest.created_at.strftime("%Y-%m-%d %H:%M") if guest.created_at else "",
                "Updated": guest.updated_at.strftime("%Y-%m-%d %H:%M") if guest.updated_at else ""
            })
        
        session.close()
        
        # Create Excel file
        df = pd.DataFrame(data)
        
        # Create BytesIO buffer
        excel_buffer = BytesIO()
        
        # Write to Excel with formatting
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Wedding Guests', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Wedding Guests']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        excel_buffer.seek(0)
        
        # Return as downloadable file
        from datetime import datetime
        filename = f"wedding_guests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            BytesIO(excel_buffer.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"Error exporting guests: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error exporting guests: {str(e)}"
        }, status_code=500)


@api_router.post("/guests/import")
def import_guests_excel(request: Request, authenticated: bool = Depends(require_auth)):
    """Import guests from Excel file"""
    try:
        import pandas as pd
        import base64
        from io import BytesIO
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        from datetime import datetime
        import json
        
        body = asyncio.run(request.body())
        data = json.loads(body.decode())
        
        # Get the base64 encoded file
        file_content = data.get("file_content")
        if not file_content:
            return JSONResponse({
                "success": False,
                "message": "No file content provided"
            }, status_code=400)
        
        # Decode base64 file content
        file_bytes = base64.b64decode(file_content.split(',')[1])  # Remove data:application/... prefix
        excel_buffer = BytesIO(file_bytes)
        
        # Read Excel file
        df = pd.read_excel(excel_buffer)
        
        # Database connection
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        from models import Guest, RelationType
        
        # Get existing relation types for mapping
        relation_types = {rt.name: rt.id for rt in session.query(RelationType).all()}
        
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Map relation type name to ID
                relation_type_id = None
                if pd.notna(row.get("Relation Type", "")):
                    relation_type_id = relation_types.get(str(row["Relation Type"]))
                
                # Create new guest
                new_guest = Guest(
                    first_name=str(row.get("First Name", "")).strip(),
                    last_name=str(row.get("Last Name", "")).strip(),
                    phone=str(row.get("Phone", "")).strip() if pd.notna(row.get("Phone")) else None,
                    seat_number=str(row.get("Seat Number", "")).strip() if pd.notna(row.get("Seat Number")) else None,
                    relation=str(row.get("Relation", "")).strip() if pd.notna(row.get("Relation")) else None,
                    relation_type_id=relation_type_id,
                    message=str(row.get("Message", "")).strip() if pd.notna(row.get("Message")) else None,
                    story=str(row.get("Story", "")).strip() if pd.notna(row.get("Story")) else None,
                    about=str(row.get("About", "")).strip() if pd.notna(row.get("About")) else None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                session.add(new_guest)
                imported_count += 1
                
            except Exception as row_error:
                errors.append(f"Row {index + 2}: {str(row_error)}")
        
        if imported_count > 0:
            session.commit()
        
        session.close()
        
        return JSONResponse({
            "success": True,
            "message": f"Successfully imported {imported_count} guests",
            "imported_count": imported_count,
            "errors": errors
        })
        
    except Exception as e:
        print(f"Error importing guests: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error importing guests: {str(e)}"
        }, status_code=500)
