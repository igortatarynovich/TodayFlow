"""Challenges/Marathons API endpoints."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from todayflow_backend.db.session import get_session
from todayflow_backend.db.models import Challenge, ChallengeParticipant, ChallengeDayTask, ChallengeTaskCompletion, User
from todayflow_backend.api.auth import require_user, get_optional_user

router = APIRouter(prefix="/challenges", tags=["challenges"])


class ChallengeResponse(BaseModel):
    id: str
    title: str
    description: str
    duration: int
    goal: str
    challenge_type: Optional[str] = "goal"  # "tracker", "ascetic", "goal", "habit"
    price: Optional[int]  # in cents
    is_pro_only: bool
    icon: Optional[str]
    color: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class ChallengeParticipantResponse(BaseModel):
    id: int
    challenge_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    current_day: int
    is_active: bool
    challenge: Optional[ChallengeResponse] = None  # Включаем объект challenge
    current_streak_days: Optional[int] = None  # Текущая серия дней подряд
    longest_streak_days: Optional[int] = None  # Самая длинная серия дней подряд

    class Config:
        from_attributes = True


class ChallengeParticipantCreate(BaseModel):
    challenge_id: str


class UserChallengeCreate(BaseModel):
    title: str
    description: str
    duration: int = 21  # default 21 days
    goal: Optional[str] = None
    challenge_type: str = "goal"  # "tracker", "ascetic", "goal", "habit"
    icon: Optional[str] = None
    color: Optional[str] = None


@router.post("", response_model=ChallengeParticipantResponse, status_code=status.HTTP_201_CREATED)
def create_user_challenge(
    challenge_data: UserChallengeCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Create a user-defined challenge (goal or ascetic) and automatically join it."""
    import uuid
    from datetime import datetime
    
    # Generate unique challenge ID for user-created challenges
    challenge_id = f"user-{current_user.id}-{uuid.uuid4().hex[:8]}"
    
    # Create the challenge
    challenge = Challenge(
        id=challenge_id,
        title=challenge_data.title,
        description=challenge_data.description,
        duration=challenge_data.duration,
        goal=challenge_data.goal or "",  # Empty string if None (for asceses)
        challenge_type=challenge_data.challenge_type,
        price=None,  # User-created challenges are always free
        is_pro_only=False,
        icon=challenge_data.icon,
        color=challenge_data.color,
        is_active=True,
    )
    
    db.add(challenge)
    db.flush()  # Get the challenge ID
    
    # Automatically join the challenge
    participant = ChallengeParticipant(
        user_id=current_user.id,
        challenge_id=challenge_id,
        current_day=1,
        is_active=True,
    )
    
    db.add(participant)
    db.commit()
    db.refresh(participant)
    db.refresh(challenge)
    
    # Return participant with challenge data
    challenge_response = ChallengeResponse(
        id=challenge.id,
        title=challenge.title,
        description=challenge.description,
        duration=challenge.duration,
        goal=challenge.goal,
        challenge_type=challenge.challenge_type or "goal",
        price=challenge.price,
        is_pro_only=challenge.is_pro_only,
        icon=challenge.icon,
        color=challenge.color,
        is_active=challenge.is_active,
    )
    
    return ChallengeParticipantResponse(
        id=participant.id,
        challenge_id=participant.challenge_id,
        started_at=participant.started_at,
        completed_at=participant.completed_at,
        current_day=participant.current_day,
        is_active=participant.is_active,
        challenge=challenge_response,
        current_streak_days=None,
        longest_streak_days=None,
    )


@router.get("", response_model=List[ChallengeResponse])
def get_challenges(
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_session),
):
    """Get all active challenges."""
    challenges = db.query(Challenge).filter(Challenge.is_active == True).all()
    
    # Filter out Pro-only challenges if user is not Pro
    if current_user and isinstance(current_user, User):
        # Check subscription status from database
        from todayflow_backend.db.models import Subscription
        active_subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.status == "active"
        ).first()
        is_pro = current_user.is_paid or (active_subscription is not None)
        if not is_pro:
            challenges = [c for c in challenges if not c.is_pro_only]
    
    return challenges


@router.get("/{challenge_id}", response_model=ChallengeResponse)
def get_challenge(
    challenge_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_session),
):
    """Get a specific challenge by ID."""
    challenge = db.query(Challenge).filter(
        Challenge.id == challenge_id,
        Challenge.is_active == True
    ).first()
    
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    # Check if Pro-only and user doesn't have Pro
    if challenge.is_pro_only and current_user:
        is_pro = current_user.is_paid or current_user.subscription_status == "active"
        if not is_pro:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This challenge requires Pro subscription"
            )
    
    return challenge


@router.post("/{challenge_id}/join", response_model=ChallengeParticipantResponse, status_code=status.HTTP_201_CREATED)
def join_challenge(
    challenge_id: str,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Join a challenge."""
    challenge = db.query(Challenge).filter(
        Challenge.id == challenge_id,
        Challenge.is_active == True
    ).first()
    
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    # Check if Pro-only and user doesn't have Pro
    if challenge.is_pro_only:
        is_pro = current_user.is_paid or current_user.subscription_status == "active"
        if not is_pro:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This challenge requires Pro subscription"
            )
    
    # Check if user already joined
    existing = db.query(ChallengeParticipant).filter(
        ChallengeParticipant.user_id == current_user.id,
        ChallengeParticipant.challenge_id == challenge_id
    ).first()
    
    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already participating in this challenge"
            )
        else:
            # Reactivate participation
            existing.is_active = True
            existing.current_day = 1
            existing.started_at = datetime.utcnow()
            existing.completed_at = None
            db.commit()
            db.refresh(existing)
            return existing
    
    # Create new participation
    participant = ChallengeParticipant(
        user_id=current_user.id,
        challenge_id=challenge_id,
        current_day=1,
        is_active=True
    )
    
    db.add(participant)
    db.commit()
    db.refresh(participant)
    
    return participant


@router.get("/my/participations", response_model=List[ChallengeParticipantResponse])
def get_my_participations(
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Get all challenges the current user is participating in."""
    from datetime import date, timedelta
    
    participations = db.query(ChallengeParticipant).filter(
        ChallengeParticipant.user_id == current_user.id,
        ChallengeParticipant.is_active == True
    ).all()
    
    result = []
    for participation in participations:
        # Загружаем challenge
        challenge = db.query(Challenge).filter(Challenge.id == participation.challenge_id).first()
        
        # Вычисляем streak дни на основе task completions
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        # Получаем все завершенные задачи для этого участия
        completions = db.query(ChallengeTaskCompletion).join(
            ChallengeDayTask
        ).filter(
            ChallengeTaskCompletion.participant_id == participation.id
        ).order_by(ChallengeTaskCompletion.completed_at.desc()).all()
        
        if completions:
            # Группируем по дням
            days_completed = set()
            for completion in completions:
                task = db.query(ChallengeDayTask).filter(ChallengeDayTask.id == completion.task_id).first()
                if task:
                    days_completed.add(task.day_number)
            
            # Вычисляем текущую серию (последние дни подряд)
            today = date.today()
            for i in range(participation.current_day, 0, -1):
                if i in days_completed:
                    current_streak += 1
                else:
                    break
            
            # Вычисляем самую длинную серию
            sorted_days = sorted(days_completed)
            for day in sorted_days:
                if day == sorted_days[0] or day == sorted_days[sorted_days.index(day) - 1] + 1:
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 1
        
        challenge_data = None
        if challenge:
            challenge_data = ChallengeResponse(
                id=challenge.id,
                title=challenge.title,
                description=challenge.description,
                duration=challenge.duration,
                goal=challenge.goal,
                price=challenge.price,
                is_pro_only=challenge.is_pro_only,
                icon=challenge.icon,
                color=challenge.color,
                is_active=challenge.is_active,
            )
        
        result.append(ChallengeParticipantResponse(
            id=participation.id,
            challenge_id=participation.challenge_id,
            started_at=participation.started_at,
            completed_at=participation.completed_at,
            current_day=participation.current_day,
            is_active=participation.is_active,
            challenge=challenge_data,
            current_streak_days=current_streak if current_streak > 0 else None,
            longest_streak_days=longest_streak if longest_streak > 0 else None,
        ))
    
    return result


@router.post("/{challenge_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_challenge(
    challenge_id: str,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Leave a challenge (deactivate participation)."""
    participant = db.query(ChallengeParticipant).filter(
        ChallengeParticipant.user_id == current_user.id,
        ChallengeParticipant.challenge_id == challenge_id,
        ChallengeParticipant.is_active == True
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participation not found"
        )
    
    participant.is_active = False
    db.commit()
    
    return None


class ChallengeDayTaskResponse(BaseModel):
    id: int
    challenge_id: str
    day_number: int
    title: str
    description: str
    task_type: str
    order: int

    class Config:
        from_attributes = True


class ChallengeTaskCompletionResponse(BaseModel):
    id: int
    task_id: int
    completed_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/{challenge_id}/tasks", response_model=List[ChallengeDayTaskResponse])
def get_challenge_tasks(
    challenge_id: str,
    day_number: Optional[int] = None,
    db: Session = Depends(get_session),
):
    """Get tasks for a challenge, optionally filtered by day."""
    # Verify challenge exists
    challenge = db.query(Challenge).filter(
        Challenge.id == challenge_id,
        Challenge.is_active == True
    ).first()
    
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    query = db.query(ChallengeDayTask).filter(ChallengeDayTask.challenge_id == challenge_id)
    
    if day_number is not None:
        query = query.filter(ChallengeDayTask.day_number == day_number)
    
    tasks = query.order_by(ChallengeDayTask.day_number, ChallengeDayTask.order).all()
    return tasks


@router.get("/{challenge_id}/tasks/{day_number}", response_model=List[ChallengeDayTaskResponse])
def get_challenge_tasks_by_day(
    challenge_id: str,
    day_number: int,
    db: Session = Depends(get_session),
):
    """Get tasks for a specific day of a challenge."""
    return get_challenge_tasks(challenge_id, day_number, db)


@router.get("/my/participations/{participation_id}/tasks", response_model=List[dict])
def get_my_participation_tasks(
    participation_id: int,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Get tasks for user's participation with completion status."""
    participation = db.query(ChallengeParticipant).filter(
        ChallengeParticipant.id == participation_id,
        ChallengeParticipant.user_id == current_user.id,
        ChallengeParticipant.is_active == True
    ).first()
    
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participation not found"
        )
    
    # Get all tasks for current day
    tasks = db.query(ChallengeDayTask).filter(
        ChallengeDayTask.challenge_id == participation.challenge_id,
        ChallengeDayTask.day_number == participation.current_day
    ).order_by(ChallengeDayTask.order).all()
    
    # Get completion status
    completed_task_ids = {
        c.task_id for c in db.query(ChallengeTaskCompletion.task_id).filter(
            ChallengeTaskCompletion.participant_id == participation_id
        ).all()
    }
    
    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "challenge_id": task.challenge_id,
            "day_number": task.day_number,
            "title": task.title,
            "description": task.description,
            "task_type": task.task_type,
            "order": task.order,
            "is_completed": task.id in completed_task_ids,
        })
    
    return result


@router.post("/tasks/{task_id}/complete", response_model=ChallengeTaskCompletionResponse, status_code=status.HTTP_201_CREATED)
def complete_task(
    task_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_session),
):
    """Mark a task as completed."""
    # Get task
    task = db.query(ChallengeDayTask).filter(ChallengeDayTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Get user's active participation
    participation = db.query(ChallengeParticipant).filter(
        ChallengeParticipant.user_id == current_user.id,
        ChallengeParticipant.challenge_id == task.challenge_id,
        ChallengeParticipant.is_active == True
    ).first()
    
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not participating in this challenge"
        )
    
    # Check if already completed
    existing = db.query(ChallengeTaskCompletion).filter(
        ChallengeTaskCompletion.participant_id == participation.id,
        ChallengeTaskCompletion.task_id == task_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already completed"
        )
    
    # Create completion
    completion = ChallengeTaskCompletion(
        participant_id=participation.id,
        task_id=task_id,
        notes=notes,
    )
    db.add(completion)
    db.commit()
    db.refresh(completion)
    
    return completion

