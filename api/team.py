"""Team API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
import datetime

from database import get_db
from models.user import User
from models.opportunity import Opportunity
from models.team import Team, TeamMember, TeamRequest
from api.auth import get_current_user
from services.matchmaker_service import TeamMatchmakerService


router = APIRouter(prefix="/api/teams", tags=["teams"])


# Pydantic Schemas
class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    needed_skills: Optional[str] = None
    max_members: Optional[int] = 4


class TeamResponse(BaseModel):
    id: int
    opportunity_id: int
    leader_id: str
    name: str
    description: Optional[str]
    needed_skills: Optional[str]
    max_members: int
    is_active: bool
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: str
    role: str
    joined_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class TeamRequestCreate(BaseModel):
    message: Optional[str] = None


class TeamRequestResponse(BaseModel):
    id: int
    team_id: int
    user_id: str
    message: Optional[str]
    status: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


@router.post("/opportunity/{opportunity_id}", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    opportunity_id: int,
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new team for an opportunity."""
    # Check if opportunity exists and is a hackathon
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    if opp.type != "hackathon":
        raise HTTPException(status_code=400, detail="Teams can only be formed for hackathons")

    # Check if user already has a team for this opportunity
    existing_team = db.query(Team).filter(
        Team.opportunity_id == opportunity_id,
        Team.leader_id == current_user.id
    ).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="You already lead a team for this opportunity")

    # Create team
    new_team = Team(
        opportunity_id=opportunity_id,
        leader_id=current_user.id,
        name=team_data.name,
        description=team_data.description,
        needed_skills=team_data.needed_skills,
        max_members=team_data.max_members
    )
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    # Add leader to team members
    member = TeamMember(
        team_id=new_team.id,
        user_id=current_user.id,
        role="leader"
    )
    db.add(member)
    db.commit()

    return new_team


@router.get("/opportunity/{opportunity_id}", response_model=List[TeamResponse])
async def get_teams_for_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db)
):
    """Get all active teams for an opportunity."""
    teams = db.query(Team).filter(
        Team.opportunity_id == opportunity_id,
        Team.is_active == True
    ).all()
    return teams


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: Session = Depends(get_db)
):
    """Get details of a specific team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("/{team_id}/join", response_model=TeamRequestResponse)
async def request_to_join_team(
    team_id: int,
    request_data: TeamRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a request to join a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    if not team.is_active:
        raise HTTPException(status_code=400, detail="Team is no longer active")

    # Check if user is already a member
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="You are already a member of this team")

    # Check if request already exists
    existing_request = db.query(TeamRequest).filter(
        TeamRequest.team_id == team_id,
        TeamRequest.user_id == current_user.id,
        TeamRequest.status == "pending"
    ).first()
    if existing_request:
        raise HTTPException(status_code=400, detail="You already have a pending request for this team")

    # Check capacity
    member_count = db.query(TeamMember).filter(TeamMember.team_id == team_id).count()
    if member_count >= team.max_members:
        raise HTTPException(status_code=400, detail="Team has reached its maximum capacity")

    # Create request
    new_request = TeamRequest(
        team_id=team_id,
        user_id=current_user.id,
        message=request_data.message
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


@router.get("/{team_id}/requests", response_model=List[TeamRequestResponse])
async def get_team_requests(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all join requests for a team (Leader only)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    if team.leader_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the team leader can view requests")

    requests = db.query(TeamRequest).filter(
        TeamRequest.team_id == team_id,
        TeamRequest.status == "pending"
    ).all()
    
    return requests


@router.put("/requests/{request_id}/{action}", response_model=TeamRequestResponse)
async def process_team_request(
    request_id: int,
    action: str,  # "accept" or "reject"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept or reject a team join request (Leader only)."""
    if action not in ["accept", "reject"]:
        raise HTTPException(status_code=400, detail="Action must be 'accept' or 'reject'")

    join_request = db.query(TeamRequest).filter(TeamRequest.id == request_id).first()
    if not join_request:
        raise HTTPException(status_code=404, detail="Request not found")

    team = db.query(Team).filter(Team.id == join_request.team_id).first()
    if not team or team.leader_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the team leader can process requests")

    if join_request.status != "pending":
        raise HTTPException(status_code=400, detail="Request has already been processed")

    # Process
    if action == "accept":
        # Check team capacity again
        member_count = db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
        if member_count >= team.max_members:
            join_request.status = "rejected"
            db.commit()
            raise HTTPException(status_code=400, detail="Team has reached its maximum capacity. Request rejected automatically.")
            
        join_request.status = "accepted"
        
        # Add to team members
        member = TeamMember(
            team_id=team.id,
            user_id=join_request.user_id,
            role="member"
        )
        db.add(member)
        
        # If team is now full, mark it
        if member_count + 1 >= team.max_members:
            team.is_active = False

    elif action == "reject":
        join_request.status = "rejected"

    db.commit()
    db.refresh(join_request)
    return join_request


@router.get("/{team_id}/recommend-members")
async def recommend_members_for_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Find solo users who fill the team's skill gap."""
    matchmaker = TeamMatchmakerService(db)
    return matchmaker.recommend_members_for_team(team_id)


@router.get("/recommended/for-me")
async def recommend_teams_for_user(
    opportunity_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Find teams that need your skills."""
    matchmaker = TeamMatchmakerService(db)
    return matchmaker.recommend_teams_for_user(current_user.id, opportunity_id)
