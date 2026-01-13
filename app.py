"""
GreenTrust AI - Streamlit Dashboard (Hybrid Mode)
Tries live API first, falls back to demo mode if quota exceeded.
"""

import streamlit as st
import plotly.graph_objects as go
from pathlib import Path
import json
import sys
from datetime import datetime
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents import create_audit_workflow, AuditState
from agents.state import ExtractionResult, VerificationResult, ComplianceResult, ReasoningStep
from knowledge_base.logistics_api import logistics_api

# Page configuration
st.set_page_config(
    page_title="GreenTrust AI - ESG Auditor",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E7D32;
    }
    .warning-box {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #F57C00;
    }
    .error-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #C62828;
    }
</style>
""", unsafe_allow_html=True)


def create_trust_score_gauge(score: float, brsr_aligned: bool):
    """Create a Plotly gauge chart for Trust Score."""
    
    if score >= 80:
        color = "#2E7D32"
    elif score >= 60:
        color = "#F57C00"
    else:
        color = "#C62828"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Trust Score", 'font': {'size': 24}},
        delta={'reference': 60, 'increasing': {'color': "#2E7D32"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 60], 'color': '#FFEBEE'},
                {'range': [60, 80], 'color': '#FFF3E0'},
                {'range': [80, 100], 'color': '#E8F5E9'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 60
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="white",
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig


def display_thinking_process(reasoning_history):
    """Display agent thinking process."""
    
    st.markdown("### 🧠 Agent Thinking Process")
    
    for i, step in enumerate(reasoning_history, 1):
        agent_emoji = {
            "extraction": "📄",
            "verification": "🔍",
            "compliance": "✅",
            "human_review": "👤"
        }.get(step.agent, "🤖")
        
        result_color = {
            "SUCCESS": "🟢",
            "ACCEPTABLE": "🟢",
            "FLAGGED": "🟡",
            "PENDING_REVIEW": "🟡",
            "APPROVE": "🟢",
            "REJECT": "🔴",
            "ERROR": "🔴",
            "FAILED": "🔴",
            "FALLBACK_ACTIVATED": "🟡"
        }.get(step.result, "⚪")
        
        with st.expander(f"{agent_emoji} **Step {i}: [{step.agent.upper()}]** {step.action} {result_color}", expanded=(i <= 3)):
            st.markdown(f"**Reasoning:** {step.reasoning}")
            if step.result:
                st.markdown(f"**Result:** `{step.result}`")
            st.caption(f"Timestamp: {step.timestamp.strftime('%H:%M:%S')}")


def run_live_audit(pdf_path: str):
    """Run audit with live API (with fallback to regex if quota exceeded)."""
    
    document_id = Path(pdf_path).stem
    initial_state = AuditState(
        pdf_path=pdf_path,
        document_id=document_id
    )
    
    workflow = create_audit_workflow()
    
    try:
        result = workflow.invoke(initial_state)
        
        # Convert dict to AuditState if needed
        if isinstance(result, dict):
            final_state = AuditState(**result)
        else:
            final_state = result
        
        return final_state, True  # Success
        
    except Exception as e:
        st.error(f"Workflow error: {str(e)}")
        return None, False


def main():
    """Main Streamlit app."""
    
    # Header
    st.markdown('<div class="main-header">🌱 GreenTrust AI</div>', unsafe_allow_html=True)
    
    # Check if API key is configured
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key and len(api_key) > 20:
        st.markdown('<div class="sub-header">Autonomous Multi-Agent ESG Scope 3 Auditor (Live Mode with Fallback)</div>', unsafe_allow_html=True)
        mode = "live"
    else:
        st.markdown('<div class="sub-header">Autonomous Multi-Agent ESG Scope 3 Auditor (Demo Mode)</div>', unsafe_allow_html=True)
        mode = "demo"
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 About")
        st.info(f"""
        **GreenTrust AI** uses multi-agent AI to audit carbon emission claims.
        
        **Agents:**
        - 📄 Extraction Agent (with regex fallback)
        - 🔍 Verification Agent
        - ✅ Compliance Agent
        - 👤 Human Review
        
        **Mode**: {'🔴 Live API' if mode == 'live' else '🟡 Demo'}
        """)
        
        st.markdown("---")
        st.markdown("### 📁 Sample Invoices")
        
        sample_files = [
            "valid_invoice.pdf",
            "suspicious_invoice.pdf",
            "edge_case_missing_date.pdf",
            "edge_case_eur_currency.pdf",
            "edge_case_high_risk_region.pdf",
            "edge_case_multimodal.pdf",
            "edge_case_zero_emissions.pdf"
        ]
        
        selected_sample = st.selectbox("Select invoice:", sample_files)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 Upload or Select Invoice")
        
        # Upload option
        uploaded_file = st.file_uploader(
            "Upload your own PDF invoice",
            type=['pdf'],
            help="Upload a logistics invoice with carbon emission data"
        )
        
        # Determine which file to use
        if uploaded_file:
            # Save uploaded file temporarily
            pdf_path = f"temp_{uploaded_file.name}"
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ Uploaded: {uploaded_file.name}")
        else:
            # Use selected sample
            pdf_path = f"data_samples/{selected_sample}"
            st.info(f"📁 Using sample: {selected_sample}")
        
        if st.button("🚀 Run Audit", type="primary"):
            with st.spinner("Running audit..."):
                final_state, success = run_live_audit(pdf_path)
                
                if success and final_state:
                    st.session_state['audit_result'] = final_state
                    st.session_state['mode_used'] = "live"
                    st.rerun()
                else:
                    st.error("Audit failed. Check logs for details.")
    
    with col2:
        st.markdown("### 📋 Quick Stats")
        if 'audit_result' in st.session_state:
            state = st.session_state['audit_result']
            
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                if state.extraction and state.extraction.co2e_claimed:
                    st.metric("CO2e Claimed", f"{state.extraction.co2e_claimed:.1f} kg")
                else:
                    st.metric("CO2e Claimed", "N/A")
            
            with metric_col2:
                if state.verification and state.verification.benchmark_co2e:
                    st.metric("Benchmark", f"{state.verification.benchmark_co2e:.1f} kg")
                else:
                    st.metric("Benchmark", "N/A")
            
            with metric_col3:
                if state.verification and state.verification.deviation_percent is not None:
                    deviation = state.verification.deviation_percent
                    st.metric("Deviation", f"{deviation:.1f}%", delta=f"{deviation:.1f}%", delta_color="inverse")
                else:
                    st.metric("Deviation", "N/A")
        else:
            st.info("👆 Select an invoice and click 'Run Audit'")
    
    # Results section
    if 'audit_result' in st.session_state:
        state = st.session_state['audit_result']
        
        st.markdown("---")
        
        # Show mode used
        if st.session_state.get('mode_used') == 'live':
            st.success("✅ Audit completed using Live API with intelligent fallback")
        
        # Trust Score Gauge
        if state.compliance:
            col_gauge, col_details = st.columns([1, 1])
            
            with col_gauge:
                fig = create_trust_score_gauge(
                    state.compliance.trust_score,
                    state.compliance.brsr_aligned
                )
                st.plotly_chart(fig, width='stretch')
                
                if state.compliance.brsr_aligned:
                    st.markdown('<div class="success-box">✅ <b>SEBI BRSR Aligned</b></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-box">❌ <b>Not SEBI BRSR Aligned</b></div>', unsafe_allow_html=True)
            
            with col_details:
                st.markdown("### 📊 Compliance Details")
                
                if state.requires_human_review:
                    st.markdown(f'<div class="warning-box">⚠️ <b>Human Review Required</b><br>{state.human_review_reason}</div>', unsafe_allow_html=True)
                    if state.human_review_decision:
                        st.info(f"Decision: **{state.human_review_decision.upper()}**")
                
                st.markdown("**Recommendations:**")
                for rec in state.compliance.recommendations:
                    st.markdown(f"- {rec}")
        
        st.markdown("---")
        
        # Thinking process
        if state.reasoning_history:
            display_thinking_process(state.reasoning_history)
        
        st.markdown("---")
        
        # Export
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            export_data = {
                "document_id": state.document_id,
                "audit_date": state.audit_date.isoformat(),
                "workflow_status": state.workflow_status,
                "extraction": state.extraction.model_dump() if state.extraction else None,
                "verification": state.verification.model_dump() if state.verification else None,
                "compliance": state.compliance.model_dump() if state.compliance else None,
                "reasoning_history": [
                    {
                        "agent": step.agent,
                        "timestamp": step.timestamp.isoformat(),
                        "action": step.action,
                        "reasoning": step.reasoning,
                        "result": step.result
                    }
                    for step in state.reasoning_history
                ],
                "human_review": {
                    "required": state.requires_human_review,
                    "reason": state.human_review_reason,
                    "completed": state.human_review_completed,
                    "decision": state.human_review_decision
                }
            }
            
            st.download_button(
                label="📥 Download Audit Report (JSON)",
                data=json.dumps(export_data, indent=2),
                file_name=f"{state.document_id}_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col_export2:
            if st.button("🔄 New Audit"):
                del st.session_state['audit_result']
                if 'mode_used' in st.session_state:
                    del st.session_state['mode_used']
                st.rerun()


if __name__ == "__main__":
    main()
