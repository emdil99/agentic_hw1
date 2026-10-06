"""The data the tools read: Pilates exercises and medication label keywords."""

# Exercises in class order, warm-up first and cool-down last.
#   level        beginner, intermediate, or advanced
#   minutes      time to teach it
#   avoid_for    conditions it isn't safe for
#   modification an easier or safer version
EXERCISES = {
    "Supine Breathing": {
        "level": "beginner",
        "minutes": 3,
        "avoid_for": [],
        "modification": "Sit on a chair and breathe into the sides of the ribs.",
    },
    "Pelvic Curl": {
        "level": "beginner",
        "minutes": 4,
        "avoid_for": ["osteoporosis", "disc_herniation"],
        "modification": "Lift the hips with a long, neutral spine instead of rolling up one bone at a time.",
    },
    "Cat-Cow": {
        "level": "beginner",
        "minutes": 3,
        "avoid_for": ["wrist_pain"],
        "modification": "Do it seated on a chair with the hands on the thighs.",
    },
    "Chest Lift": {
        "level": "beginner",
        "minutes": 3,
        "avoid_for": ["osteoporosis", "neck_pain", "pregnancy", "diastasis_recti"],
        "modification": "Keep the head on the mat and exhale to draw the abdominals in.",
    },
    "The Hundred": {
        "level": "beginner",
        "minutes": 3,
        "avoid_for": ["osteoporosis", "neck_pain", "pregnancy", "diastasis_recti"],
        "modification": "Keep the head on the mat and pump the arms. Seated on a chair works too.",
    },
    "Roll Up": {
        "level": "intermediate",
        "minutes": 4,
        "avoid_for": ["osteoporosis", "disc_herniation", "neck_pain", "pregnancy"],
        "modification": "Half roll back: start seated with knees bent and roll back only partway.",
    },
    "Single Leg Circles": {
        "level": "beginner",
        "minutes": 4,
        "avoid_for": ["hip_replacement"],
        "modification": "Keep the bottom knee bent and make small circles that don't cross the body.",
    },
    "Rolling Like a Ball": {
        "level": "intermediate",
        "minutes": 3,
        "avoid_for": ["osteoporosis", "disc_herniation", "neck_pain", "pregnancy"],
        "modification": "Balance behind the sit bones and hold, without rolling.",
    },
    "Single Leg Stretch": {
        "level": "beginner",
        "minutes": 3,
        "avoid_for": ["osteoporosis", "neck_pain", "pregnancy", "diastasis_recti"],
        "modification": "Head down, legs in tabletop; tap one foot to the mat at a time.",
    },
    "Criss-Cross": {
        "level": "intermediate",
        "minutes": 3,
        "avoid_for": ["osteoporosis", "disc_herniation", "neck_pain", "pregnancy", "diastasis_recti"],
        "modification": "Head down; reach one hand toward the opposite knee.",
    },
    "Spine Stretch Forward": {
        "level": "beginner",
        "minutes": 3,
        "avoid_for": ["osteoporosis", "disc_herniation"],
        "modification": "Hinge forward from the hips with a long, flat back.",
    },
    "Swan Prep": {
        "level": "beginner",
        "minutes": 3,
        "avoid_for": ["pregnancy", "spondylolisthesis"],
        "modification": "Sit on a chair and lift the chest with the hands behind the head.",
    },
    "Swimming": {
        "level": "intermediate",
        "minutes": 3,
        "avoid_for": ["pregnancy", "shoulder_pain"],
        "modification": "Bird Dog: on hands and knees, reach the opposite arm and leg.",
    },
    "Side Kick Series": {
        "level": "beginner",
        "minutes": 5,
        "avoid_for": ["hip_replacement"],
        "modification": "Keep the top leg in line with the hip; don't swing it forward past 90 degrees.",
    },
    "Clam": {
        "level": "beginner",
        "minutes": 3,
        "avoid_for": [],
        "modification": "Rest the head on a pillow and make the movement smaller.",
    },
    "Bird Dog": {
        "level": "beginner",
        "minutes": 4,
        "avoid_for": ["wrist_pain", "knee_pain"],
        "modification": "Do it on the forearms with a cushion under the knees.",
    },
    "Front Plank": {
        "level": "intermediate",
        "minutes": 3,
        "avoid_for": ["wrist_pain", "shoulder_pain", "diastasis_recti", "high_blood_pressure"],
        "modification": "Incline plank with the hands on a bench or chair.",
    },
    "Teaser": {
        "level": "advanced",
        "minutes": 4,
        "avoid_for": ["osteoporosis", "disc_herniation", "neck_pain", "pregnancy", "diastasis_recti"],
        "modification": "One-leg teaser: keep one foot on the mat.",
    },
    "Rollover": {
        "level": "advanced",
        "minutes": 3,
        "avoid_for": ["osteoporosis", "disc_herniation", "neck_pain", "pregnancy", "high_blood_pressure"],
        "modification": "Do a neutral-spine bridge instead.",
    },
    "Mermaid": {
        "level": "beginner",
        "minutes": 3,
        "avoid_for": ["shoulder_pain"],
        "modification": "Keep the hand on the head instead of reaching it overhead.",
    },
    "Child's Pose": {
        "level": "beginner",
        "minutes": 3,
        "avoid_for": ["knee_pain"],
        "modification": "Lie on the back and hug one knee in at a time.",
    },
    "Standing Calf Raises": {
        "level": "beginner",
        "minutes": 3,
        "avoid_for": [],
        "modification": "Hold a wall or chair for balance.",
    },
}

# Words to look for in an FDA drug label -> what it means in a Pilates class.
MEDICATION_FLAGS = {
    "dizziness": "May feel dizzy changing positions. Rise slowly and pause seated before standing.",
    "bradycardia": "Heart rate may not rise with effort. Use the talk test instead of heart rate.",
    "hypoglycemia": "Ask when they last ate and keep a sugary snack nearby.",
    "tendon rupture": "Higher risk of tendon injury. Avoid jumping and sudden loading.",
    "osteoporosis": "Long-term use can thin bones. Avoid loaded spinal flexion like the Roll Up.",
    "bleeding": "Bruises easily. Avoid impact and take care with props.",
    "drowsiness": "Balance may be off. Keep standing work near a wall.",
    "myopathy": "Watch for unusual muscle pain or weakness.",
}
