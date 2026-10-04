import json

import streamlit as st
import pandas as pd
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("AQ.Ab8RN6LSetkie3c6tsXZ2UByRzHa2xUGETUu1QjORySOx-mDGg")

client = genai.Client(api_key=API_KEY)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="wide"
)
def evaluate_answer(question, answer):

    prompt = f"""
You are an expert interviewer evaluating a candidate
for a Business Analyst role.

Interview Question:
{question}

Candidate Answer:
{answer}

Evaluate the candidate's answer using the following five dimensions.

1. Correctness
2. Relevance
3. Completeness
4. Clarity
5. Technical or Business Understanding

Give each dimension a score from 0 to 10.

Scoring guidelines:

0-2 = Very poor
3-4 = Poor
5-6 = Average
7-8 = Good
9 = Very good
10 = Excellent

Also provide:
- Two specific strengths
- Two specific areas for improvement
- An ideal answer
- One practical recommendation

Return ONLY valid JSON.

Use exactly this structure:

{{
    "correctness": 0,
    "relevance": 0,
    "completeness": 0,
    "clarity": 0,
    "technical_business_understanding": 0,
    "strengths": [
        "strength 1",
        "strength 2"
    ],
    "improvements": [
        "improvement 1",
        "improvement 2"
    ],
    "ideal_answer": "ideal answer here",
    "recommendation": "practical recommendation here"
}}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    evaluation = json.loads(response.text)

    return evaluation

    prompt = f"""
You are an expert interviewer evaluating a candidate
for a Business Analyst role.

Interview Question:
{question}

Candidate Answer:
{answer}

Evaluate the candidate's answer based on:

1. Correctness
2. Relevance
3. Completeness
4. Clarity
5. Business or technical understanding

Provide the following:

- Score out of 10
- What the candidate did well
- What the candidate could improve
- Ideal answer
- One practical recommendation for the candidate

Keep the feedback professional, concise and constructive.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text

questions_df = pd.read_csv("questions.csv")


# --------------------------------------------------
# INITIALIZE SESSION STATE
# --------------------------------------------------

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "selected_questions" not in st.session_state:
    st.session_state.selected_questions = None

if "answers" not in st.session_state:
    st.session_state.answers = []


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🎯 AI Interview Coach")

st.subheader("Intelligent Interview Preparation & Assessment")

st.write(
    "Practice interview questions, receive AI-powered feedback, "
    "and analyze your performance."
)

st.divider()


# --------------------------------------------------
# INTERVIEW SETUP
# --------------------------------------------------

if not st.session_state.interview_started:

    st.header("Interview Setup")

    role = st.selectbox(
        "Select your role",
        [
            "Business Analyst",
            "Data Analyst",
            "Marketing Analyst",
            "Finance Analyst"
        ]
    )

    topic = st.selectbox(
        "Select topic",
        [
            "SQL",
            "Python",
            "Excel",
            "Power BI",
            "Statistics",
            "Case Study",
            "Business Strategy",
            "HR / Behavioral"
        ]
    )

    difficulty = st.selectbox(
        "Select difficulty",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

    number_of_questions = st.number_input(
        "Number of questions",
        min_value=1,
        max_value=10,
        value=5
    )

    st.divider()

    if st.button("🚀 Start Interview", type="primary"):

        # Filter questions according to user selection

        filtered_questions = questions_df[
            (questions_df["role"] == role) &
            (questions_df["topic"] == topic) &
            (questions_df["difficulty"] == difficulty)
        ]

        # Check whether questions exist

        if len(filtered_questions) == 0:

            st.error(
                "No questions are available for this combination "
                "of role, topic and difficulty."
            )

        else:

            # Limit number of questions to available questions

            number_of_questions = min(
                number_of_questions,
                len(filtered_questions)
            )

            # Select questions

            selected_questions = filtered_questions.head(
                number_of_questions
            ).reset_index(drop=True)

            # Save interview information

            st.session_state.selected_questions = selected_questions

            st.session_state.current_question = 0

            st.session_state.answers = []

            st.session_state.interview_started = True

            # Refresh application

            st.rerun()


# --------------------------------------------------
# INTERVIEW SECTION
# --------------------------------------------------

else:

    selected_questions = st.session_state.selected_questions

    current_question_index = st.session_state.current_question

    total_questions = len(selected_questions)


    # --------------------------------------------------
    # CHECK IF INTERVIEW IS COMPLETE
    # --------------------------------------------------

    if current_question_index >= total_questions:

        st.success("🎉 Interview Completed!")

        st.header("Interview Summary")

        st.write(
            f"You answered {total_questions} question(s)."
        )

        st.write("Your answers have been recorded.")

        st.divider()

        for i, answer in enumerate(st.session_state.answers):

            st.subheader(
                f"Question {i + 1}"
            )

            st.write(
                selected_questions.iloc[i]["question"]
            )

            st.write("**Your Answer:**")

            st.write(answer)

        st.divider()

        if st.button("🔄 Start New Interview"):

            st.session_state.interview_started = False

            st.session_state.current_question = 0

            st.session_state.selected_questions = None

            st.session_state.answers = []

            st.rerun()


    # --------------------------------------------------
    # DISPLAY CURRENT QUESTION
    # --------------------------------------------------

    else:

        question = selected_questions.iloc[
            current_question_index
        ]["question"]


        # Progress information

        st.progress(
            current_question_index / total_questions
        )

        st.caption(
            f"Question {current_question_index + 1} "
            f"of {total_questions}"
        )


        st.header(
            f"Question {current_question_index + 1}"
        )

        st.write(question)

        st.divider()


        # Answer box

        answer = st.text_area(
            "Your Answer",
            height=200,
            placeholder="Type your answer here..."
        )


       # Submit answer

if st.button(
    "Submit Answer ➡️",
    type="primary"
):

    if answer.strip() == "":

        st.warning(
            "Please enter an answer before continuing."
        )

    else:

        with st.spinner(
            "🤖 Gemini is evaluating your answer..."
        ):

            feedback = evaluate_answer(
                question,
                answer
            )

        st.subheader("🤖 AI Interviewer Feedback")

        st.write(feedback)

        st.divider()

        # Save answer

        st.session_state.answers.append(
            answer
        )

        # Continue button

        if st.button("Next Question ➡️"):

            st.session_state.current_question += 1

            st.rerun()