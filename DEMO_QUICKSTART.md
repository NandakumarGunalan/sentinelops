# SentinelOps - Demo Quick Start

**Autonomous Security Triage Platform - Hackathon Demo**

## 🎯 What This Demo Shows

SentinelOps demonstrates an autonomous security triage agent that:
- Receives security alerts from various sources
- Automatically investigates threats using multiple tools
- Updates risk scores dynamically based on evidence
- Provides actionable recommendations with full audit trails

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.11+ 
- Node.js 18+
- npm or yarn

### Step 1: Start the Backend (Demo Server)

```bash
cd backend
pip install -r requirements-demo.txt
python demo_server.py
```

The backend will start on `http://localhost:8000`

### Step 2: Start the Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will start on `http://localhost:5173`

### Step 3: Open the Demo

Visit `http://localhost:5173` in your browser

## 🎬 Demo Scenarios

The demo includes 3 pre-loaded security alerts:

### 1. **Privileged Account Compromise** (CRITICAL)
- Admin account accessed from malicious IP in Russia
- Shows: IP reputation lookup, privileged user check, geo anomaly detection
- Risk Score: 80 → 95 → 98
- Recommendation: Escalate to human, disable account immediately

### 2. **Malware Outbreak** (HIGH)
- Suspicious endpoint command execution detected
- Shows: Playbook lookup, related alerts search, IP reputation
- Risk Score: 60 → 75
- Recommendation: Isolate host, run full scan

### 3. **Brute Force Attack** (MEDIUM)
- Multiple failed login attempts from proxy IP
- Shows: IP reputation, related alerts correlation
- Risk Score: 40 → 50
- Recommendation: Monitor account, consider lockout

## 🎥 Demo Flow

1. **Select an alert** from the left panel
2. **Click "Start Autonomous Investigation"**
3. **Watch the investigation unfold** step-by-step:
   - Each step shows reasoning and risk score updates
   - Tool invocations display real-time results
   - Risk score increases/decreases based on evidence
4. **View the final finding** with recommended actions

## 🏗️ Architecture Overview

```
┌─────────────────┐
│  Security Alert │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Autonomous Triage Agent    │
│  ┌─────────────────────┐   │
│  │ 1. Initialize       │   │
│  │ 2. Analyze Evidence │   │
│  │ 3. Call Tools       │   │
│  │ 4. Update Risk      │   │
│  │ 5. Repeat/Conclude  │   │
│  └─────────────────────┘   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Investigation Tools        │
│  • IP Reputation Lookup     │
│  • Privileged User Check    │
│  • Related Alerts Search    │
│  • Geo Anomaly Detection    │
│  • Playbook Lookup          │
│  • Action Simulator         │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Finding + Recommendation   │
└─────────────────────────────┘
```

## 🎨 Key Features Demonstrated

✅ **Autonomous Investigation**: Agent makes decisions without human input
✅ **Multi-Step Reasoning**: Clear reasoning at each investigation step
✅ **Dynamic Risk Scoring**: Risk updates based on accumulated evidence
✅ **Tool Integration**: 6 specialized investigation tools
✅ **Audit Trail**: Complete trace of every decision and action
✅ **Actionable Output**: Clear recommendations with detailed steps
✅ **Real-Time Visualization**: Watch investigation unfold in real-time

## 🔧 What's Simulated

For hackathon demo purposes, the following are simulated:

- **Backend**: Simplified FastAPI server with in-memory storage
- **Tool Results**: Deterministic mock data (no real external APIs)
- **Investigation Logic**: Pre-scripted investigation flows per scenario
- **Database**: In-memory storage (no persistent database)

## 🎯 Production Roadmap

To move from demo to production:

1. **Replace mock tools** with real integrations (VirusTotal, IPInfo, SIEM APIs)
2. **Add LangGraph/LLM** for true autonomous decision-making
3. **Implement database** (PostgreSQL) for persistent storage
4. **Add authentication** and multi-tenancy
5. **Scale infrastructure** for concurrent investigations
6. **Add feedback loop** for continuous learning

## 📊 Demo Talking Points

- **Autonomous Operation**: No human in the loop during investigation
- **Bounded Autonomy**: Clear step limits and stopping conditions
- **Explainable AI**: Every decision has clear reasoning
- **Tool Orchestration**: Agent selects appropriate tools dynamically
- **Risk-Based Prioritization**: Severity adapts to evidence
- **Actionable Intelligence**: Not just alerts, but recommended actions

## 🐛 Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (need 3.11+)
- Try: `pip install --upgrade pip`
- Try: `pip install -r requirements-demo.txt --force-reinstall`

**Frontend won't start:**
- Check Node version: `node --version` (need 18+)
- Delete `node_modules` and `package-lock.json`, then `npm install`

**Can't see alerts:**
- Make sure backend is running on port 8000
- Check browser console for errors
- Try refreshing the page

**Investigation not animating:**
- This is normal - wait 1-2 seconds after clicking "Start Investigation"
- Steps animate sequentially with 800ms delay

## 📝 License

MIT - Built for hackathon demonstration
