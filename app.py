import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------

st.set_page_config(
    page_title="Responsible AI Practice Tracker",
    page_icon="🛡️",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #f4f6fb;
}

h1, h2, h3 {
    color: #1a2036;
}

.metric-card {
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# DATABASE SETUP
# ---------------------------------------------------

def get_connection():
    return sqlite3.connect("responsible_ai.db")


def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            use_case_name TEXT,
            category TEXT,
            transparency_score INTEGER,
            bias_score INTEGER,
            privacy_score INTEGER,
            accountability_score INTEGER,
            total_score INTEGER,
            risk_level TEXT,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------------------------------------------
# SCORE FUNCTIONS
# ---------------------------------------------------

SCORE_MAP = {
    "Yes": 2,
    "Partially": 1,
    "No": 0
}


def classify_risk(total_score):

    if total_score >= 6:
        return "Low Risk"

    elif total_score >= 3:
        return "Medium Risk"

    else:
        return "High Risk"


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("🛡️ Responsible AI")

menu = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📝 New Assessment",
        "📜 View History"
    ]
)


# ===================================================
# DASHBOARD
# ===================================================

if menu == "📊 Dashboard":

    st.title("🛡️ Responsible AI Practice Tracker")

    st.write(
        """
        Assess AI use cases against core responsible-AI principles —
        **Transparency, Bias & Fairness, Privacy, and Accountability** —
        and track how your projects measure up over time.
        """
    )

    st.divider()

    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM assessments",
        conn
    )

    conn.close()

    st.subheader("📊 Portfolio Overview")

    col1, col2, col3 = st.columns(3)

    # Total Assessments
    with col1:

        st.metric(
            "Total Use Cases Assessed",
            len(df)
        )

    # Average Score
    with col2:

        if len(df) > 0:

            avg_score = round(
                df["total_score"].mean(),
                1
            )

        else:

            avg_score = 0

        st.metric(
            "Average Responsible-AI Score",
            f"{avg_score} / 8"
        )

    # High Risk
    with col3:

        if len(df) > 0:

            high_risk_count = len(
                df[
                    df["risk_level"] == "High Risk"
                ]
            )

        else:

            high_risk_count = 0

        st.metric(
            "⚠️ High Risk Use Cases",
            high_risk_count
        )


    st.divider()


    # Charts

    if len(df) > 0:

        col1, col2 = st.columns(2)

        # Risk Distribution
        with col1:

            st.subheader("Risk Level Distribution")

            risk_counts = (
                df["risk_level"]
                .value_counts()
            )

            st.bar_chart(risk_counts)


        # Pillar Scores
        with col2:

            st.subheader("Average Score by Pillar")

            pillar_avgs = df[[
                "transparency_score",
                "bias_score",
                "privacy_score",
                "accountability_score"
            ]].mean()

            pillar_avgs.index = [
                "Transparency",
                "Bias & Fairness",
                "Privacy",
                "Accountability"
            ]

            st.bar_chart(pillar_avgs)


        # Recent Assessments

        st.divider()

        st.subheader("Recent Assessments")

        recent = df[[
            "date",
            "use_case_name",
            "category",
            "total_score",
            "risk_level"
        ]].tail(5)

        st.dataframe(
            recent,
            use_container_width=True
        )


    else:

        st.info(
            "ℹ️ No assessments logged yet. "
            "Add one under **New Assessment**."
        )


# ===================================================
# NEW ASSESSMENT
# ===================================================

elif menu == "📝 New Assessment":

    st.title("📝 Assess a New AI Use Case")

    st.write(
        "Evaluate your AI system using the four Responsible AI principles."
    )

    st.divider()


    with st.form("assessment_form"):

        # -------------------------------------------
        # BASIC INFORMATION
        # -------------------------------------------

        st.subheader("Basic Information")

        use_case_name = st.text_input(
            "AI Use Case Name",
            placeholder="Example: Resume Screening Tool"
        )

        category = st.selectbox(
            "Category",
            [
                "Hiring & HR",
                "Healthcare",
                "Customer Service",
                "Finance",
                "Education",
                "Other"
            ]
        )


        st.divider()


        # -------------------------------------------
        # TRANSPARENCY
        # -------------------------------------------

        st.subheader("👁️ Transparency")

        st.write(
            "Are decisions and limitations explained to users?"
        )

        transparency = st.radio(
            "Transparency Rating",
            ["Yes", "Partially", "No"],
            horizontal=True
        )


        # -------------------------------------------
        # BIAS
        # -------------------------------------------

        st.subheader("⚖️ Bias & Fairness")

        st.write(
            "Has the system been checked for biased outcomes across groups?"
        )

        bias = st.radio(
            "Bias & Fairness Rating",
            ["Yes", "Partially", "No"],
            horizontal=True
        )


        # -------------------------------------------
        # PRIVACY
        # -------------------------------------------

        st.subheader("🔒 Privacy & Data Protection")

        st.write(
            "Is personal data collected, stored, and used responsibly?"
        )

        privacy = st.radio(
            "Privacy Rating",
            ["Yes", "Partially", "No"],
            horizontal=True
        )


        # -------------------------------------------
        # ACCOUNTABILITY
        # -------------------------------------------

        st.subheader("📋 Accountability & Governance")

        st.write(
            "Is there a named owner and an escalation path for issues?"
        )

        accountability = st.radio(
            "Accountability Rating",
            ["Yes", "Partially", "No"],
            horizontal=True
        )


        # -------------------------------------------
        # NOTES
        # -------------------------------------------

        st.subheader("Notes")

        notes = st.text_area(
            "Notes / Follow-up Actions",
            placeholder="Add observations or follow-up actions..."
        )


        # SUBMIT

        submitted = st.form_submit_button(
            "💾 Save Assessment",
            use_container_width=True
        )


    # -----------------------------------------------
    # SAVE DATA
    # -----------------------------------------------

    if submitted:

        if not use_case_name.strip():

            st.error(
                "⚠️ Please enter an AI Use Case Name."
            )

        else:

            # Calculate Scores

            transparency_score = SCORE_MAP[transparency]

            bias_score = SCORE_MAP[bias]

            privacy_score = SCORE_MAP[privacy]

            accountability_score = SCORE_MAP[accountability]


            total_score = (
                transparency_score
                + bias_score
                + privacy_score
                + accountability_score
            )


            risk_level = classify_risk(total_score)


            date = datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )


            # Save to Database

            conn = get_connection()

            cursor = conn.cursor()


            cursor.execute("""

                INSERT INTO assessments (

                    date,
                    use_case_name,
                    category,
                    transparency_score,
                    bias_score,
                    privacy_score,
                    accountability_score,
                    total_score,
                    risk_level,
                    notes

                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            """, (

                date,
                use_case_name,
                category,
                transparency_score,
                bias_score,
                privacy_score,
                accountability_score,
                total_score,
                risk_level,
                notes

            ))


            conn.commit()

            conn.close()


            # Show Result

            st.success(
                "✅ Assessment Saved Successfully!"
            )


            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Responsible AI Score",
                    f"{total_score} / 8"
                )

            with col2:

                st.metric(
                    "Risk Level",
                    risk_level
                )


# ===================================================
# VIEW HISTORY
# ===================================================

elif menu == "📜 View History":

    st.title("📜 Assessment History")

    st.write(
        "View and manage all previously saved Responsible AI assessments."
    )

    st.divider()


    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM assessments ORDER BY id DESC",
        conn
    )

    conn.close()


    if len(df) == 0:

        st.info(
            "ℹ️ No assessment history available yet."
        )


    else:

        # Display Table

        display_df = df[[
            "id",
            "date",
            "use_case_name",
            "category",
            "total_score",
            "risk_level",
            "notes"
        ]]


        display_df.columns = [
            "ID",
            "Date",
            "Use Case",
            "Category",
            "Score",
            "Risk Level",
            "Notes"
        ]


        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


        st.divider()


        # DELETE SECTION

        st.subheader("🗑️ Delete an Assessment")


        assessment_ids = df["id"].tolist()


        selected_id = st.selectbox(
            "Select Assessment ID to Delete",
            assessment_ids
        )


        if st.button(
            "🗑️ Delete Selected Assessment"
        ):

            conn = get_connection()

            cursor = conn.cursor()


            cursor.execute(
                "DELETE FROM assessments WHERE id = ?",
                (selected_id,)
            )


            conn.commit()

            conn.close()


            st.success(
                f"Assessment ID {selected_id} deleted successfully!"
            )


            st.rerun()