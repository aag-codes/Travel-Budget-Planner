# import streamlit as st
# import pandas as pd

# from trip_budget import TripBudget
# from budget_report import BudgetReport
# from holiday_ai import HolidayAI

# # --------------------------------------------------------------------------
# # Page config
# # --------------------------------------------------------------------------
# st.set_page_config(
#     page_title="Wayfare — Travel Budget Planner",
#     page_icon="🧭",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# # --------------------------------------------------------------------------
# # Styling
# # --------------------------------------------------------------------------
# st.markdown(
#     """
#     <style>
#     :root {
#         --ink: #1F2A28;
#         --paper: #FBF7F0;
#         --moss: #2F6F5E;
#         --moss-dark: #255A4C;
#         --terracotta: #C8693F;
#         --sand: #E8DFC9;
#         color-scheme: light;
#     }

#     /* Force light scheme regardless of the user's OS/browser theme,
#        so our colors below are never fought by Streamlit's dark defaults. */
#     .stApp {
#         background-color: var(--paper);
#         color: var(--ink);
#     }

#     /* Catch-all: every piece of text in the app defaults to dark ink
#        unless explicitly overridden below. */
#     .stApp, .stApp p, .stApp span, .stApp label, .stApp div,
#     .stApp li, .stApp td, .stApp th {
#         color: var(--ink);
#     }

#     h1, h2, h3, h4 {
#         color: var(--ink) !important;
#         font-family: "Georgia", "Iowan Old Style", serif;
#     }

#     /* Sidebar */
#     [data-testid="stSidebar"] {
#         background-color: #F1EBDD;
#         border-right: 1px solid var(--sand);
#     }
#     [data-testid="stSidebar"] * {
#         color: var(--ink) !important;
#     }

#     /* Text inputs, number inputs, selects, textareas */
#     .stTextInput input,
#     .stNumberInput input,
#     .stTextArea textarea {
#         background-color: #FFFFFF !important;
#         color: var(--ink) !important;
#         border: 1px solid var(--sand) !important;
#     }
#     .stSelectbox div[data-baseweb="select"] > div {
#         background-color: #FFFFFF !important;
#         color: var(--ink) !important;
#         border: 1px solid var(--sand) !important;
#     }
#     /* The dropdown menu that pops out of a selectbox */
#     div[data-baseweb="popover"] li,
#     div[data-baseweb="menu"] li {
#         color: var(--ink) !important;
#         background-color: #FFFFFF !important;
#     }
#     div[data-baseweb="popover"] li:hover,
#     div[data-baseweb="menu"] li:hover {
#         background-color: var(--sand) !important;
#     }

#     /* Placeholder text */
#     ::placeholder {
#         color: #8A8276 !important;
#         opacity: 1;
#     }

#     .wf-eyebrow {
#         text-transform: uppercase;
#         letter-spacing: 0.12em;
#         font-size: 0.75rem;
#         color: var(--moss) !important;
#         font-weight: 600;
#         margin-bottom: 0.2rem;
#     }

#     .wf-card {
#         background-color: #FFFFFF;
#         border: 1px solid var(--sand);
#         border-radius: 10px;
#         padding: 1.1rem 1.3rem;
#     }

#     .wf-divider {
#         border: none;
#         border-top: 1px solid var(--sand);
#         margin: 1.2rem 0;
#     }

#     div[data-testid="stMetric"] {
#         background-color: #FFFFFF;
#         border: 1px solid var(--sand);
#         border-radius: 10px;
#         padding: 0.8rem 1rem 0.6rem 1rem;
#     }
#     div[data-testid="stMetric"] * {
#         color: var(--ink) !important;
#     }

#     /* Buttons: regular buttons and form submit buttons */
#     .stButton > button,
#     .stFormSubmitButton > button,
#     .stDownloadButton > button {
#         background-color: var(--moss) !important;
#         color: #FFFFFF !important;
#         border: none !important;
#         border-radius: 6px !important;
#         font-weight: 600 !important;
#     }
#     .stButton > button:hover,
#     .stFormSubmitButton > button:hover,
#     .stDownloadButton > button:hover {
#         background-color: var(--moss-dark) !important;
#         color: #FFFFFF !important;
#     }
#     .stButton > button p,
#     .stFormSubmitButton > button p,
#     .stDownloadButton > button p {
#         color: #FFFFFF !important;
#     }

#     /* Tabs */
#     .stTabs [data-baseweb="tab"] {
#         font-weight: 600;
#         color: var(--ink) !important;
#     }
#     .stTabs [aria-selected="true"] {
#         color: var(--moss) !important;
#     }

#     /* Alerts: error / warning / success / info boxes need their own
#        readable text + background pairing, not inherited from .stApp */
#     div[data-testid="stAlert"] {
#         color: var(--ink) !important;
#     }
#     div[data-testid="stAlert"] p {
#         color: var(--ink) !important;
#     }

#     /* Dataframe / table text */
#     [data-testid="stDataFrame"] * {
#         color: var(--ink) !important;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# CATEGORIES = ["Accommodation", "Food", "Transport", "Activities", "Shopping", "Miscellaneous"]
# COMMON_CURRENCIES = ["USD", "EUR", "GBP", "NGN", "JPY", "CAD", "AUD", "ZAR", "INR", "CNY"]

# # --------------------------------------------------------------------------
# # Session state
# # --------------------------------------------------------------------------
# if "trip" not in st.session_state:
#     st.session_state.trip = None
# if "summary_cache" not in st.session_state:
#     st.session_state.summary_cache = None
# if "summary_stale" not in st.session_state:
#     st.session_state.summary_stale = True



# def mark_stale():
#     """Flag that the cached summary needs recomputing (avoids redundant API calls)."""
#     st.session_state.summary_stale = True


# def get_summary():
#     """Return a cached summary, recomputing only when expenses have changed."""
#     trip: TripBudget = st.session_state.trip
#     if st.session_state.summary_stale or st.session_state.summary_cache is None:
#         st.session_state.summary_cache = trip.summary()
#         st.session_state.summary_stale = False
#     return st.session_state.summary_cache


# # --------------------------------------------------------------------------
# # Setup screen (shown once, before a trip exists)
# # --------------------------------------------------------------------------
# def render_setup_screen():
#     st.markdown('<div class="wf-eyebrow">Wayfare</div>', unsafe_allow_html=True)
#     st.title("🧭 Plan your next trip's budget")
#     st.write(
#         "Set up your trip once — name, total budget, and base currency — "
#         "then track every expense against it as you go."
#     )

#     st.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)

#     with st.form("setup_form"):
#         col1, col2 = st.columns([2, 1])
#         with col1:
#             trip_name = st.text_input("Trip name", placeholder="e.g. Lisbon Summer 2026")
#         with col2:
#             base_currency = st.selectbox("Base currency", COMMON_CURRENCIES, index=0)

#         total_budget = st.number_input(
#             "Total budget", min_value=0.0, step=50.0, format="%.2f"
#         )

#         submitted = st.form_submit_button("Start planning →", use_container_width=True)

#         if submitted:
#             if not trip_name.strip():
#                 st.error("Please give your trip a name.")
#             elif total_budget <= 0:
#                 st.error("Total budget must be greater than zero.")
#             else:
#                 try:
#                     st.session_state.trip = TripBudget(
#                         trip_name=trip_name.strip(),
#                         total_budget=total_budget,
#                         base_currency=base_currency,
#                     )
#                     mark_stale()
#                     st.rerun()
#                 except ValueError as e:
#                     st.error(f"Couldn't start your trip: {e}")


# # --------------------------------------------------------------------------
# # Sidebar: add expense (always visible once a trip exists)
# # --------------------------------------------------------------------------
# def render_sidebar():
#     trip: TripBudget = st.session_state.trip

#     st.sidebar.markdown('<div class="wf-eyebrow">Current trip</div>', unsafe_allow_html=True)
#     st.sidebar.markdown(f"### {trip.trip_name}")
#     st.sidebar.caption(f"Base currency: {trip.base_currency}")

#     st.sidebar.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)
#     st.sidebar.subheader("➕ Add an expense")

#     with st.sidebar.form("expense_form", clear_on_submit=True):
#         description = st.text_input("Description", placeholder="e.g. Hotel deposit")
#         amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
#         currency = st.selectbox("Currency", COMMON_CURRENCIES, index=0)
#         category = st.selectbox("Category", CATEGORIES)

#         add_clicked = st.form_submit_button("Add expense", use_container_width=True)

#         if add_clicked:
#             if not description.strip():
#                 st.sidebar.error("Please add a short description.")
#             elif amount <= 0:
#                 st.sidebar.error("Amount must be greater than zero.")
#             else:
#                 trip.add_expense(description.strip(), amount, currency, category)
#                 mark_stale()
#                 st.sidebar.success(f"Added: {description.strip()}")
#                 st.rerun()

#     st.sidebar.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)
#     if st.sidebar.button("🔁 Start a new trip", use_container_width=True):
#         st.session_state.trip = None
#         st.session_state.summary_cache = None
#         st.session_state.summary_stale = True
#         st.rerun()


# # --------------------------------------------------------------------------
# # Tab 1: Overview
# # --------------------------------------------------------------------------
# def render_overview_tab():
#     trip: TripBudget = st.session_state.trip

#     if not trip.expenses:
#         st.info("No expenses logged yet. Add your first one from the sidebar.")
#         return

#     try:
#         summary = get_summary()
#     except Exception as e:
#         st.error(f"Couldn't calculate your budget summary: {e}")
#         return

#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("Total Budget", f"{summary['total_budget']:.2f} {summary['base_currency']}")
#     col2.metric("Total Spent", f"{summary['total_spent']:.2f} {summary['base_currency']}")
#     remaining = summary["remaining_budget"]
#     col3.metric(
#         "Remaining",
#         f"{remaining:.2f} {summary['base_currency']}",
#         delta=None if remaining >= 0 else "Over budget",
#         delta_color="inverse",
#     )
#     col4.metric("Expenses Logged", summary["number_of_expenses"])

#     if summary["total_budget"] > 0:
#         pct_used = min(summary["total_spent"] / summary["total_budget"], 1.0)
#         st.progress(pct_used, text=f"{pct_used * 100:.1f}% of budget used")
#         if remaining < 0:
#             st.warning(
#                 f"You're over budget by {abs(remaining):.2f} {summary['base_currency']}."
#             )

#     st.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)

#     left, right = st.columns([1, 1])

#     with left:
#         st.markdown('<div class="wf-eyebrow">Breakdown</div>', unsafe_allow_html=True)
#         st.subheader("Spending by category")
#         cat_data = summary["expenses_by_category"]
#         if cat_data:
#             cat_df = pd.DataFrame(
#                 {"Category": list(cat_data.keys()), "Amount": list(cat_data.values())}
#             ).set_index("Category")
#             st.bar_chart(cat_df, color="#C8693F")

#     with right:
#         st.markdown('<div class="wf-eyebrow">Log</div>', unsafe_allow_html=True)
#         st.subheader("All expenses")
#         expense_rows = [e.to_dict() for e in trip.expenses]
#         exp_df = pd.DataFrame(expense_rows)[["date", "description", "amount", "currency", "category"]]
#         exp_df.columns = ["Date", "Description", "Amount", "Currency", "Category"]
#         st.dataframe(exp_df, use_container_width=True, hide_index=True)


# # --------------------------------------------------------------------------
# # Tab 2: Report
# # --------------------------------------------------------------------------
# def render_report_tab():
#     trip: TripBudget = st.session_state.trip

#     if not trip.expenses:
#         st.info("Add some expenses first to generate a report.")
#         return

#     try:
#         report = BudgetReport(trip)
#         report_text = report.generate_report()
#     except Exception as e:
#         st.error(f"Couldn't generate the report: {e}")
#         return

#     st.markdown('<div class="wf-eyebrow">Export</div>', unsafe_allow_html=True)
#     st.subheader("Trip budget report")
#     st.text(report_text)

#     st.download_button(
#         "⬇ Download report (.txt)",
#         data=report_text,
#         file_name=f"{trip.trip_name.replace(' ', '_')}_budget_report.txt",
#         mime="text/plain",
#         use_container_width=True,
#     )


# def _is_transient_ai_error(error: Exception) -> bool:
#     """Heuristic check for temporary, retry-worthy API errors (overload, rate limit, timeout)."""
#     text = str(error).lower()
#     signals = ["503", "unavailable", "overloaded", "high demand", "429", "rate limit", "timeout", "deadline exceeded"]
#     return any(signal in text for signal in signals)


# def _show_ai_error(error: Exception, retry_key: str):
#     """Shows a friendly message for transient errors (with a retry button) or the raw error otherwise."""
#     if _is_transient_ai_error(error):
#         st.warning(
#             "Gemini is busy right now and couldn't respond. This is usually temporary — "
#             "wait a few seconds and try again."
#         )
#         st.button("🔁 Try again", key=retry_key)
#     else:
#         st.error(f"Couldn't fetch a response: {error}")


# # --------------------------------------------------------------------------
# # Tab 3: AI Travel Assistant
# # --------------------------------------------------------------------------
# def render_ai_tab():
#     trip: TripBudget = st.session_state.trip

#     st.markdown('<div class="wf-eyebrow">Powered by Gemini</div>', unsafe_allow_html=True)
#     st.subheader("AI travel assistant")
#     st.caption(
#         "Get quick advice for your destination based on the trip you've set up."
#     )

#     try:
#         ai = HolidayAI()
#     except ValueError as e:
#         st.warning(f"AI assistant unavailable: {e}")
#         st.caption("Add a GEMINI_API_KEY to your .env file to enable this tab.")
#         return

#     destination = st.text_input("Destination", placeholder="e.g. Lisbon, Portugal")

#     advice_tab, packing_tab, breakdown_tab = st.tabs(
#         ["✨ Travel Advice", "🎒 Packing List", "📊 Budget Breakdown"]
#     )

#     with advice_tab:
#         if st.button("Get travel advice", key="advice_btn"):
#             if not destination.strip():
#                 st.error("Enter a destination first.")
#             else:
#                 with st.spinner("Thinking about your trip..."):
#                     try:
#                         result = ai.get_travel_advice(
#                             destination.strip(), trip.total_budget, trip.base_currency
#                         )
#                         st.markdown(result)
#                     except Exception as e:
#                         _show_ai_error(e, retry_key="retry_advice")

#     with packing_tab:
#         duration = st.number_input("Trip length (days)", min_value=1, step=1, value=7)
#         if st.button("Get packing list", key="packing_btn"):
#             if not destination.strip():
#                 st.error("Enter a destination first.")
#             else:
#                 with st.spinner("Packing your bags..."):
#                     try:
#                         result = ai.get_packing_suggestions(destination.strip(), int(duration))
#                         st.markdown(result)
#                     except Exception as e:
#                         _show_ai_error(e, retry_key="retry_packing")

#     with breakdown_tab:
#         if st.button("Get budget breakdown advice", key="breakdown_btn"):
#             if not destination.strip():
#                 st.error("Enter a destination first.")
#             else:
#                 with st.spinner("Crunching the numbers..."):
#                     try:
#                         result = ai.get_budget_breakdown_advice(
#                             destination.strip(), trip.total_budget, trip.base_currency
#                         )
#                         st.markdown(result)
#                     except Exception as e:
#                         _show_ai_error(e, retry_key="retry_breakdown")


# # --------------------------------------------------------------------------
# # Main
# # --------------------------------------------------------------------------
# def main():
#     if st.session_state.trip is None:
#         render_setup_screen()
#         return

#     render_sidebar()

#     trip: TripBudget = st.session_state.trip
#     st.markdown('<div class="wf-eyebrow">Wayfare</div>', unsafe_allow_html=True)
#     st.title(f"🧭 {trip.trip_name}")

#     overview_tab, report_tab, ai_tab = st.tabs(
#         ["📊 Overview", "📄 Report", "✨ AI Assistant"]
#     )

#     with overview_tab:
#         render_overview_tab()
#     with report_tab:
#         render_report_tab()
#     with ai_tab:
#         render_ai_tab()


# if __name__ == "__main__":
#     main()

import streamlit as st
import pandas as pd

from trip_budget import TripBudget
from budget_report import BudgetReport
from holiday_ai import HolidayAI
from currency_converter import CurrencyConverter

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Wayfare — Travel Budget Planner",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --ink: #1F2A28;
        --paper: #FBF7F0;
        --moss: #2F6F5E;
        --moss-dark: #255A4C;
        --terracotta: #C8693F;
        --sand: #E8DFC9;
        color-scheme: light;
    }

    /* Force light scheme regardless of the user's OS/browser theme,
       so our colors below are never fought by Streamlit's dark defaults. */
    .stApp {
        background-color: var(--paper);
        color: var(--ink);
    }

    /* Catch-all: every piece of text in the app defaults to dark ink
       unless explicitly overridden below. */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div,
    .stApp li, .stApp td, .stApp th {
        color: var(--ink);
    }

    h1, h2, h3, h4 {
        color: var(--ink) !important;
        font-family: "Georgia", "Iowan Old Style", serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F1EBDD;
        border-right: 1px solid var(--sand);
    }
    [data-testid="stSidebar"] * {
        color: var(--ink) !important;
    }

    /* Text inputs, number inputs, selects, textareas */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: var(--ink) !important;
        border: 1px solid var(--sand) !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: var(--ink) !important;
        border: 1px solid var(--sand) !important;
    }
    /* The dropdown menu that pops out of a selectbox */
    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"] li {
        color: var(--ink) !important;
        background-color: #FFFFFF !important;
    }
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="menu"] li:hover {
        background-color: var(--sand) !important;
    }

    /* Placeholder text */
    ::placeholder {
        color: #8A8276 !important;
        opacity: 1;
    }

    .wf-eyebrow {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.75rem;
        color: var(--moss) !important;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }

    .wf-card {
        background-color: #FFFFFF;
        border: 1px solid var(--sand);
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
    }

    .wf-divider {
        border: none;
        border-top: 1px solid var(--sand);
        margin: 1.2rem 0;
    }

    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid var(--sand);
        border-radius: 10px;
        padding: 0.8rem 1rem 0.6rem 1rem;
    }
    div[data-testid="stMetric"] * {
        color: var(--ink) !important;
    }

    /* Buttons: regular buttons and form submit buttons */
    .stButton > button,
    .stFormSubmitButton > button,
    .stDownloadButton > button {
        background-color: var(--moss) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover,
    .stFormSubmitButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: var(--moss-dark) !important;
        color: #FFFFFF !important;
    }
    .stButton > button p,
    .stFormSubmitButton > button p,
    .stDownloadButton > button p {
        color: #FFFFFF !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: var(--ink) !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--moss) !important;
    }

    /* Alerts: error / warning / success / info boxes need their own
       readable text + background pairing, not inherited from .stApp */
    div[data-testid="stAlert"] {
        color: var(--ink) !important;
    }
    div[data-testid="stAlert"] p {
        color: var(--ink) !important;
    }

    /* Dataframe / table text */
    [data-testid="stDataFrame"] * {
        color: var(--ink) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

CATEGORIES = ["Accommodation", "Food", "Transport", "Activities", "Shopping", "Miscellaneous"]
COMMON_CURRENCIES = ["USD", "EUR", "GBP", "NGN", "JPY", "CAD", "AUD", "ZAR", "INR", "CNY"]

# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
if "trip" not in st.session_state:
    st.session_state.trip = None
if "trip_duration" not in st.session_state:
    st.session_state.trip_duration = 7
if "summary_cache" not in st.session_state:
    st.session_state.summary_cache = None
if "summary_stale" not in st.session_state:
    st.session_state.summary_stale = True


def mark_stale():
    """Flag that the cached summary needs recomputing (avoids redundant API calls)."""
    st.session_state.summary_stale = True


def get_summary():
    """Return a cached summary, recomputing only when expenses have changed."""
    trip: TripBudget = st.session_state.trip
    if st.session_state.summary_stale or st.session_state.summary_cache is None:
        st.session_state.summary_cache = trip.summary()
        st.session_state.summary_stale = False
    return st.session_state.summary_cache


# --------------------------------------------------------------------------
# Setup screen (shown once, before a trip exists)
# --------------------------------------------------------------------------
def render_setup_screen():
    st.markdown('<div class="wf-eyebrow">Wayfare</div>', unsafe_allow_html=True)
    st.title("🧭 Plan your next trip's budget")
    st.write(
        "Set up your trip once — name, total budget, base currency, and duration — "
        "then track every expense against it as you go."
    )

    st.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)

    with st.form("setup_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            trip_name = st.text_input("Trip name", placeholder="e.g. Lisbon Summer 2026")
        with col2:
            base_currency = st.selectbox("Base currency", COMMON_CURRENCIES, index=0)

        col3, col4 = st.columns([1, 1])
        with col3:
            total_budget = st.number_input(
                "Total budget", min_value=0.0, step=50.0, format="%.2f"
            )
        with col4:
            duration_days = st.number_input(
                "Trip duration (days)", min_value=1, step=1, value=7
            )

        submitted = st.form_submit_button("Start planning →", use_container_width=True)

        if submitted:
            if not trip_name.strip():
                st.error("Please give your trip a name.")
            elif total_budget <= 0:
                st.error("Total budget must be greater than zero.")
            else:
                try:
                    st.session_state.trip = TripBudget(
                        trip_name=trip_name.strip(),
                        total_budget=total_budget,
                        base_currency=base_currency,
                    )
                    st.session_state.trip_duration = int(duration_days)
                    mark_stale()
                    st.rerun()
                except ValueError as e:
                    st.error(f"Couldn't start your trip: {e}")

    st.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)
    render_currency_converter_section()


def render_currency_converter_section():
    """Standalone live currency converter, available before a trip is set up."""
    st.markdown('<div class="wf-eyebrow">Quick tool</div>', unsafe_allow_html=True)
    st.subheader("💱 Convert your currency")
    st.caption("Check what your money is worth at your destination before you plan your budget.")

    try:
        converter = CurrencyConverter()
    except ValueError as e:
        st.warning(f"Currency converter unavailable: {e}")
        st.caption("Add an EXCHANGE_RATE_API_KEY to your .env file to enable this tool.")
        return

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        amount = st.number_input(
            "Amount", min_value=0.0, step=10.0, format="%.2f", key="converter_amount"
        )
    with col2:
        from_currency = st.selectbox("From", COMMON_CURRENCIES, index=0, key="converter_from")
    with col3:
        to_currency = st.selectbox("To", COMMON_CURRENCIES, index=1, key="converter_to")

    if st.button("Convert", key="convert_btn", use_container_width=True):
        if amount <= 0:
            st.error("Enter an amount greater than zero.")
        elif from_currency == to_currency:
            st.info(f"{amount:.2f} {from_currency} is the same in {to_currency}.")
        else:
            with st.spinner("Fetching the latest rate..."):
                try:
                    result = converter.convert(amount, from_currency, to_currency)
                    st.success(
                        f"{result['original_amount']:.2f} {result['base_currency']} "
                        f"= **{result['converted_amount']:.2f} {result['target_currency']}** "
                        f"(rate: 1 {result['base_currency']} = {result['rate']:.4f} {result['target_currency']})"
                    )
                except Exception as e:
                    st.error(f"Couldn't fetch the exchange rate: {e}")


# --------------------------------------------------------------------------
# Sidebar: add expense (always visible once a trip exists)
# --------------------------------------------------------------------------
def render_sidebar():
    trip: TripBudget = st.session_state.trip

    st.sidebar.markdown('<div class="wf-eyebrow">Current trip</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f"### {trip.trip_name}")
    st.sidebar.caption(
        f"Base currency: {trip.base_currency} · "
        f"Duration: {st.session_state.trip_duration} day(s)"
    )

    st.sidebar.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)
    st.sidebar.subheader("➕ Add an expense")

    with st.sidebar.form("expense_form", clear_on_submit=True):
        description = st.text_input("Description", placeholder="e.g. Hotel deposit")
        amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
        currency = st.selectbox("Currency", COMMON_CURRENCIES, index=0)
        category = st.selectbox("Category", CATEGORIES)

        add_clicked = st.form_submit_button("Add expense", use_container_width=True)

        if add_clicked:
            if not description.strip():
                st.sidebar.error("Please add a short description.")
            elif amount <= 0:
                st.sidebar.error("Amount must be greater than zero.")
            else:
                trip.add_expense(description.strip(), amount, currency, category)
                mark_stale()
                st.sidebar.success(f"Added: {description.strip()}")
                st.rerun()

    st.sidebar.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)
    if st.sidebar.button("🔁 Start a new trip", use_container_width=True):
        st.session_state.trip = None
        st.session_state.trip_duration = 7
        st.session_state.summary_cache = None
        st.session_state.summary_stale = True
        st.rerun()


# --------------------------------------------------------------------------
# Tab 1: Overview
# --------------------------------------------------------------------------
def render_overview_tab():
    trip: TripBudget = st.session_state.trip

    if not trip.expenses:
        st.info("No expenses logged yet. Add your first one from the sidebar.")
        return

    try:
        summary = get_summary()
    except Exception as e:
        st.error(f"Couldn't calculate your budget summary: {e}")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Budget", f"{summary['total_budget']:.2f} {summary['base_currency']}")
    col2.metric("Total Spent", f"{summary['total_spent']:.2f} {summary['base_currency']}")
    remaining = summary["remaining_budget"]
    col3.metric(
        "Remaining",
        f"{remaining:.2f} {summary['base_currency']}",
        delta=None if remaining >= 0 else "Over budget",
        delta_color="inverse",
    )
    col4.metric("Expenses Logged", summary["number_of_expenses"])

    if summary["total_budget"] > 0:
        pct_used = min(summary["total_spent"] / summary["total_budget"], 1.0)
        st.progress(pct_used, text=f"{pct_used * 100:.1f}% of budget used")
        if remaining < 0:
            st.warning(
                f"You're over budget by {abs(remaining):.2f} {summary['base_currency']}."
            )

    st.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="wf-eyebrow">Breakdown</div>', unsafe_allow_html=True)
        st.subheader("Spending by category")
        cat_data = summary["expenses_by_category"]
        if cat_data:
            cat_df = pd.DataFrame(
                {"Category": list(cat_data.keys()), "Amount": list(cat_data.values())}
            ).set_index("Category")
            st.bar_chart(cat_df, color="#C8693F")

    with right:
        st.markdown('<div class="wf-eyebrow">Log</div>', unsafe_allow_html=True)
        st.subheader("All expenses")
        expense_rows = [e.to_dict() for e in trip.expenses]
        exp_df = pd.DataFrame(expense_rows)[["date", "description", "amount", "currency", "category"]]
        exp_df.columns = ["Date", "Description", "Amount", "Currency", "Category"]
        st.dataframe(exp_df, use_container_width=True, hide_index=True)


# --------------------------------------------------------------------------
# Tab 2: Report
# --------------------------------------------------------------------------
def render_report_tab():
    trip: TripBudget = st.session_state.trip

    if not trip.expenses:
        st.info("Add some expenses first to generate a report.")
        return

    try:
        report = BudgetReport(trip)
        report_text = report.generate_report()
    except Exception as e:
        st.error(f"Couldn't generate the report: {e}")
        return

    st.markdown('<div class="wf-eyebrow">Export</div>', unsafe_allow_html=True)
    st.subheader("Trip budget report")
    st.text(report_text)

    st.download_button(
        "⬇ Download report (.txt)",
        data=report_text,
        file_name=f"{trip.trip_name.replace(' ', '_')}_budget_report.txt",
        mime="text/plain",
        use_container_width=True,
    )


def _is_transient_ai_error(error: Exception) -> bool:
    """Heuristic check for temporary, retry-worthy API errors (overload, rate limit, timeout)."""
    text = str(error).lower()
    signals = ["503", "unavailable", "overloaded", "high demand", "429", "rate limit", "timeout", "deadline exceeded"]
    return any(signal in text for signal in signals)


def _show_ai_error(error: Exception, retry_key: str):
    """Shows a friendly message for transient errors (with a retry button) or the raw error otherwise."""
    if _is_transient_ai_error(error):
        st.warning(
            "Gemini is busy right now and couldn't respond. This is usually temporary — "
            "wait a few seconds and try again."
        )
        st.button("🔁 Try again", key=retry_key)
    else:
        st.error(f"Couldn't fetch a response: {error}")


# --------------------------------------------------------------------------
# Tab 3: AI Travel Assistant
# --------------------------------------------------------------------------
def render_ai_tab():
    trip: TripBudget = st.session_state.trip

    st.markdown('<div class="wf-eyebrow">Powered by Gemini</div>', unsafe_allow_html=True)
    st.subheader("AI travel assistant")
    st.caption(
        "Get quick advice for your destination based on the trip you've set up."
    )

    try:
        ai = HolidayAI()
    except ValueError as e:
        st.warning(f"AI assistant unavailable: {e}")
        st.caption("Add a GEMINI_API_KEY to your .env file to enable this tab.")
        return

    destination = st.text_input("Destination", placeholder="e.g. Lisbon, Portugal")

    advice_tab, packing_tab, breakdown_tab = st.tabs(
        ["✨ Travel Advice", "🎒 Packing List", "📊 Budget Breakdown"]
    )

    with advice_tab:
        if st.button("Get travel advice", key="advice_btn"):
            if not destination.strip():
                st.error("Enter a destination first.")
            else:
                with st.spinner("Thinking about your trip..."):
                    try:
                        result = ai.get_travel_advice(
                            destination.strip(), trip.total_budget, trip.base_currency
                        )
                        st.markdown(result)
                    except Exception as e:
                        _show_ai_error(e, retry_key="retry_advice")

    with packing_tab:
        duration = st.number_input(
            "Trip length (days)",
            min_value=1,
            step=1,
            value=st.session_state.trip_duration,
            key="ai_duration",
        )
        if st.button("Get packing list", key="packing_btn"):
            if not destination.strip():
                st.error("Enter a destination first.")
            else:
                with st.spinner("Packing your bags..."):
                    try:
                        result = ai.get_packing_suggestions(destination.strip(), int(duration))
                        st.markdown(result)
                    except Exception as e:
                        _show_ai_error(e, retry_key="retry_packing")

    with breakdown_tab:
        if st.button("Get budget breakdown advice", key="breakdown_btn"):
            if not destination.strip():
                st.error("Enter a destination first.")
            else:
                with st.spinner("Crunching the numbers..."):
                    try:
                        result = ai.get_budget_breakdown_advice(
                            destination.strip(), trip.total_budget, trip.base_currency
                        )
                        st.markdown(result)
                    except Exception as e:
                        _show_ai_error(e, retry_key="retry_breakdown")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    if st.session_state.trip is None:
        render_setup_screen()
        return

    render_sidebar()

    trip: TripBudget = st.session_state.trip
    st.markdown('<div class="wf-eyebrow">Wayfare</div>', unsafe_allow_html=True)
    st.title(f"🧭 {trip.trip_name}")

    overview_tab, report_tab, ai_tab = st.tabs(
        ["📊 Overview", "📄 Report", "✨ AI Assistant"]
    )

    with overview_tab:
        render_overview_tab()
    with report_tab:
        render_report_tab()
    with ai_tab:
        render_ai_tab()


if __name__ == "__main__":
    main()