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
            secure=True,  # Required for HTTPS (production)
            samesite="none",  # Allow cross-origin cookies
            domain=".raheva.com"  # Share cookie across subdomains
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
    response.delete_cookie(
        key="mirror_auth",
        secure=True,
        samesite="none",
        domain=".raheva.com"
    )
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
                        SELECT id, first_name, last_name, phone, seat_number, relation, message, story, about
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
                        SELECT id, first_name, last_name, phone, seat_number, relation, message, story, about
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
                            SELECT id, first_name, last_name, phone, seat_number, relation, message, story, about
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
                    SELECT id, first_name, last_name, phone, seat_number, relation, message, story, about
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
                    "id": result[0],
                    "name": f"{result[1]} {result[2]}" if result[1] and result[2] else guest_name,
                    "first_name": result[1],
                    "last_name": result[2],
                    "phone": result[3],
                    "table_number": result[4],
                    "relationship": result[5],
                    "message": result[6],
                    "story": result[7],
                    "about": result[8]
                }
                
                print("🎉 GUEST FOUND!")
                print(f"🆔 ID: {guest_info['id']}")
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
        
        # Get all non-deleted guests with their relation types
        guests = session.query(Guest).filter(
            Guest.deleted_at.is_(None)
        ).join(RelationType, Guest.relation_type_id == RelationType.id, isouter=True).all()
        
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
        
        # Basic validation
        if 'first_name' in data and not data['first_name'].strip():
            return JSONResponse({
                "success": False,
                "message": "First name cannot be empty"
            }, status_code=400)
            
        if 'last_name' in data and not data['last_name'].strip():
            return JSONResponse({
                "success": False,
                "message": "Last name cannot be empty"
            }, status_code=400)
        
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
        
        # Update guest fields with stripped values
        if 'first_name' in data:
            guest.first_name = data['first_name'].strip()
        if 'last_name' in data:
            guest.last_name = data['last_name'].strip()
        if 'phone' in data:
            guest.phone = data['phone']
        if 'seat_number' in data:
            guest.seat_number = data['seat_number']
        if 'relation' in data:
            guest.relation = data['relation']
        if 'relation_type_id' in data:
            guest.relation_type_id = data['relation_type_id']
        if 'message' in data:
            guest.message = data['message']
        if 'story' in data:
            guest.story = data['story']
        if 'about' in data:
            guest.about = data['about']
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
        from datetime import datetime
        
        # Find and soft delete the guest
        guest = session.query(Guest).filter_by(id=guest_id).first()
        if not guest:
            session.close()
            return JSONResponse({
                "success": False,
                "message": "Guest not found"
            }, status_code=404)
        
        # Soft delete by setting deleted_at timestamp
        guest.deleted_at = datetime.utcnow()
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
        
        # Get all non-deleted guests with relation types
        guests = session.query(Guest).filter(
            Guest.deleted_at.is_(None)
        ).join(RelationType, Guest.relation_type_id == RelationType.id, isouter=True).all()
        
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
        updated_count = 0
        skipped_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Extract and clean data
                first_name = str(row.get("First Name", "")).strip()
                last_name = str(row.get("Last Name", "")).strip()
                phone = str(row.get("Phone", "")).strip() if pd.notna(row.get("Phone")) else None
                
                # Skip if no name
                if not first_name or not last_name:
                    errors.append(f"Row {index + 2}: Missing required fields (first name or last name)")
                    continue
                
                # Check for duplicates
                existing_guest = None
                
                # Strategy 1: Check by phone if provided
                if phone and phone != "":
                    existing_guest = session.query(Guest).filter(
                        Guest.phone == phone,
                        Guest.deleted_at.is_(None)
                    ).first()
                
                # Strategy 2: Check by full name if no phone match
                if not existing_guest:
                    existing_guest = session.query(Guest).filter(
                        Guest.first_name.ilike(first_name),
                        Guest.last_name.ilike(last_name),
                        Guest.deleted_at.is_(None)
                    ).first()
                
                # Map relation type name to ID
                relation_type_id = None
                if pd.notna(row.get("Relation Type", "")):
                    relation_type_id = relation_types.get(str(row["Relation Type"]))
                
                # If duplicate found, update instead of insert
                if existing_guest:
                    # Update existing guest
                    existing_guest.phone = phone or existing_guest.phone
                    existing_guest.seat_number = str(row.get("Seat Number", "")).strip() if pd.notna(row.get("Seat Number")) else existing_guest.seat_number
                    existing_guest.relation = str(row.get("Relation", "")).strip() if pd.notna(row.get("Relation")) else existing_guest.relation
                    existing_guest.relation_type_id = relation_type_id or existing_guest.relation_type_id
                    existing_guest.message = str(row.get("Message", "")).strip() if pd.notna(row.get("Message")) else existing_guest.message
                    existing_guest.story = str(row.get("Story", "")).strip() if pd.notna(row.get("Story")) else existing_guest.story
                    existing_guest.about = str(row.get("About", "")).strip() if pd.notna(row.get("About")) else existing_guest.about
                    existing_guest.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new guest
                    new_guest = Guest(
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone,
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
        
        if imported_count > 0 or updated_count > 0:
            session.commit()
        
        session.close()
        
        # Build message
        message_parts = []
        if imported_count > 0:
            message_parts.append(f"imported {imported_count} new guests")
        if updated_count > 0:
            message_parts.append(f"updated {updated_count} existing guests")
        if skipped_count > 0:
            message_parts.append(f"skipped {skipped_count} duplicates")
            
        message = "Successfully " + ", ".join(message_parts) if message_parts else "No changes made"
        
        return JSONResponse({
            "success": True,
            "message": message,
            "imported_count": imported_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "errors": errors
        })
        
    except Exception as e:
        print(f"Error importing guests: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error importing guests: {str(e)}"
        }, status_code=500)
