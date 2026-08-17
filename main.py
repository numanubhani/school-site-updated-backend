from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta
from pathlib import Path
import uuid, string, random, shutil

from database import engine, Base, get_db
import models, schemas, auth

models.Base.metadata.create_all(bind=engine)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

_PLATFORM_COURSES_SEED = [
    {
        "course": {"title": "Identifying Emotions", "domain": "Self-Awareness", "description": "Learn to recognize, name, and understand your own emotions and how they shape your thoughts and actions. This module builds the foundation for all social-emotional learning.", "duration": "15 min", "icon_name": "smile", "order": 1},
        "lessons": [
            {"title": "What Are Emotions?", "duration": "3 min", "order": 1, "content": "Emotions are signals from our brain that give us important information about our experiences. Psychologist Paul Ekman identified 6 universal primary emotions: happiness, sadness, fear, anger, disgust, and surprise. These blend into hundreds of secondary emotions — for example, anger + disgust = contempt; joy + anticipation = optimism. The Emotion Wheel, developed by Robert Plutchik, maps how emotions relate and intensify. Recognizing and naming your emotions is the very first step toward emotional intelligence. Studies show that people who can accurately label their emotions make better decisions and have healthier relationships."},
            {"title": "Reading Your Body", "duration": "4 min", "order": 2, "content": "Every emotion creates distinct physical sensations in the body — a phenomenon called somatic awareness. Anger often feels like heat in the face, a tight chest, or clenched fists. Excitement and anxiety share a similar physical signature: racing heart and rapid breathing, which is why they're so easy to confuse. Sadness can feel like heaviness in the chest or a lump in the throat. Fear triggers the fight-or-flight response: adrenaline surges, muscles tense, and digestion slows. By learning to read these physical signals BEFORE your thinking mind processes them, you can catch emotions early and choose your response rather than reacting automatically."},
            {"title": "The Emotion–Thought Connection", "duration": "4 min", "order": 3, "content": "Emotions and thoughts exist in a constant two-way relationship called the cognitive-emotional cycle. An emotion can trigger a thought (feeling anxious → 'I'm going to fail'), and a thought can trigger an emotion (thinking about an argument → feeling angry again). Cognitive psychologist Aaron Beck discovered that distorted thinking patterns — called cognitive distortions — amplify negative emotions. Examples: catastrophizing ('this is the worst thing ever'), all-or-nothing thinking ('I always mess up'), and mind-reading ('they must hate me'). Recognizing this cycle gives you a point of intervention: you can challenge the thought, which changes the emotion — or regulate the emotion, which clears your thinking."},
            {"title": "Building Your Emotion Vocabulary", "duration": "4 min", "order": 4, "content": "Research by psychologist Lisa Feldman Barrett introduces the concept of 'emotional granularity' — the ability to distinguish subtle differences between emotions. People with high emotional granularity don't just feel 'bad'; they can pinpoint whether they feel disappointed, embarrassed, defeated, melancholic, or grief-stricken. Barrett's research shows that greater emotional granularity leads to less intense negative emotional experiences, better impulse control, and faster emotional recovery. Practice: instead of 'I'm stressed,' ask yourself: Am I overwhelmed? Frustrated? Apprehensive? Pressured? Each word points to a different cause and a different solution. Your emotional vocabulary is a skill you can build every day."},
        ],
    },
    {
        "course": {"title": "Stress Management 101", "domain": "Self-Management", "description": "Discover practical, research-backed strategies to manage stress, regulate emotions, and build the resilience needed to navigate daily challenges with confidence.", "duration": "20 min", "icon_name": "zap", "order": 2},
        "lessons": [
            {"title": "Understanding Stress", "duration": "5 min", "order": 1, "content": "Stress is your body's natural response to any perceived demand or threat — real or imagined. When your brain detects a stressor, the hypothalamus triggers the release of cortisol and adrenaline, activating the fight-or-flight response: heart rate increases, breathing quickens, muscles tense, digestion slows. In short bursts, this is adaptive — it sharpens focus and boosts performance (called 'eustress'). But chronic stress keeps cortisol elevated, which damages the immune system, disrupts sleep, impairs memory, and increases risk of anxiety and depression. The key insight: stress itself isn't always the problem. Your perception of the stressor and your capacity to respond to it are what matter most."},
            {"title": "Your Personal Stress Triggers", "duration": "5 min", "order": 2, "content": "Stress triggers are highly individual. Common categories include: Academic pressure (exams, deadlines, performance expectations), Social stress (conflict, exclusion, peer pressure, rejection), Environmental stress (noise, clutter, overcrowding, commuting), Life transitions (moving, changing schools, family changes), and Internal pressure (perfectionism, self-criticism, imposter syndrome, fear of failure). This week, keep a 'Stress Log': every time you notice stress symptoms, write down: (1) the trigger, (2) your physical reaction, (3) your emotional response, (4) what you did. After 5-7 entries, look for patterns. Awareness of your unique triggers is the foundation of an effective management strategy."},
            {"title": "The Toolbox: 5 Evidence-Based Techniques", "duration": "6 min", "order": 3, "content": "Technique 1 — Box Breathing: Inhale for 4 counts, hold for 4, exhale for 4, hold for 4. Repeat 4 times. This activates the parasympathetic nervous system (your 'rest and digest' mode), directly countering the stress response. Used by Navy SEALs and surgeons. Technique 2 — Progressive Muscle Relaxation (PMR): Starting from your toes, tense each muscle group tightly for 5 seconds, then release. Work up to your forehead. This breaks the physical stress cycle. Technique 3 — 5-4-3-2-1 Grounding: Name 5 things you can see, 4 you can physically feel, 3 you can hear, 2 you can smell, 1 you can taste. Immediately brings you back to the present moment. Technique 4 — Movement: Just 10 minutes of moderate physical activity lowers cortisol and releases endorphins. A brisk walk is enough. Technique 5 — Expressive Journaling: Write about the stressor for 15 minutes without editing. Research by James Pennebaker shows this reduces the emotional intensity of stressors and improves immune function."},
            {"title": "Building Your Personal Stress Plan", "duration": "4 min", "order": 4, "content": "An effective stress management plan is proactive, personal, and practiced before you need it. Your plan has four components: (1) Trigger Awareness — list your top 3 personal stress triggers from your Stress Log. (2) Your Technique Toolkit — choose 2-3 techniques you've tested and that work for YOU. Not every technique works for every person. (3) Daily Self-Care Foundations — consistent sleep (7-9 hours), regular movement, social connection, and nutrition regulate your stress baseline. These aren't optional extras; they're infrastructure. (4) Your Stress Emergency Kit — for peak-stress moments: a written list of 3 actions you'll take immediately (e.g., 'step outside for 2 minutes, box breathe, text a friend'). Review and update your plan monthly, or after any major stressful event."},
        ],
    },
    {
        "course": {"title": "The Empathy Project", "domain": "Social Awareness", "description": "Develop the ability to understand and share the feelings of others. This module fosters compassion, perspective-taking, and the skills to build inclusive, caring communities.", "duration": "25 min", "icon_name": "users", "order": 3},
        "lessons": [
            {"title": "Empathy vs Sympathy", "duration": "6 min", "order": 1, "content": "Sympathy means feeling FOR someone from a distance — 'I feel sorry for you.' It often involves pity and can subtly reinforce a power imbalance. Empathy means feeling WITH someone — stepping into their emotional world without judgment. Dr. Brené Brown explains: 'Empathy fuels connection; sympathy drives disconnection.' Empathy requires four skills: (1) Perspective-taking — choosing to see the world through their eyes. (2) Staying out of judgment — suspending your evaluations. (3) Recognizing the emotion — identifying what they're feeling. (4) Communicating your understanding — 'I hear that this is really hard.' The classic sympathy response starts with 'At least...' (at least you have your health, at least it wasn't worse). Empathy rarely starts with 'at least' — it starts with 'Tell me more.'"},
            {"title": "Walking in Their Shoes", "duration": "7 min", "order": 2, "content": "Perspective-taking is the cognitive ability to mentally simulate another person's point of view. It is different from projection (assuming they feel what YOU would feel in their situation). True perspective-taking requires: (1) Pausing your own perspective — temporarily setting aside your feelings and opinions. (2) Gathering context — what is their background, history, culture, and current circumstances? (3) Asking yourself: 'What might they be experiencing, and why might they feel that way?' (4) Checking your understanding — asking open questions like 'How has this been for you?' rather than 'You must be feeling...' Psychologist Nicholas Epley's research shows that we are systematically poor at perspective-taking when we rely on assumption alone. Curiosity — genuine interest in the other person's experience — is the antidote."},
            {"title": "Barriers to Empathy", "duration": "6 min", "order": 3, "content": "Understanding the barriers to empathy helps you overcome them: (1) Unconscious bias — our brains use mental shortcuts that lead us to empathize more easily with people who are similar to us. Recognizing this bias is the first step to expanding our empathy. (2) Emotional overwhelm — when we're flooded with our own stress and emotions, we have little capacity to hold space for others. Self-care isn't selfish; it's what makes empathy sustainable. (3) Empathy fatigue — experienced by caregivers, teachers, and helpers who give so much emotional energy that their reserves deplete. Healthy boundaries are essential. (4) 'Othering' — perceiving someone as fundamentally different from you reduces the instinctive empathic response. Seeking commonality is the antidote. (5) Power dynamics — research shows empathy flows less freely upward (toward people with more power). Being in a position of authority requires intentional empathic practice."},
            {"title": "Empathic Communication", "duration": "6 min", "order": 4, "content": "Empathic communication transforms relationships. It has four elements: (1) Active Presence — put down your phone, face the person, make natural eye contact. Your body communicates before your words do. (2) Reflective Listening — mirror back what you heard: 'It sounds like you're feeling overwhelmed by everything happening at once.' This shows you're engaged AND gives them a chance to correct your understanding. (3) Validation — confirm that their feelings make sense: 'That makes complete sense given what you've been through.' Validation is NOT the same as agreement. You can validate an emotion without agreeing with the behavior. (4) Curious Questions — ask open questions that invite sharing: 'What's been the hardest part for you?' Avoid: 'Have you tried...?', 'Why didn't you just...?', or 'I know exactly how you feel' — each one shifts focus from them to you."},
        ],
    },
    {
        "course": {"title": "Healthy Boundaries", "domain": "Relationship Skills", "description": "Learn how to set, communicate, and respect personal boundaries in every relationship. Build trust, mutual respect, and healthier connections with others.", "duration": "18 min", "icon_name": "handshake", "order": 4},
        "lessons": [
            {"title": "What Are Boundaries?", "duration": "4 min", "order": 1, "content": "Boundaries are the personal limits we set in relationships to protect our physical, emotional, and mental well-being. Think of boundaries not as walls, but as fences with gates — you decide who enters, when, and how far. Types of boundaries: Physical — personal space, touch, and privacy. Emotional — what feelings you share, with whom, and when. Time — how you allocate your time and energy. Digital — your privacy online, response time expectations, and screen habits. Material — whether and how you share your possessions. Intellectual — your right to your own beliefs and opinions. Healthy boundaries are not about controlling others — they are about honoring your own needs. People with healthy boundaries are actually MORE connected because others trust that their 'yes' is genuine and their 'no' is respected."},
            {"title": "Recognizing Boundary Violations", "duration": "5 min", "order": 2, "content": "Knowing when a boundary has been crossed — yours or someone else's — is a crucial skill. Signs YOUR boundaries may be compromised: You feel resentful, drained, or anxious after certain interactions. You often say yes when you mean no. You feel responsible for managing other people's emotions. You fear the consequences of saying no. You feel guilty for having needs. Signs you may be crossing SOMEONE ELSE's boundaries: They give short, closed answers. They cancel or avoid plans frequently. They seem tense or uncomfortable around you. They rarely share personal information with you. They say yes but their body language says no. The body's discomfort — that 'off' feeling in your gut — is often the first signal. Learning to trust and act on that signal is a form of self-respect."},
            {"title": "Setting Boundaries Assertively", "duration": "5 min", "order": 3, "content": "Assertiveness is the healthy middle ground between passive (ignoring your needs) and aggressive (violating others' needs). The three-part boundary formula: Step 1 — Describe the behavior specifically: 'When you look at my phone without asking...' Step 2 — Name the impact: '...I feel like my privacy isn't respected...' Step 3 — State your need clearly: '...I need us to agree that our phones are private.' Practice this formula in low-stakes situations first. Important: You do not need to justify, apologize for, or over-explain a boundary. 'No' is a complete sentence. People may push back — that is normal. Hold the boundary calmly and consistently. The discomfort of setting a boundary is almost always less than the resentment of not setting one."},
            {"title": "Boundaries in the Digital World", "duration": "4 min", "order": 4, "content": "Digital boundaries are one of the most urgent modern boundary skills. Questions to consider for your digital life: (1) What do I share publicly vs privately, and with whom? (2) Do I feel pressured to respond to messages immediately? Is that expectation healthy? (3) Am I comfortable with location sharing, and with whom? (4) How does my screen time affect my sleep, focus, and mood? (5) Are there platforms or interactions that consistently drain me? Your time and attention are finite, valuable resources. Setting digital boundaries might mean turning off notifications after 9pm, not responding to messages during study time, or unfollowing accounts that make you feel worse about yourself. You are allowed to shape your digital environment to support your well-being."},
        ],
    },
    {
        "course": {"title": "Ethical Leadership", "domain": "Decision-Making", "description": "Explore ethical decision-making frameworks and develop the values, courage, and judgment to lead with integrity, accountability, and a sense of responsibility.", "duration": "30 min", "icon_name": "target", "order": 5},
        "lessons": [
            {"title": "What Makes a Leader Ethical?", "duration": "7 min", "order": 1, "content": "Ethical leadership means consistently making decisions guided by values — not by convenience, self-interest, or fear. Research by James MacGregor Burns and later Bernard Bass distinguishes transactional leaders (who trade rewards for compliance) from transformational leaders (who inspire through values and vision). Five pillars of ethical leadership: (1) Integrity — doing what you say, being honest especially when it costs you. (2) Accountability — owning your mistakes without blame-shifting or excuse-making. (3) Fairness — treating people equitably, which sometimes means treating people differently based on their needs. (4) Respect — valuing every person's inherent dignity, regardless of their status or usefulness to you. (5) Service — orienting your leadership toward the good of the group, not personal gain. Ethical leaders don't just avoid doing wrong — they actively do right, even under pressure."},
            {"title": "Three Decision-Making Frameworks", "duration": "8 min", "order": 2, "content": "When facing ethical dilemmas, frameworks provide structure: Framework 1 — Utilitarianism (Jeremy Bentham, John Stuart Mill): Choose the action that produces the greatest good for the greatest number of people. Useful for policy and group decisions. Limitation: can justify harming a minority for the majority's benefit. Framework 2 — Virtue Ethics (Aristotle): Ask 'What would a person of good character do in this situation?' Focus on who you are becoming, not just what to do. Strength: makes ethics personal and developmental. Framework 3 — Deontology (Immanuel Kant): Some actions are inherently right or wrong, regardless of outcomes. Key test: 'Could this rule apply universally to everyone?' Strength: protects individuals from being sacrificed for collective benefit. Best practice: apply all three frameworks to any major ethical decision. If all three point to the same answer, you can proceed with confidence. If they diverge, that divergence itself is important data."},
            {"title": "Leading When It's Hard", "duration": "8 min", "order": 3, "content": "Ethical leadership is most tested in moments of pressure: when telling the truth could damage a relationship; when peer pressure pushes against your values; when the right decision is deeply unpopular; when you benefit from an unfair system; when staying silent is easier. Strategies for ethical courage: (1) The Newspaper Test: 'Would I be comfortable if this decision appeared on the front page tomorrow?' (2) The Mentor Test: 'What would the person I most respect think of this choice?' (3) Slow Down: Urgency is often used to bypass good judgment. Most decisions can wait 24 hours. (4) Consult Widely: Ethical blind spots shrink when diverse voices are heard. (5) Document Your Reasoning: Writing out your decision-making process creates accountability and clarity. Remember: short-term comfort from an unethical choice almost always creates long-term cost. Short-term discomfort from the ethical choice almost always creates long-term respect."},
            {"title": "Your Personal Leadership Values", "duration": "7 min", "order": 4, "content": "Your leadership values are the principles that guide your decisions when no one is watching and when it isn't easy. Step 1 — Identify your values by completing these sentences: 'I will always...' (e.g., tell the truth, give credit where it's due, listen before deciding). 'I will never...' (e.g., take credit for someone else's work, stay silent when I see injustice). 'Those I lead can count on me to...' Step 2 — Prioritize: when values conflict (e.g., loyalty vs honesty), which one takes precedence for you, and why? Step 3 — Write your Leadership Mission Statement: 'I lead by [value] and [value] to [intended impact].' Example: 'I lead with honesty and humility to create environments where every person's contribution is seen and valued.' Revisit and refine this every year as your experience deepens."},
        ],
    },
    {
        "course": {"title": "Active Listening", "domain": "Relationship Skills", "description": "Master the art of truly hearing others — staying present, understanding deeply, and responding thoughtfully. Build stronger relationships through the power of listening.", "duration": "12 min", "icon_name": "ear", "order": 6},
        "lessons": [
            {"title": "Are You Really Listening?", "duration": "3 min", "order": 1, "content": "Most people listen to respond, not to understand. Communication researcher Albert Mehrabian found that only 7% of meaning is conveyed through words — 38% through tone and 55% through body language. Yet most of us are only processing the words. Common listening barriers: (1) Mental rehearsal — thinking about what you'll say next while the other person is still talking. (2) Filtering — hearing only what confirms your existing beliefs. (3) Environmental distraction — phones, noise, notifications. (4) Emotional hijacking — a trigger word derails your full attention. (5) Advice-mode — jumping to solutions before the speaker has finished sharing. The first step to becoming an active listener is simply noticing which barrier shows up most frequently for YOU."},
            {"title": "The 5 Components of Active Listening", "duration": "4 min", "order": 2, "content": "Active listening is a skill with five interconnected components: (1) Attending — giving your full physical attention: face the speaker, maintain natural eye contact (not staring), put devices away, lean slightly forward. Your body communicates engagement before you say a word. (2) Understanding — going beyond the words to grasp the underlying meaning, feeling, and intent. Ask yourself: 'What are they really trying to tell me?' (3) Remembering — retaining key points, especially names and details that matter to the speaker. This signals that they are worth remembering. (4) Evaluating — withholding judgment until the speaker has fully finished. Premature evaluation shuts down honest communication. (5) Responding — using verbal and nonverbal signals ('I see,' 'go on,' nodding) to confirm that you're engaged, and then reflecting back what you've heard before adding your own perspective. All five components must be present simultaneously for listening to be truly active."},
            {"title": "Reflective Listening Techniques", "duration": "3 min", "order": 3, "content": "Reflective listening means mirroring back what you heard to confirm understanding and make the speaker feel genuinely heard. Three core techniques: (1) Paraphrasing — restate the content in your own words: 'So if I'm understanding correctly, you're saying that the project timeline feels unrealistic, and it's creating a lot of pressure for the whole team?' This surfaces misunderstandings before they compound. (2) Reflecting Feelings — name the emotion beneath the words: 'It sounds like you're feeling really overwhelmed — and maybe a bit unsupported?' People feel profoundly heard when their emotion is named accurately. (3) Summarizing — at natural pause points, briefly recap the main themes: 'So the key challenges seem to be X, Y, and Z — is that right?' Summarizing shows sustained attention and creates alignment. One rule: always end a reflection with an open question or a pause — this invites correction and keeps the conversation with them."},
            {"title": "Listening in Conflict", "duration": "2 min", "order": 4, "content": "Active listening is hardest — and most powerful — during conflict or disagreement. When emotions are high, we instinctively stop listening and start defending. The counter-intuitive truth: the person who listens first in a conflict almost always has more influence in the outcome. Five rules for listening in conflict: (1) Listen to understand their position fully before sharing yours. (2) Do not interrupt — even when you disagree strongly. (3) Acknowledge their point before responding: 'I hear that you felt excluded from that decision...' (4) Ask clarifying questions with curiosity, not interrogation: 'Help me understand what made that feel unfair.' (5) Monitor your own emotional state — if you're flooded, it's okay to say 'I want to hear you out fully, can we take a 5-minute pause first?' Research by John Gottman shows that physiological self-regulation during conflict is the single strongest predictor of relationship success."},
        ],
    },
]

def _seed_platform_courses():
    db = next(get_db())
    try:
        if db.query(models.PlatformCourse).count() == 0:
            for entry in _PLATFORM_COURSES_SEED:
                course = models.PlatformCourse(**entry["course"])
                db.add(course)
                db.flush()
                for lesson_data in entry["lessons"]:
                    db.add(models.PlatformCourseLesson(course_id=course.id, **lesson_data))
            db.commit()
        elif db.query(models.PlatformCourseLesson).count() == 0:
            # Courses exist but lessons were added later — seed lessons now
            for entry in _PLATFORM_COURSES_SEED:
                course = db.query(models.PlatformCourse).filter(
                    models.PlatformCourse.title == entry["course"]["title"]
                ).first()
                if course:
                    for lesson_data in entry["lessons"]:
                        db.add(models.PlatformCourseLesson(course_id=course.id, **lesson_data))
            db.commit()
    finally:
        db.close()

_seed_platform_courses()

app = FastAPI(title="EduXcel API")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── helpers ──────────────────────────────────────────────────────────────────

def generate_password(length=10):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def get_current_user(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise exc
    except auth.JWTError:
        raise exc
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise exc
    return user

def require_role(user: models.User, *roles):
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Not authorized")

# ── registration ─────────────────────────────────────────────────────────────

@app.post("/register/principal", response_model=schemas.UserResponse)
def register_principal(user: schemas.UserCreate, school: schemas.SchoolCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        uid=str(uuid.uuid4()), email=user.email,
        hashed_password=auth.get_password_hash(user.password),
        display_name=user.display_name, role="principal"
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    new_school = models.School(name=school.name, address=school.address, phone=school.phone, invite_code=invite_code, principal_id=new_user.id)
    db.add(new_school); db.commit(); db.refresh(new_school)
    new_user.school_id = new_school.id
    db.commit(); db.refresh(new_user)
    return new_user

@app.post("/register/parent", response_model=schemas.UserResponse)
def register_parent(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        uid=str(uuid.uuid4()), email=user.email,
        hashed_password=auth.get_password_hash(user.password),
        display_name=user.display_name, role="parent"
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    return new_user

@app.post("/register/teacher", response_model=schemas.UserResponse)
def register_teacher(data: schemas.UserCreateWithCode, db: Session = Depends(get_db)):
    school = db.query(models.School).filter(models.School.invite_code == data.invite_code.upper()).first()
    if not school:
        raise HTTPException(status_code=404, detail="Invalid school invite code")
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        uid=str(uuid.uuid4()), email=data.email,
        hashed_password=auth.get_password_hash(data.password),
        display_name=data.display_name, role="teacher", school_id=school.id
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    return new_user

@app.post("/register/student", response_model=schemas.UserResponse)
def register_student(data: schemas.UserCreateWithCode, db: Session = Depends(get_db)):
    school = db.query(models.School).filter(models.School.invite_code == data.invite_code.upper()).first()
    if not school:
        raise HTTPException(status_code=404, detail="Invalid school invite code")
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        uid=str(uuid.uuid4()), email=data.email,
        hashed_password=auth.get_password_hash(data.password),
        display_name=data.display_name, role="student", school_id=school.id
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    return new_user

# ── auth ──────────────────────────────────────────────────────────────────────

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    token = auth.create_access_token(data={"sub": user.email, "role": user.role}, expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# ── school ────────────────────────────────────────────────────────────────────

@app.get("/schools/my", response_model=schemas.SchoolResponse)
def get_my_school(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.school_id:
        raise HTTPException(status_code=404, detail="No school associated with this user")
    return db.query(models.School).filter(models.School.id == current_user.school_id).first()

@app.patch("/schools/my", response_model=schemas.SchoolResponse)
def update_school(data: schemas.SchoolUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    school = db.query(models.School).filter(models.School.id == current_user.school_id).first()
    if not school: raise HTTPException(status_code=404, detail="School not found")
    if data.name is not None: school.name = data.name
    if data.address is not None: school.address = data.address
    if data.phone is not None: school.phone = data.phone
    db.commit(); db.refresh(school)
    return school

# ── principal: user management ────────────────────────────────────────────────

@app.post("/schools/my/teachers", response_model=dict)
def add_teacher(user_data: schemas.UserBase, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    pwd = generate_password()
    new_user = models.User(uid=str(uuid.uuid4()), email=user_data.email, hashed_password=auth.get_password_hash(pwd), display_name=user_data.display_name, role="teacher", school_id=current_user.school_id)
    db.add(new_user); db.commit(); db.refresh(new_user)
    return {"user": schemas.UserResponse.model_validate(new_user).model_dump(), "generated_password": pwd}

@app.get("/schools/my/teachers", response_model=list[schemas.UserResponse])
def get_teachers(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    return db.query(models.User).filter(models.User.school_id == current_user.school_id, models.User.role == "teacher").all()

@app.post("/schools/my/students", response_model=dict)
def add_student(user_data: schemas.UserBase, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    pwd = generate_password()
    new_user = models.User(uid=str(uuid.uuid4()), email=user_data.email, hashed_password=auth.get_password_hash(pwd), display_name=user_data.display_name, role="student", school_id=current_user.school_id)
    db.add(new_user); db.commit(); db.refresh(new_user)
    return {"user": schemas.UserResponse.model_validate(new_user).model_dump(), "generated_password": pwd}

@app.get("/schools/my/students", response_model=list[schemas.UserResponse])
def get_students(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    return db.query(models.User).filter(models.User.school_id == current_user.school_id, models.User.role == "student").all()

@app.delete("/schools/my/users/{user_id}", status_code=204)
def remove_user(user_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    user = db.query(models.User).filter(models.User.id == user_id, models.User.school_id == current_user.school_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user); db.commit()

@app.get("/schools/my/parents", response_model=list[schemas.UserResponse])
def get_school_parents(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    student_ids = [s.id for s in db.query(models.User).filter(models.User.school_id == current_user.school_id, models.User.role == "student").all()]
    parent_ids = list(set(l.parent_id for l in db.query(models.ParentStudent).filter(models.ParentStudent.student_id.in_(student_ids)).all()))
    return db.query(models.User).filter(models.User.id.in_(parent_ids)).all()

# ── classes ───────────────────────────────────────────────────────────────────

@app.post("/schools/my/classes", response_model=schemas.ClassResponse)
def create_class(class_data: schemas.ClassCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    new_class = models.Class(name=class_data.name, school_id=current_user.school_id, teacher_id=class_data.teacher_id)
    db.add(new_class); db.commit(); db.refresh(new_class)
    return new_class

@app.get("/schools/my/classes", response_model=list[schemas.ClassResponse])
def get_classes(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    classes = db.query(models.Class).filter(models.Class.school_id == current_user.school_id).all()
    result = []
    for c in classes:
        count = db.query(models.Enrollment).filter(models.Enrollment.class_id == c.id).count()
        result.append(schemas.ClassResponse(
            id=c.id, name=c.name, school_id=c.school_id,
            teacher_id=c.teacher_id, created_at=c.created_at, student_count=count
        ))
    return result

@app.delete("/classes/{class_id}", status_code=204)
def delete_class(class_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    cls = db.query(models.Class).filter(models.Class.id == class_id, models.Class.school_id == current_user.school_id).first()
    if not cls: raise HTTPException(status_code=404, detail="Class not found")
    db.delete(cls); db.commit()

# ── enrollment ────────────────────────────────────────────────────────────────

@app.get("/classes/{class_id}/students", response_model=list[schemas.UserResponse])
def get_class_students(class_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.class_id == class_id).all()
    student_ids = [e.student_id for e in enrollments]
    return db.query(models.User).filter(models.User.id.in_(student_ids)).all()

@app.patch("/classes/{class_id}/teacher", response_model=schemas.ClassResponse)
def update_class_teacher(class_id: int, teacher_id: Optional[int] = None, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    cls = db.query(models.Class).filter(models.Class.id == class_id, models.Class.school_id == current_user.school_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    cls.teacher_id = teacher_id
    db.commit(); db.refresh(cls)
    count = db.query(models.Enrollment).filter(models.Enrollment.class_id == cls.id).count()
    return schemas.ClassResponse(id=cls.id, name=cls.name, school_id=cls.school_id, teacher_id=cls.teacher_id, created_at=cls.created_at, student_count=count)

@app.post("/classes/{class_id}/enroll/{student_id}", response_model=schemas.EnrollmentResponse)
def enroll_student(class_id: int, student_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    existing = db.query(models.Enrollment).filter(models.Enrollment.class_id == class_id, models.Enrollment.student_id == student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student already enrolled")
    enrollment = models.Enrollment(student_id=student_id, class_id=class_id)
    db.add(enrollment); db.commit(); db.refresh(enrollment)
    return enrollment

@app.delete("/classes/{class_id}/enroll/{student_id}", status_code=204)
def unenroll_student(class_id: int, student_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.class_id == class_id, models.Enrollment.student_id == student_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(enrollment); db.commit()

# ── subjects ──────────────────────────────────────────────────────────────────

@app.get("/classes/{class_id}/subjects", response_model=list[schemas.SubjectResponse])
def get_subjects(class_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Subject).filter(models.Subject.class_id == class_id).all()

@app.post("/classes/{class_id}/subjects", response_model=schemas.SubjectResponse)
def create_subject(class_id: int, data: schemas.SubjectCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    subject = models.Subject(name=data.name, description=data.description, class_id=class_id, created_by_id=current_user.id)
    db.add(subject); db.commit(); db.refresh(subject)
    return subject

@app.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(subject_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subject); db.commit()

# ── materials ─────────────────────────────────────────────────────────────────

@app.get("/subjects/{subject_id}/materials", response_model=list[schemas.MaterialResponse])
def get_materials(subject_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Material).filter(models.Material.subject_id == subject_id).all()

@app.post("/subjects/{subject_id}/materials/url", response_model=schemas.MaterialResponse)
def add_material_url(subject_id: int, data: schemas.MaterialCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    material = models.Material(title=data.title, description=data.description, material_type=data.material_type, url=data.url, subject_id=subject_id, uploaded_by_id=current_user.id)
    db.add(material); db.commit(); db.refresh(material)
    return material

@app.post("/subjects/{subject_id}/materials/upload", response_model=schemas.MaterialResponse)
async def upload_material_file(
    subject_id: int,
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_role(current_user, "principal", "teacher")
    ext = Path(file.filename).suffix.lower()
    material_type = "video" if ext in (".mp4", ".mov", ".avi", ".webm", ".mkv", ".wmv", ".m4v", ".3gp", ".ts") else "pdf" if ext == ".pdf" else "file"
    save_name = f"{uuid.uuid4()}{ext}"
    save_path = UPLOAD_DIR / save_name
    with save_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)
    url = f"/uploads/{save_name}"
    material = models.Material(title=title, description=description, material_type=material_type, url=url, filename=file.filename, subject_id=subject_id, uploaded_by_id=current_user.id)
    db.add(material); db.commit(); db.refresh(material)
    return material

@app.delete("/materials/{material_id}", status_code=204)
def delete_material(material_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    material = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Not found")
    if material.filename and material.url:
        p = UPLOAD_DIR / Path(material.url).name
        if p.exists():
            p.unlink()
    db.delete(material); db.commit()

@app.patch("/materials/{material_id}", response_model=schemas.MaterialResponse)
def update_material(material_id: int, data: schemas.MaterialUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    material = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not material: raise HTTPException(status_code=404, detail="Not found")
    if data.title is not None: material.title = data.title
    if data.description is not None: material.description = data.description
    db.commit(); db.refresh(material)
    return material

# ── teacher routes ────────────────────────────────────────────────────────────

@app.get("/teachers/my/classes", response_model=list[schemas.ClassResponse])
def teacher_get_classes(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "teacher")
    classes = db.query(models.Class).filter(models.Class.teacher_id == current_user.id).all()
    result = []
    for c in classes:
        count = db.query(models.Enrollment).filter(models.Enrollment.class_id == c.id).count()
        result.append(schemas.ClassResponse(
            id=c.id, name=c.name, school_id=c.school_id,
            teacher_id=c.teacher_id, created_at=c.created_at, student_count=count
        ))
    return result

# ── student routes ────────────────────────────────────────────────────────────

@app.get("/students/my/classes", response_model=list[schemas.ClassResponse])
def student_get_classes(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "student")
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.student_id == current_user.id).all()
    class_ids = [e.class_id for e in enrollments]
    classes = db.query(models.Class).filter(models.Class.id.in_(class_ids)).all()
    result = []
    for c in classes:
        count = db.query(models.Enrollment).filter(models.Enrollment.class_id == c.id).count()
        result.append(schemas.ClassResponse(
            id=c.id, name=c.name, school_id=c.school_id,
            teacher_id=c.teacher_id, created_at=c.created_at, student_count=count
        ))
    return result

# ── parent routes ─────────────────────────────────────────────────────────────

@app.get("/parents/my/children", response_model=list[schemas.UserResponse])
def get_children(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "parent")
    links = db.query(models.ParentStudent).filter(models.ParentStudent.parent_id == current_user.id).all()
    student_ids = [l.student_id for l in links]
    return db.query(models.User).filter(models.User.id.in_(student_ids)).all()

@app.post("/parents/link-student", response_model=schemas.UserResponse)
def link_student(student_email: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "parent")
    student = db.query(models.User).filter(models.User.email == student_email, models.User.role == "student").first()
    if not student: raise HTTPException(status_code=404, detail="No student found with that email")
    existing = db.query(models.ParentStudent).filter(models.ParentStudent.parent_id == current_user.id, models.ParentStudent.student_id == student.id).first()
    if existing: raise HTTPException(status_code=400, detail="Already linked to this student")
    db.add(models.ParentStudent(parent_id=current_user.id, student_id=student.id)); db.commit()
    return student

@app.delete("/parents/unlink-student/{student_id}", status_code=204)
def unlink_student(student_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "parent")
    link = db.query(models.ParentStudent).filter(models.ParentStudent.parent_id == current_user.id, models.ParentStudent.student_id == student_id).first()
    if not link: raise HTTPException(status_code=404, detail="Not linked")
    db.delete(link); db.commit()

@app.get("/parents/student/{student_id}/classes", response_model=list[schemas.ClassResponse])
def parent_view_student_classes(student_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "parent")
    link = db.query(models.ParentStudent).filter(models.ParentStudent.parent_id == current_user.id, models.ParentStudent.student_id == student_id).first()
    if not link: raise HTTPException(status_code=403, detail="Not linked to this student")
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.student_id == student_id).all()
    class_ids = [e.class_id for e in enrollments]
    classes = db.query(models.Class).filter(models.Class.id.in_(class_ids)).all()
    result = []
    for c in classes:
        count = db.query(models.Enrollment).filter(models.Enrollment.class_id == c.id).count()
        result.append(schemas.ClassResponse(id=c.id, name=c.name, school_id=c.school_id, teacher_id=c.teacher_id, created_at=c.created_at, student_count=count))
    return result

# ── platform course library ───────────────────────────────────────────────────

@app.get("/platform-courses", response_model=list[schemas.PlatformCourseResponse])
def get_platform_courses(db: Session = Depends(get_db)):
    return db.query(models.PlatformCourse).order_by(models.PlatformCourse.order).all()

@app.get("/platform-courses/{course_id}", response_model=schemas.PlatformCourseResponse)
def get_platform_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.PlatformCourse).filter(models.PlatformCourse.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.post("/platform-courses/{course_id}/materials/url", response_model=schemas.PlatformCourseMaterialResponse)
def add_platform_material_url(course_id: int, data: schemas.MaterialCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    if not db.query(models.PlatformCourse).filter(models.PlatformCourse.id == course_id).first():
        raise HTTPException(status_code=404, detail="Course not found")
    material = models.PlatformCourseMaterial(course_id=course_id, title=data.title, description=data.description, material_type=data.material_type, url=data.url)
    db.add(material); db.commit(); db.refresh(material)
    return material

@app.post("/platform-courses/{course_id}/materials/upload", response_model=schemas.PlatformCourseMaterialResponse)
async def upload_platform_material(
    course_id: int,
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_role(current_user, "principal", "teacher")
    if not db.query(models.PlatformCourse).filter(models.PlatformCourse.id == course_id).first():
        raise HTTPException(status_code=404, detail="Course not found")
    ext = Path(file.filename).suffix.lower()
    material_type = "video" if ext in (".mp4", ".mov", ".avi", ".webm", ".mkv") else "pdf" if ext == ".pdf" else "worksheet" if ext in (".docx", ".doc") else "file"
    save_name = f"{uuid.uuid4()}{ext}"
    save_path = UPLOAD_DIR / save_name
    with save_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)
    material = models.PlatformCourseMaterial(course_id=course_id, title=title, description=description, material_type=material_type, url=f"/uploads/{save_name}", filename=file.filename)
    db.add(material); db.commit(); db.refresh(material)
    return material

@app.get("/platform-courses/{course_id}/lessons", response_model=list[schemas.PlatformCourseLessonResponse])
def get_platform_course_lessons(course_id: int, db: Session = Depends(get_db)):
    return db.query(models.PlatformCourseLesson).filter(models.PlatformCourseLesson.course_id == course_id).order_by(models.PlatformCourseLesson.order).all()

@app.delete("/platform-course-materials/{material_id}", status_code=204)
def delete_platform_material(material_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    material = db.query(models.PlatformCourseMaterial).filter(models.PlatformCourseMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Not found")
    if material.filename and material.url:
        p = UPLOAD_DIR / Path(material.url).name
        if p.exists():
            p.unlink()
    db.delete(material); db.commit()

# ── misc ──────────────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"message": "EduXcel API is running"}
