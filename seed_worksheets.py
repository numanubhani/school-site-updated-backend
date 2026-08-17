"""
Run this script once to generate PDF worksheets for all 6 platform courses
and seed them into the database as course materials.

Usage:
    python seed_worksheets.py
"""

import sys, uuid
from pathlib import Path
from fpdf import FPDF
from database import engine, SessionLocal
import models

models.Base.metadata.create_all(bind=engine)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

WORKSHEETS = [
    {
        "course_title": "Identifying Emotions",
        "worksheet_title": "The Emotion Journal",
        "instructions": (
            "For each of the three situations below, identify the emotion you felt, "
            "rate its intensity, describe the physical sensations in your body, and name "
            "the thought that accompanied the emotion. Be as specific as possible."
        ),
        "objectives": [
            "Identify and name at least 8 primary and secondary emotions",
            "Recognize physical sensations associated with emotions",
            "Understand how emotions influence thoughts and behavior",
            "Practice emotional vocabulary in real-life scenarios",
        ],
        "key_concepts": [
            "Primary vs Secondary Emotions",
            "The Emotion Wheel (Plutchik)",
            "Emotional Granularity",
            "Somatic Awareness",
            "Cognitive-Emotional Cycle",
        ],
        "sections": [
            {
                "heading": "Part 1: Emotion Identification",
                "questions": [
                    ("Situation 1", "Describe a recent situation that triggered a strong emotion:\n\n\n\n"
                     "Emotion name (be specific — not just 'bad' or 'good'):\n\n\n"
                     "Intensity (circle): 1   2   3   4   5   6   7   8   9   10\n\n"
                     "Physical sensations in your body:\n\n\n"
                     "The thought that came with this emotion:\n\n\n"),
                    ("Situation 2", "Describe a second situation that triggered a different emotion:\n\n\n\n"
                     "Emotion name:\n\n\n"
                     "Intensity (circle): 1   2   3   4   5   6   7   8   9   10\n\n"
                     "Physical sensations in your body:\n\n\n"
                     "The thought that came with this emotion:\n\n\n"),
                    ("Situation 3", "Describe a third situation:\n\n\n\n"
                     "Emotion name:\n\n\n"
                     "Intensity (circle): 1   2   3   4   5   6   7   8   9   10\n\n"
                     "Physical sensations in your body:\n\n\n"
                     "The thought that came with this emotion:\n\n\n"),
                ],
            },
            {
                "heading": "Part 2: Expanding Your Emotion Vocabulary",
                "questions": [
                    ("Exercise", "List 5 emotions more specific than 'happy':\n1.\n2.\n3.\n4.\n5.\n\n"
                     "List 5 emotions more specific than 'sad':\n1.\n2.\n3.\n4.\n5.\n\n"
                     "List 5 emotions more specific than 'angry':\n1.\n2.\n3.\n4.\n5."),
                ],
            },
            {
                "heading": "Part 3: Reflection",
                "questions": [
                    ("Reflection Questions",
                     "1. What was the most surprising emotion you noticed this week, and why?\n\n\n\n"
                     "2. How did naming your emotion change the way you responded to it?\n\n\n\n"
                     "3. Which physical sensation in your body is the clearest signal that you are stressed?\n\n\n"),
                ],
            },
        ],
    },
    {
        "course_title": "Stress Management 101",
        "worksheet_title": "My Personal Stress Management Plan",
        "instructions": (
            "Complete each section thoughtfully. This worksheet will become your personal "
            "reference guide for managing stress. The more honest and specific you are, "
            "the more useful it will be."
        ),
        "objectives": [
            "Understand the stress response (fight-or-flight)",
            "Identify your personal stress triggers",
            "Learn 5 evidence-based stress management techniques",
            "Create a personalized, actionable stress management plan",
        ],
        "key_concepts": [
            "Fight-or-Flight Response",
            "Cortisol & Adrenaline",
            "Eustress vs Distress",
            "Parasympathetic Nervous System",
            "Box Breathing",
            "5-4-3-2-1 Grounding",
            "Progressive Muscle Relaxation",
        ],
        "sections": [
            {
                "heading": "Part 1: Know Your Triggers",
                "questions": [
                    ("My Top 3 Stress Triggers",
                     "1. _______________________________________________\n"
                     "   How does my body react? ___________________________\n\n"
                     "2. _______________________________________________\n"
                     "   How does my body react? ___________________________\n\n"
                     "3. _______________________________________________\n"
                     "   How does my body react? ___________________________\n"),
                    ("Early Warning Signs",
                     "List 3 physical signals that tell you stress is building BEFORE it peaks:\n"
                     "1.\n2.\n3."),
                ],
            },
            {
                "heading": "Part 2: Technique Practice Log",
                "questions": [
                    ("Box Breathing",
                     "Practiced on (date): ________   Situation: __________________________\n"
                     "How did it feel? (1=didn't help  5=very helpful)  1   2   3   4   5\n"
                     "Notes:\n\n"),
                    ("5-4-3-2-1 Grounding",
                     "Practiced on (date): ________   Situation: __________________________\n"
                     "5 things I saw:   1.          2.          3.          4.          5.\n"
                     "4 things I felt:  1.          2.          3.          4.\n"
                     "3 things I heard: 1.          2.          3.\n"
                     "How helpful? (1-5): ___\n\n"),
                    ("Movement / Physical Activity",
                     "Activity I tried: __________________________   Duration: __________\n"
                     "How stressed was I before? (1-10): ___   After? (1-10): ___\n"),
                    ("Expressive Journaling",
                     "Topic I wrote about: _________________________________________________\n"
                     "Did writing reduce the intensity of the stressor? Yes / Somewhat / No\n"
                     "One insight from writing:\n\n"),
                ],
            },
            {
                "heading": "Part 3: My Stress Management Plan",
                "questions": [
                    ("My Best Techniques (top 2-3 that worked for me)",
                     "1.\n2.\n3."),
                    ("My Daily Self-Care Commitments",
                     "Sleep: I will aim for ______ hours per night.\n"
                     "Movement: I will _________________________ for ______ minutes per day.\n"
                     "Connection: I will spend time with ________________________________.\n"
                     "Nutrition: I will ______________________________________________."),
                    ("My Stress Emergency Kit (3 actions for peak stress moments)",
                     "1.\n2.\n3."),
                ],
            },
            {
                "heading": "Part 4: Reflection",
                "questions": [
                    ("Questions",
                     "1. Which technique surprised you by being more effective than you expected?\n\n\n"
                     "2. What makes stress management harder for you personally?\n\n\n"
                     "3. Who in your life can you contact when stress becomes overwhelming?\n\n"),
                ],
            },
        ],
    },
    {
        "course_title": "The Empathy Project",
        "worksheet_title": "The Perspective Challenge",
        "instructions": (
            "Read each scenario carefully. Then answer the questions from multiple "
            "perspectives — your own, the other person's, and any neutral observer's. "
            "There are no right or wrong answers. The goal is to practice seeing beyond "
            "your own viewpoint."
        ),
        "objectives": [
            "Define empathy and distinguish it from sympathy",
            "Practice perspective-taking in realistic social scenarios",
            "Identify personal barriers to empathy",
            "Apply empathic responses in conversation",
        ],
        "key_concepts": [
            "Empathy vs Sympathy",
            "Perspective-Taking",
            "Emotional Validation",
            "Empathic Communication",
            "Active Presence",
            "Barriers to Empathy",
        ],
        "sections": [
            {
                "heading": "Scenario 1: The Classroom",
                "questions": [
                    ("Scenario",
                     "Your classmate gives a class presentation and makes several mistakes. "
                     "The class laughs. Your classmate goes quiet and doesn't speak for "
                     "the rest of the lesson.\n"),
                    ("Perspective Questions",
                     "1. What might your classmate be feeling right now? List at least 3 specific emotions:\n\n\n\n"
                     "2. What might they be thinking about themselves and the situation?\n\n\n\n"
                     "3. What past experiences might make this moment especially hard for them?\n\n\n\n"
                     "4. Write one empathic statement you could say to this person:\n\n\n"
                     "5. What would a sympathetic response look like? What's the difference?\n\n\n"),
                ],
            },
            {
                "heading": "Scenario 2: At Home",
                "questions": [
                    ("Scenario",
                     "A family member snaps at you for something small. Later you find out "
                     "they received difficult news that morning but didn't tell anyone.\n"),
                    ("Perspective Questions",
                     "1. Before you knew about the news, what did you feel when they snapped? What did you assume?\n\n\n\n"
                     "2. How does knowing the context change your interpretation of their behavior?\n\n\n\n"
                     "3. What might they have needed in that moment but didn't ask for?\n\n\n\n"
                     "4. Write an empathic response you could offer now:\n\n\n"),
                ],
            },
            {
                "heading": "Scenario 3: Conflict with a Friend",
                "questions": [
                    ("Scenario",
                     "You plan something with a close friend, but they cancel last minute "
                     "for the third time. You feel hurt and frustrated. Your friend says "
                     "they've 'just been busy.'\n"),
                    ("Perspective Questions",
                     "1. What are you feeling, and what need is going unmet for you?\n\n\n\n"
                     "2. List 3 possible reasons your friend might be canceling (beyond just 'being busy'):\n\n\n\n"
                     "3. How could you communicate your feelings without blaming?\n\n\n\n"
                     "4. How could you show empathy for what they may be going through while still expressing your needs?\n\n\n"),
                ],
            },
            {
                "heading": "Part 2: Self-Reflection",
                "questions": [
                    ("Your Personal Barriers",
                     "1. Which barrier to empathy do you recognize most in yourself? (bias, overwhelm, othering, etc.)\n\n\n"
                     "2. Describe a time you wish you had responded with more empathy. What held you back?\n\n\n\n"
                     "3. Describe a time someone showed you genuine empathy. How did it make you feel?\n\n\n"),
                ],
            },
        ],
    },
    {
        "course_title": "Healthy Boundaries",
        "worksheet_title": "My Boundary Map",
        "instructions": (
            "A Boundary Map helps you visualize and define the limits you have — or "
            "want to set — across different types of relationships. Complete each section "
            "honestly. Remember: boundaries protect relationships, they don't destroy them."
        ),
        "objectives": [
            "Define personal boundaries across different relationship types",
            "Recognize signs of healthy vs unhealthy boundaries",
            "Practice communicating boundaries assertively",
            "Understand boundaries in physical, emotional, time, and digital domains",
        ],
        "key_concepts": [
            "Types of Boundaries (Physical, Emotional, Time, Digital, Material)",
            "Assertive Communication",
            "Boundary Violations",
            "The Three-Part Boundary Formula",
            "Healthy vs Unhealthy Boundaries",
        ],
        "sections": [
            {
                "heading": "Part 1: My Boundary Map",
                "questions": [
                    ("Friendships",
                     "Physical boundary I have with friends:\n\n"
                     "Emotional boundary I have with friends:\n\n"
                     "Time/energy boundary I have with friends:\n\n"
                     "Digital boundary I have with friends:\n\n"),
                    ("Family",
                     "Physical boundary I have with family:\n\n"
                     "Emotional boundary I have with family:\n\n"
                     "Time/energy boundary I have with family:\n\n"
                     "Topics I prefer not to discuss with certain family members:\n\n"),
                    ("School / Work",
                     "How I protect my focus and study time:\n\n"
                     "How I handle requests that take more than I can give:\n\n"
                     "How I handle social media during school/work:\n\n"),
                    ("Romantic Relationships",
                     "Physical boundaries that are important to me:\n\n"
                     "Emotional boundaries that are important to me:\n\n"
                     "Digital privacy boundaries:\n\n"),
                ],
            },
            {
                "heading": "Part 2: Boundary Practice",
                "questions": [
                    ("Using the Three-Part Formula",
                     "Choose a real boundary you need to set. Write it out:\n\n"
                     "When you [specific behavior]: __________________________________\n\n"
                     "I feel [emotion]: ______________________________________________\n\n"
                     "I need [specific request]: ______________________________________\n\n"
                     "How do you think this person might react? How will you hold the boundary calmly?\n\n\n"),
                    ("Boundary Violations",
                     "Describe a recent situation where a boundary of yours was crossed:\n\n\n\n"
                     "Describe a time you may have crossed someone else's boundary (even unintentionally):\n\n\n\n"
                     "What did you learn from each situation?\n\n\n"),
                ],
            },
            {
                "heading": "Part 3: Digital Boundaries Audit",
                "questions": [
                    ("My Digital Audit",
                     "Do I feel pressure to respond to messages immediately?   Yes / Sometimes / No\n"
                     "What time do I stop responding to messages at night? ___________\n"
                     "List 2 digital habits I want to change:\n1.\n2.\n\n"
                     "One digital boundary I will set this week:\n\n"),
                ],
            },
            {
                "heading": "Part 4: Reflection",
                "questions": [
                    ("Questions",
                     "1. In which relationship do you find it hardest to set boundaries? Why?\n\n\n\n"
                     "2. What happens when you don't set a boundary that you needed to set?\n\n\n\n"
                     "3. How would your life be different if your boundaries were consistently respected?\n\n\n"),
                ],
            },
        ],
    },
    {
        "course_title": "Ethical Leadership",
        "worksheet_title": "The Ethical Dilemma Lab",
        "instructions": (
            "Ethical dilemmas are situations where there is no clear right answer — "
            "where competing values, loyalties, or interests create genuine tension. "
            "Use the three decision-making frameworks (Utilitarianism, Virtue Ethics, "
            "Deontology) to analyze each case. Then write your own reasoned response."
        ),
        "objectives": [
            "Apply three ethical decision-making frameworks",
            "Analyze real-world ethical dilemmas with nuance",
            "Identify personal leadership values",
            "Write a personal leadership mission statement",
        ],
        "key_concepts": [
            "Integrity & Accountability",
            "Utilitarianism",
            "Virtue Ethics",
            "Deontology",
            "Ethical Courage",
            "The Newspaper Test",
            "Transformational Leadership",
        ],
        "sections": [
            {
                "heading": "Dilemma 1: The Shortcut",
                "questions": [
                    ("Case",
                     "You are a team leader for a group project. Your team is exhausted "
                     "and behind schedule. A teammate suggests copying a section from "
                     "an online source without citing it — 'just this once.' Most of "
                     "the team agrees. Your grade — and theirs — depends on this project.\n"),
                    ("Analysis",
                     "Utilitarian view (greatest good for greatest number):\n\n\n\n"
                     "Virtue Ethics view (what would a person of good character do?):\n\n\n\n"
                     "Deontological view (is this action universally acceptable?):\n\n\n\n"
                     "What would YOU do, and why?\n\n\n\n"
                     "What are the short-term and long-term consequences of each choice?\n\n\n"),
                ],
            },
            {
                "heading": "Dilemma 2: The Secret",
                "questions": [
                    ("Case",
                     "A close friend confides that they have been struggling with a serious "
                     "issue that could put them in danger. They beg you not to tell anyone. "
                     "You genuinely care about them and don't want to betray their trust, "
                     "but you're worried.\n"),
                    ("Analysis",
                     "Utilitarian view:\n\n\n\n"
                     "Virtue Ethics view:\n\n\n\n"
                     "Deontological view:\n\n\n\n"
                     "What would YOU do? How would you balance loyalty with safety?\n\n\n\n"
                     "What would you say to your friend regardless of your decision?\n\n\n"),
                ],
            },
            {
                "heading": "Dilemma 3: The Unfair Advantage",
                "questions": [
                    ("Case",
                     "You discover that a selection process you benefited from — for a "
                     "leadership position or team — was unfair to another candidate who "
                     "was more qualified. No one else knows. Speaking up might cost you "
                     "the position.\n"),
                    ("Analysis",
                     "Utilitarian view:\n\n\n\n"
                     "Virtue Ethics view:\n\n\n\n"
                     "Deontological view:\n\n\n\n"
                     "What would YOU do? What does ethical courage require here?\n\n\n\n"
                     "Apply the Newspaper Test: would you be comfortable if your choice was public?\n\n\n"),
                ],
            },
            {
                "heading": "Part 2: My Leadership Values",
                "questions": [
                    ("Building My Values Statement",
                     "I will always: __________________________________________________\n\n"
                     "I will never: ___________________________________________________\n\n"
                     "Those I lead can count on me to: ________________________________\n\n"
                     "When values conflict, I prioritize: ________________________________\n\n"
                     "My Leadership Mission Statement:\n"
                     "'I lead by _________________ and _________________ to ______________________________.'\n"),
                ],
            },
        ],
    },
    {
        "course_title": "Active Listening",
        "worksheet_title": "The Listening Lab",
        "instructions": (
            "This worksheet includes both solo reflection and paired partner exercises. "
            "Complete the individual sections on your own, then work through the partner "
            "exercises with a classmate or someone at home."
        ),
        "objectives": [
            "Identify personal listening barriers",
            "Practice the 5 components of active listening",
            "Apply reflective listening techniques",
            "Use active listening during conflict or disagreement",
        ],
        "key_concepts": [
            "Active Listening vs Passive Hearing",
            "The 5 Components (Attending, Understanding, Remembering, Evaluating, Responding)",
            "Paraphrasing",
            "Reflecting Feelings",
            "Summarizing",
            "Listening in Conflict",
        ],
        "sections": [
            {
                "heading": "Part 1: Self-Assessment",
                "questions": [
                    ("My Listening Habits",
                     "Rate yourself honestly (1 = rarely, 5 = always):\n\n"
                     "I give my full attention without checking my phone:           1  2  3  4  5\n"
                     "I wait for the person to finish before I respond:             1  2  3  4  5\n"
                     "I can remember the key points of a conversation:              1  2  3  4  5\n"
                     "I recognize when my emotions distract me from listening:      1  2  3  4  5\n"
                     "I ask questions to clarify rather than to challenge:          1  2  3  4  5\n"
                     "I reflect feelings back to make the speaker feel heard:       1  2  3  4  5\n\n"
                     "My strongest listening skill:\n\n"
                     "The barrier I struggle with most:\n\n"),
                ],
            },
            {
                "heading": "Part 2: Partner Exercise — 3-Minute Share",
                "questions": [
                    ("Instructions",
                     "Partner A speaks for 3 minutes about something meaningful — "
                     "a challenge they've faced, something they care about, or a recent experience. "
                     "Partner B listens without speaking. No phone, no nodding advice — just listening.\n"),
                    ("Partner B: After the 3 minutes, respond using these techniques",
                     "Paraphrase (restate the content): 'So what I heard is...'\n\n\n\n"
                     "Reflect the feeling: 'It sounds like you felt...'\n\n\n\n"
                     "Summarize the main themes: 'The key things that stood out were...'\n\n\n\n"
                     "Ask one open question: 'What has been the hardest part for you?'\n\n\n"),
                    ("Partner A: Feedback",
                     "Did you feel truly heard? (1=not at all  5=completely)   1  2  3  4  5\n\n"
                     "What specifically made you feel heard (or not)?\n\n\n\n"
                     "What would have made you feel even more heard?\n\n\n"),
                ],
            },
            {
                "heading": "Part 3: Listening in Conflict Roleplay",
                "questions": [
                    ("Scenario",
                     "Partner A is upset that Partner B forgot an important commitment "
                     "they had together. Partner A expresses this frustration. "
                     "Partner B must listen actively before defending or explaining.\n"),
                    ("Partner B: Practice these steps",
                     "1. Let Partner A finish completely without interrupting.\n"
                     "2. Acknowledge before responding: 'I hear that you felt let down...'\n"
                     "3. Ask a clarifying question with genuine curiosity.\n"
                     "4. Then — and only then — share your perspective.\n\n"
                     "Write what you said in step 2:\n\n\n"
                     "Write the clarifying question from step 3:\n\n\n"
                     "How did it feel to listen first, before defending?\n\n\n"),
                ],
            },
            {
                "heading": "Part 4: Real-World Commitment",
                "questions": [
                    ("This Week",
                     "Choose one person and one situation where you will practice active listening:\n\n"
                     "Person: ___________________________  Situation: ________________________\n\n"
                     "Which technique will you focus on? ______________________________________\n\n"
                     "After you do it, come back and reflect:\n"
                     "What happened? How did the other person respond?\n\n\n\n"
                     "What was harder than expected? What went well?\n\n\n"),
                ],
            },
        ],
    },
]


W = 170  # usable page width (210 - 20 left - 20 right)

def _ascii(s: str) -> str:
    """Replace non-Latin-1 characters with safe ASCII equivalents."""
    return (s
        .replace("—", " - ").replace("–", "-")
        .replace("‘", "'").replace("’", "'")
        .replace("“", '"').replace("”", '"')
        .replace("•", "-").replace("…", "...")
        .replace("â", "'")
        .encode("latin-1", errors="replace").decode("latin-1")
    )

def make_pdf(ws_data: dict):
    course_title = ws_data["course_title"]

    class WS(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(130, 130, 130)
            self.set_x(20)
            self.cell(W, 7, _ascii(f"SkillsOra SEL Academy  |  {course_title}"), ln=1)
            self.set_draw_color(210, 210, 210)
            self.line(20, self.get_y(), 190, self.get_y())
            self.ln(3)

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(150, 150, 150)
            self.set_x(20)
            self.cell(W, 8,
                      _ascii(f"Page {self.page_no()}  |  SkillsOra - Social Emotional Learning  |  {course_title}"),
                      align="C", ln=1)

    pdf = WS()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(20, 20, 20)
    pdf.add_page()

    def t(s, size=10, style="", color=(40, 40, 40), h=6, align="L"):
        """Print multi-cell text, always starting from left margin."""
        pdf.set_font("Helvetica", style, size)
        pdf.set_text_color(*color)
        pdf.set_x(20)
        pdf.multi_cell(W, h, _ascii(s), align=align)

    def rule(gray=200):
        pdf.set_draw_color(gray, gray, gray)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())

    def row(left, right, lw=88, fw=11):
        pdf.set_font("Helvetica", "", fw)
        pdf.set_text_color(50, 50, 50)
        pdf.set_x(20)
        pdf.cell(lw, 8, left, ln=0)
        pdf.cell(W - lw, 8, right, ln=1)

    def label(text_str, fill=(238, 238, 248)):
        pdf.set_fill_color(*fill)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.set_x(20)
        pdf.cell(W, 8, _ascii(f"  {text_str}"), fill=True, ln=1)

    # Title
    pdf.ln(2)
    t(ws_data["worksheet_title"], size=20, style="B", color=(20, 20, 20), h=9)
    t(f"Course: {course_title}  |  Student Worksheet", size=11, color=(90, 90, 90), h=7)
    pdf.ln(2)
    rule(175)
    pdf.ln(5)

    # Student info
    row("Name: ____________________________________", "Date: ___________________")
    row("Grade / Class: ___________________________", "Teacher: ________________")
    pdf.ln(5)

    # Instructions
    label("Instructions")
    t(ws_data["instructions"], size=10, color=(60, 60, 60), h=6)
    pdf.ln(4)

    # Learning objectives
    label("Learning Objectives")
    for obj in ws_data["objectives"]:
        t(f"  - {obj}", size=10, color=(60, 60, 60), h=6)
    pdf.ln(3)

    # Key concepts
    label("Key Concepts")
    t("  " + "  |  ".join(ws_data["key_concepts"]), size=10, color=(60, 60, 60), h=6)
    pdf.ln(5)
    rule(210)
    pdf.ln(5)

    # Sections
    for section in ws_data["sections"]:
        pdf.set_fill_color(220, 220, 240)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(20, 20, 60)
        pdf.set_x(20)
        pdf.cell(W, 9, _ascii(f"  {section['heading']}"), fill=True, ln=1)
        pdf.ln(3)
        for q_label, q_body in section["questions"]:
            if q_label and q_label not in ("Instructions",):
                style = "BI" if q_label not in ("Scenario", "Case") else "B"
                t(q_label, size=10, style=style, color=(50, 50, 90), h=6)
            t(q_body, size=10, color=(50, 50, 50), h=6)
            pdf.ln(2)
        pdf.ln(4)

    fname = "worksheet_" + course_title.lower().replace(" ", "_") + ".pdf"
    path = UPLOAD_DIR / fname
    pdf.output(str(path))
    return path, fname


def seed():
    db = SessionLocal()
    try:
        for ws_data in WORKSHEETS:
            course_title = ws_data["course_title"]
            course = db.query(models.PlatformCourse).filter(models.PlatformCourse.title == course_title).first()
            if not course:
                print(f"  SKIP — course not found in DB: {course_title}")
                continue

            already = db.query(models.PlatformCourseMaterial).filter(
                models.PlatformCourseMaterial.course_id == course.id,
                models.PlatformCourseMaterial.title == ws_data["worksheet_title"],
            ).first()
            if already:
                print(f"  SKIP — worksheet already seeded for: {course_title}")
                continue

            print(f"  Generating PDF for: {course_title} ...")
            path, fname = make_pdf(ws_data)
            material = models.PlatformCourseMaterial(
                course_id=course.id,
                title=ws_data["worksheet_title"],
                description=f"Printable student worksheet for {course_title}. Includes guided questions, reflection exercises, and activities aligned with the lesson content.",
                material_type="pdf",
                url=f"/uploads/{fname}",
                filename=fname,
            )
            db.add(material)
            db.commit()
            print(f"  Done — saved to {path}")

        print("\nAll worksheets generated and seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding PDF worksheets for all platform courses...\n")
    seed()
