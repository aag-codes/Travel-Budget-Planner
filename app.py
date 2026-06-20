import re

import streamlit as st
import pandas as pd
from datetime import date

from trip_budget import TripBudget, TripComparison
from budget_report import BudgetReport
from holiday_ai import HolidayAI
from holiday_checker import HolidayChecker
from currency_converter import CurrencyConverter
from exceptions import WayfareError
from validators import extract_price_from_text, extract_currency_code_from_text, PRICE_PATTERN

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
if "destination_currency" not in st.session_state:
    st.session_state.destination_currency = COMMON_CURRENCIES[1]
if "quick_add_version" not in st.session_state:
    st.session_state.quick_add_version = 0

# Backing state for the sidebar "Add an expense" form fields. Keeping these
# as named keys (rather than letting the widgets manage their own state)
# is what lets the quick-add free-text parser below pre-fill the form.
# Backing state for the sidebar "Add an expense" form fields. The fields use
# versioned keys (exp_description_<v>, exp_amount_<v>, ...) rather than fixed
# ones: Streamlit forbids writing to st.session_state[key] for a widget that
# has already been instantiated in the current run, so to both (a) let the
# quick-add parser pre-fill the form, and (b) clear the form after a
# successful submit, each "reset" bumps this version, which gives the
# widgets brand-new (and therefore blank/default) keys on the next rerun.
st.session_state.setdefault("expense_form_version", 0)


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


@st.cache_data(ttl=300, show_spinner=False)
def _cached_exchange_rate(base_currency: str, target_currency: str) -> float:
    """
    Looks up the exchange rate for a currency pair, cached for 5 minutes.
    Caching by currency pair (not by amount) means the live setup-screen
    conversion can recompute on every keystroke locally - amount * rate -
    without firing a fresh API call each time the budget field changes.
    """
    converter = CurrencyConverter()
    return converter.get_exchange_rate(base_currency, target_currency)


# --------------------------------------------------------------------------
# Setup screen (shown once, before a trip exists)
# --------------------------------------------------------------------------
def render_setup_screen():
    st.markdown('<div class="wf-eyebrow">Wayfare</div>', unsafe_allow_html=True)
    st.title("🧭 Plan your next trip's budget")
    st.write(
        "Set up your trip once — name, home currency, destination currency, "
        "total budget, and duration — then track every expense against it as you go."
    )

    st.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)

    # These live outside an st.form on purpose: a form only updates its
    # values (and reruns the script) when the submit button is pressed, but
    # we want the destination-currency preview below to update live as the
    # amount/currencies change, with no separate "Convert" button needed.
    col1, col2 = st.columns([2, 1])
    with col1:
        trip_name = st.text_input(
            "Trip name", placeholder="e.g. Lisbon Summer 2026", key="setup_trip_name"
        )
    with col2:
        duration_days = st.number_input(
            "Trip duration (days)", min_value=1, step=1, value=7, key="setup_duration_days"
        )

    col3, col4 = st.columns([1, 1])
    with col3:
        home_currency = st.selectbox(
            "Home currency", COMMON_CURRENCIES, index=0, key="setup_home_currency"
        )
    with col4:
        destination_currency = st.selectbox(
            "Destination currency", COMMON_CURRENCIES, index=1, key="setup_destination_currency"
        )

    total_budget = st.number_input(
        "Total budget (in your home currency)",
        min_value=0.0, step=50.0, format="%.2f", key="setup_total_budget",
    )

    # Live preview: what the budget is worth at the destination, recomputed
    # automatically on every change above - no "Convert" button to click.
    if home_currency == destination_currency:
        st.caption("Home and destination currency are the same, so no conversion is needed.")
    elif total_budget > 0:
        try:
            rate = _cached_exchange_rate(home_currency, destination_currency)
        except WayfareError as e:
            st.caption(f"Live conversion unavailable right now: {e}")
        except ValueError as e:
            st.caption(f"Live conversion unavailable right now: {e}")
        else:
            converted = round(total_budget * rate, 2)
            st.markdown(
                f"💱 **{total_budget:,.2f} {home_currency} ≈ {converted:,.2f} {destination_currency}** "
                f"at your destination &nbsp;<span style='color:#8A8276;font-size:0.85em;'>"
                f"(1 {home_currency} = {rate:.4f} {destination_currency})</span>",
                unsafe_allow_html=True,
            )
    else:
        st.caption("Enter a budget above to see what it's worth at your destination.")

    st.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)

    if st.button("Start planning →", use_container_width=True):
        if not trip_name.strip():
            st.error("Please give your trip a name.")
        elif total_budget <= 0:
            st.error("Total budget must be greater than zero.")
        else:
            try:
                st.session_state.trip = TripBudget(
                    trip_name=trip_name.strip(),
                    total_budget=total_budget,
                    base_currency=home_currency,
                    duration_days=int(duration_days),
                )
                st.session_state.trip_duration = int(duration_days)
                st.session_state.destination_currency = destination_currency
                mark_stale()
                st.rerun()
            except WayfareError as e:
                st.error(f"Couldn't start your trip: {e}")
            except ValueError as e:
                st.error(f"Couldn't start your trip: {e}")


# --------------------------------------------------------------------------
# Sidebar: add expense (always visible once a trip exists)
# --------------------------------------------------------------------------
def render_sidebar():
    trip: TripBudget = st.session_state.trip

    st.sidebar.markdown('<div class="wf-eyebrow">Current trip</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f"### {trip.trip_name}")
    st.sidebar.caption(
        f"Home currency: {trip.base_currency} → "
        f"Destination: {st.session_state.destination_currency} · "
        f"Duration: {st.session_state.trip_duration} day(s)"
    )

    st.sidebar.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)
    st.sidebar.subheader("⚡ Quick add")
    st.sidebar.caption(
        "Type an expense naturally and we'll pull out the amount and currency "
        "for you — e.g. \"1,200 NGN hotel deposit\" or \"about 45.50 USD lunch\"."
    )

    # The expense form fields below use a versioned key suffix (exp_amount_0,
    # exp_amount_1, ...). Streamlit forbids writing to st.session_state[key]
    # for a widget that's already rendered in the current script run, so the
    # only way to either pre-fill the form (from quick add) or clear it
    # (after a successful submit) is to bump this version and let the next
    # rerun create fresh widgets under new, currently-unset keys.
    form_version = st.session_state.expense_form_version

    quick_text = st.sidebar.text_input(
        "Quick add",
        placeholder="e.g. 1,200 NGN hotel deposit",
        key=f"quick_add_text_{st.session_state.quick_add_version}",
        label_visibility="collapsed",
    )
    if st.sidebar.button("✨ Parse into form", key="quick_add_btn", use_container_width=True):
        if not quick_text.strip():
            st.sidebar.warning("Type something first, e.g. '45.50 USD lunch'.")
        else:
            price = extract_price_from_text(quick_text)
            currency_code = extract_currency_code_from_text(quick_text, known_codes=COMMON_CURRENCIES)

            if price is None and currency_code is None:
                st.sidebar.warning(
                    "Couldn't find an amount or a known currency code in that "
                    "text — try the form below instead."
                )
            else:
                # These exp_*_<form_version> keys haven't been instantiated
                # yet this run (the form widgets are created further below),
                # so writing to them here is allowed.
                if price is not None:
                    st.session_state[f"exp_amount_{form_version}"] = price
                if currency_code is not None:
                    st.session_state[f"exp_currency_{form_version}"] = currency_code

                # Strip the matched price/currency tokens out of the text to
                # leave a clean description guess for the description field.
                desc_guess = PRICE_PATTERN.sub("", quick_text)
                if currency_code is not None:
                    desc_guess = re.sub(rf"\b{currency_code}\b", "", desc_guess, flags=re.IGNORECASE)
                desc_guess = re.sub(r"\s{2,}", " ", desc_guess).strip(" ,.-")
                st.session_state[f"exp_description_{form_version}"] = desc_guess or quick_text.strip()

                st.session_state.quick_add_version += 1
                st.sidebar.success("Parsed — review and confirm below.")
                st.rerun()

    st.sidebar.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)
    st.sidebar.subheader("➕ Add an expense")

    with st.sidebar.form("expense_form", clear_on_submit=False):
        description = st.text_input(
            "Description", placeholder="e.g. Hotel deposit", key=f"exp_description_{form_version}"
        )
        amount = st.number_input(
            "Amount", min_value=0.0, step=1.0, format="%.2f", key=f"exp_amount_{form_version}"
        )
        currency = st.selectbox("Currency", COMMON_CURRENCIES, key=f"exp_currency_{form_version}")
        category = st.selectbox("Category", CATEGORIES, key=f"exp_category_{form_version}")

        add_clicked = st.form_submit_button("Add expense", use_container_width=True)

        if add_clicked:
            if not description.strip():
                st.sidebar.error("Please add a short description.")
            elif amount <= 0:
                st.sidebar.error("Amount must be greater than zero.")
            else:
                try:
                    trip.add_expense(description.strip(), amount, currency, category)
                    mark_stale()
                    st.sidebar.success(f"Added: {description.strip()}")
                    # Bump the version instead of resetting these keys
                    # directly - the widgets above already rendered with
                    # the current version's keys this run, so writing to
                    # them now would raise a StreamlitAPIException.
                    st.session_state.expense_form_version += 1
                    st.rerun()
                except WayfareError as e:
                    st.sidebar.error(f"Couldn't add expense: {e}")

    st.sidebar.markdown("<hr class='wf-divider'>", unsafe_allow_html=True)
    if st.sidebar.button("🔁 Start a new trip", use_container_width=True):
        st.session_state.trip = None
        st.session_state.trip_duration = 7
        st.session_state.destination_currency = COMMON_CURRENCIES[1]
        st.session_state.quick_add_version = 0
        st.session_state.expense_form_version = 0
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

    st.markdown('<div class="wf-eyebrow">Pacing</div>', unsafe_allow_html=True)
    st.subheader("Daily spending limit")
    daily_status = summary["daily_spending_status"]

    dcol1, dcol2, dcol3 = st.columns(3)
    dcol1.metric("Planned Daily Limit", f"{summary['daily_limit']:.2f} {summary['base_currency']}/day")
    dcol2.metric("Average So Far", f"{daily_status['avg_daily_spend']:.2f} {summary['base_currency']}/day")
    dcol3.metric(
        "Suggested for Remaining Days",
        f"{daily_status['suggested_remaining_daily_budget']:.2f} {summary['base_currency']}/day",
    )

    if daily_status["days_elapsed"] > 0:
        if daily_status["is_over_daily_pace"]:
            st.warning(
                f"You're averaging {daily_status['avg_daily_spend']:.2f} {summary['base_currency']}/day, "
                f"above your {summary['daily_limit']:.2f}/day plan. "
                f"You have {daily_status['days_remaining']} day(s) left — "
                f"aim for {daily_status['suggested_remaining_daily_budget']:.2f} {summary['base_currency']}/day from here to recover."
            )
        else:
            st.success(
                f"You're on pace — averaging {daily_status['avg_daily_spend']:.2f} {summary['base_currency']}/day "
                f"against a {summary['daily_limit']:.2f}/day plan."
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

    safe_name = trip.trip_name.replace(" ", "_")

    dl1, dl2, dl3 = st.columns(3)
    with dl1:
        st.download_button(
            "⬇ Download report (.txt)",
            data=report_text,
            file_name=f"{safe_name}_budget_report.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with dl2:
        st.download_button(
            "⬇ Download report (.json)",
            data=report.to_json(),
            file_name=f"{safe_name}_budget_report.json",
            mime="application/json",
            use_container_width=True,
        )
    with dl3:
        st.download_button(
            "⬇ Download expenses (.csv)",
            data=report.to_csv(),
            file_name=f"{safe_name}_expenses.csv",
            mime="text/csv",
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
# --------------------------------------------------------------------------
# Tab 4: Compare two destinations
# --------------------------------------------------------------------------
def render_compare_tab():
    st.markdown('<div class="wf-eyebrow">Decide between two trips</div>', unsafe_allow_html=True)
    st.subheader("⚖️ Compare destinations")
    st.caption(
        "Enter your best estimate of the total cost for each destination, in whatever "
        "currency you have a number for — we'll convert both to a common currency to compare."
    )

    with st.form("compare_form"):
        comparison_currency = st.selectbox(
            "Compare costs in", COMMON_CURRENCIES, index=0, key="compare_currency"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Destination A**")
            name_a = st.text_input("Name", placeholder="e.g. Lisbon", key="compare_name_a")
            cost_a = st.number_input(
                "Estimated total cost", min_value=0.0, step=50.0, format="%.2f", key="compare_cost_a"
            )
            currency_a = st.selectbox("Currency", COMMON_CURRENCIES, index=0, key="compare_currency_a")
        with col_b:
            st.markdown("**Destination B**")
            name_b = st.text_input("Name", placeholder="e.g. Bangkok", key="compare_name_b")
            cost_b = st.number_input(
                "Estimated total cost", min_value=0.0, step=50.0, format="%.2f", key="compare_cost_b"
            )
            currency_b = st.selectbox("Currency", COMMON_CURRENCIES, index=1, key="compare_currency_b")

        compare_clicked = st.form_submit_button("Compare", use_container_width=True)

    if compare_clicked:
        if not name_a.strip() or not name_b.strip():
            st.error("Please name both destinations.")
        elif cost_a <= 0 or cost_b <= 0:
            st.error("Both estimated costs must be greater than zero.")
        else:
            with st.spinner("Converting and comparing..."):
                try:
                    comparison = TripComparison(comparison_currency)
                    result = comparison.compare(
                        name_a.strip(), cost_a, currency_a,
                        name_b.strip(), cost_b, currency_b,
                    )
                except WayfareError as e:
                    st.error(f"Couldn't compare these destinations: {e}")
                except Exception as e:
                    st.error(f"Couldn't compare these destinations: {e}")
                else:
                    opt_a, opt_b = result["option_a"], result["option_b"]
                    ccol1, ccol2 = st.columns(2)
                    ccol1.metric(
                        opt_a["name"],
                        f"{opt_a['converted_amount']:.2f} {result['comparison_currency']}",
                        help=f"Original: {opt_a['original_amount']:.2f} {opt_a['original_currency']}",
                    )
                    ccol2.metric(
                        opt_b["name"],
                        f"{opt_b['converted_amount']:.2f} {result['comparison_currency']}",
                        help=f"Original: {opt_b['original_amount']:.2f} {opt_b['original_currency']}",
                    )

                    if result["cheaper_option"]:
                        st.success(
                            f"**{result['cheaper_option']}** is cheaper by "
                            f"{result['difference']:.2f} {result['comparison_currency']}."
                        )
                    else:
                        st.info("Both destinations cost the same once converted.")


# --------------------------------------------------------------------------
# Tab 5: Public holiday check
# --------------------------------------------------------------------------
def render_holidays_tab():
    st.markdown('<div class="wf-eyebrow">Plan around holidays</div>', unsafe_allow_html=True)
    st.subheader("📅 Public holiday check")
    st.caption(
        "Check whether your travel dates fall on a public holiday at your destination — "
        "useful for knowing if banks, offices, or attractions might be closed."
    )

    checker = HolidayChecker()

    with st.form("holiday_form"):
        col1, col2 = st.columns([1, 1])
        with col1:
            country_code = st.text_input(
                "Destination country code (2 letters)",
                placeholder="e.g. US, GB, NG, FR",
                key="holiday_country",
            ).strip().upper()
        with col2:
            start = st.date_input("Trip start date", value=date.today(), key="holiday_start")

        duration = st.number_input(
            "Trip duration (days)",
            min_value=1,
            step=1,
            value=st.session_state.trip_duration,
            key="holiday_duration",
        )

        check_clicked = st.form_submit_button("Check for holidays", use_container_width=True)

    if check_clicked:
        if not country_code:
            st.error("Enter a destination country code.")
        elif len(country_code) != 2 or not country_code.isalpha():
            st.error("Country code must be exactly 2 letters, e.g. US, GB, NG.")
        else:
            with st.spinner("Checking the holiday calendar..."):
                try:
                    holidays = checker.check_trip_dates(start, int(duration), country_code)
                except WayfareError as e:
                    st.error(f"Couldn't check holidays: {e}")
                except ValueError as e:
                    st.error(f"Couldn't check holidays: {e}")
                else:
                    if not holidays:
                        st.success(
                            f"No public holidays in {country_code} during your trip "
                            f"({start} for {int(duration)} day(s)). 🎉"
                        )
                    else:
                        st.warning(
                            f"Your trip overlaps with {len(holidays)} public holiday(s) in {country_code}:"
                        )
                        for h in holidays:
                            label = h.get("localName") or h.get("name") or "Public holiday"
                            st.markdown(f"- **{h['date']}** — {label}")
                        st.caption(
                            "Banks, government offices, and some businesses may be closed on these dates."
                        )


def main():
    if st.session_state.trip is None:
        render_setup_screen()
        return

    render_sidebar()

    trip: TripBudget = st.session_state.trip
    st.markdown('<div class="wf-eyebrow">Wayfare</div>', unsafe_allow_html=True)
    st.title(f"🧭 {trip.trip_name}")

    overview_tab, report_tab, ai_tab, compare_tab, holidays_tab = st.tabs(
        ["📊 Overview", "📄 Report", "✨ AI Assistant", "⚖️ Compare", "📅 Holidays"]
    )

    with overview_tab:
        render_overview_tab()
    with report_tab:
        render_report_tab()
    with ai_tab:
        render_ai_tab()
    with compare_tab:
        render_compare_tab()
    with holidays_tab:
        render_holidays_tab()


if __name__ == "__main__":
    main()