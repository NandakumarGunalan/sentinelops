# SentinelOps 🛡️

**Autonomous Security Triage Infrastructure** - Hackathon Demo

An AI-powered security operations platform that autonomously investigates security alerts, gathers evidence through specialized tools, and provides actionable recommendations with complete audit trails.

## 🎯 What It Does

When a security alert arrives, SentinelOps:
1. **Automatically launches** a multi-step investigation
2. **Calls specialized tools** (IP reputation, user privileges, geo-location, etc.)
3. **Updates risk scores** dynamically based on evidence
4. **Generates findings** with clear recommendations
5. **Maintains complete audit trails** of every decision

## 🚀 Quick Demo Start

### Option 1: One-Command Start (Recommended)

**macOS/Linux:**
```bash
chmod +x start-demo.sh
./start-demo.sh
```

**Windows:**
```bash
start-demo.bat
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements-demo.txt
python demo_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Then open: **http://localhost:5173**

## 🎬 Demo Scenarios

The demo includes 3 pre-loaded security alerts:

1. **🔴 Privileged Account Compromise** (CRITICAL)
   - Admin account accessed from malicious Russian IP
   - Risk escalates from 80 → 98 as evidence accumulates
   - Recommendation: Immediate escalation + account disable

2. **🟠 Malware Outbreak** (HIGH)
   - Suspicious endpoint command execution detected
   - Multiple related alerts found in 24-hour window
   - Recommendation: Isolate host + full system scan

3. **🟡 Brute Force Attack** (MEDIUM)
   - 15 failed login attempts from proxy IP
   - Moderate threat level with monitoring recommendation

## 🏗️ Architecture

```
Security Alert → Autonomous Agent → Investigation Tools → Finding + Action
                      ↓
              ┌──────────────────┐
              │ Investigation    │
              │ Steps:           │
              │ 1. Initialize    │
              │ 2. Analyze       │
              │ 3. Call Tools    │
              │ 4. Update Risk   │
              │ 5. Conclude      │
              └──────────────────┘
                      ↓
              ┌──────────────────┐
              │ Tools:           │
              │ • IP Reputation  │
              │ • User Privileges│
              │ • Related Alerts │
              │ • Geo Anomaly    │
              │ • Playbooks      │
              │ • Action Sim     │
              └──────────────────┘
```

## 🎨 Key Features

- ✅ **Autonomous Investigation**: No human in the loop
- ✅ **Multi-Step Reasoning**: Clear logic at each step
- ✅ **Dynamic Risk Scoring**: Updates based on evidence
- ✅ **Tool Orchestration**: 6 specialized investigation tools
- ✅ **Complete Audit Trail**: Every decision tracked
- ✅ **Actionable Output**: Clear recommendations with steps
- ✅ **Real-Time Visualization**: Watch investigation unfold

## 📁 Project Structure

```
sentinelops/
├── backend/
│   ├── demo_server.py          # Simplified demo backend
│   ├── requirements-demo.txt   # Minimal dependencies
│   └── app/                    # Full implementation (WIP)
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main demo UI
│   │   └── index.css          # Tailwind styles
│   └── package.json
├── DEMO_QUICKSTART.md         # Detailed demo guide
└── start-demo.sh/bat          # One-command startup
```

## 🔧 Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Agent Framework**: LangGraph (concept demo)
- **Storage**: In-memory (demo) / SQLite (full version)

## 🎯 What's Simulated (Demo Mode)

For hackathon demonstration:
- ✅ Investigation logic (pre-scripted flows)
- ✅ Tool results (deterministic mock data)
- ✅ Backend storage (in-memory)
- ✅ Risk calculations (rule-based)

## 🚀 Production Roadmap

To move from demo to production:
1. Replace mock tools with real integrations (VirusTotal, IPInfo, SIEM APIs)
2. Implement true LangGraph/LLM-based autonomous decision-making
3. Add PostgreSQL for persistent storage
4. Implement authentication and RBAC
5. Add feedback loop for continuous learning
6. Scale infrastructure for concurrent investigations

## 📖 Documentation

- **[DEMO_QUICKSTART.md](DEMO_QUICKSTART.md)** - Detailed demo guide
- **[backend/README.md](backend/README.md)** - Backend architecture
- **[docs/architecture.md](docs/architecture.md)** - System design

## 🐛 Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (need 3.11+)
- Try: `pip install -r requirements-demo.txt --force-reinstall`

**Frontend won't start:**
- Check Node version: `node --version` (need 18+)
- Delete `node_modules` and run `npm install` again

**Can't see alerts:**
- Ensure backend is running on port 8000
- Check browser console for errors

## 🎤 Demo Talking Points

- **Autonomous Operation**: Agent makes decisions without human input
- **Explainable AI**: Every decision has clear reasoning
- **Bounded Autonomy**: Clear step limits and stopping conditions
- **Tool Orchestration**: Agent selects appropriate tools dynamically
- **Risk-Based Prioritization**: Severity adapts to evidence
- **Production-Ready Concept**: Demo shows path to real deployment

## 📝 License

MIT - Built for hackathon demonstration

## 🙏 Acknowledgments

Built for [Hackathon Name] - Demonstrating the future of autonomous security operations.
