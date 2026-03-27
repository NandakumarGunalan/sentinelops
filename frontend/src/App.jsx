import { useState, useEffect } from 'react'

function App() {
  const [alerts, setAlerts] = useState([])
  const [selectedAlert, setSelectedAlert] = useState(null)
  const [investigation, setInvestigation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [animatingStep, setAnimatingStep] = useState(0)
  const [currentStatus, setCurrentStatus] = useState('idle')
  const [currentRisk, setCurrentRisk] = useState(0)
  const [toolsInvoked, setToolsInvoked] = useState(0)

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    try {
      const res = await fetch('/api/alerts')
      const data = await res.json()
      setAlerts(data.alerts)
    } catch (err) {
      console.error('Failed to fetch alerts:', err)
    }
  }

  const handleAlertClick = async (alert) => {
    setSelectedAlert(alert)
    setInvestigation(null)
    setAnimatingStep(0)
    setCurrentStatus('idle')
    setCurrentRisk(0)
    setToolsInvoked(0)
  }

  const startInvestigation = async () => {
    if (!selectedAlert) return
    
    setLoading(true)
    setInvestigation(null)
    setAnimatingStep(0)
    setCurrentStatus('initializing')
    setCurrentRisk(0)
    setToolsInvoked(0)
    
    try {
      // Trigger investigation
      const res = await fetch(`/api/alerts/${selectedAlert.id}/investigate`, {
        method: 'POST'
      })
      const data = await res.json()
      
      // Fetch investigation results
      const invRes = await fetch(`/api/investigations/${data.investigation_id}`)
      const invData = await invRes.json()
      
      setInvestigation(invData)
      setLoading(false)
      
      // Animate steps with live state updates
      animateStepsLive(invData)
    } catch (err) {
      console.error('Investigation failed:', err)
      setLoading(false)
      setCurrentStatus('failed')
    }
  }

  const animateStepsLive = (invData) => {
    let step = 0
    let cumulativeTools = 0
    
    const interval = setInterval(() => {
      step++
      setAnimatingStep(step)
      
      // Update runtime state based on current step
      if (step <= invData.steps.length) {
        const currentStep = invData.steps[step - 1]
        
        // Update status
        if (step === 1) {
          setCurrentStatus('initializing')
        } else if (step < invData.steps.length) {
          setCurrentStatus('investigating')
        } else if (step === invData.steps.length) {
          setCurrentStatus('action_selected')
        }
        
        // Update risk score
        setCurrentRisk(currentStep.risk_score)
        
        // Update tools invoked count
        cumulativeTools += currentStep.tool_invocations.length
        setToolsInvoked(cumulativeTools)
      }
      
      if (step >= invData.steps.length) {
        clearInterval(interval)
        setCurrentStatus('completed')
      }
    }, 900) // 900ms per step for smooth animation
  }

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'bg-risk-critical text-white',
      high: 'bg-risk-high text-white',
      medium: 'bg-risk-medium text-white',
      low: 'bg-risk-low text-white'
    }
    return colors[severity] || 'bg-gray-500 text-white'
  }

  const getRiskColor = (score) => {
    if (score >= 80) return 'text-risk-critical'
    if (score >= 60) return 'text-risk-high'
    if (score >= 40) return 'text-risk-medium'
    return 'text-risk-low'
  }

  const getRiskLabel = (score) => {
    if (score >= 80) return 'CRITICAL'
    if (score >= 60) return 'HIGH'
    if (score >= 40) return 'MEDIUM'
    return 'LOW'
  }

  const getStepInfrastructureLabel = (stepType) => {
    const labels = {
      'initialize': '🎯 Agent Orchestrator',
      'tool_call': '🔧 Tool Invocation',
      'risk_update': '⚖️ Decision Engine',
      'conclusion': '🎬 Action Engine'
    }
    return labels[stepType] || '🤖 Agent Runtime'
  }

  const getInfrastructureDescription = (stepType) => {
    const descriptions = {
      'initialize': 'Orchestrator initializes investigation workflow',
      'tool_call': 'Tool Registry executes investigation tool',
      'risk_update': 'Risk State Manager recalculates threat level',
      'conclusion': 'Action Selector determines response'
    }
    return descriptions[stepType] || 'Agent runtime processing'
  }

  const getStatusDisplay = (status) => {
    const displays = {
      'idle': { text: 'Idle', color: 'text-slate-400' },
      'initializing': { text: 'Initializing...', color: 'text-blue-400' },
      'investigating': { text: 'Investigating...', color: 'text-yellow-400' },
      'action_selected': { text: 'Action Selected', color: 'text-purple-400' },
      'completed': { text: 'Completed', color: 'text-green-400' },
      'failed': { text: 'Failed', color: 'text-red-400' }
    }
    return displays[status] || displays['idle']
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <span className="text-3xl">🛡️</span>
            SentinelOps
            <span className="text-sm font-normal text-slate-400 ml-2">Autonomous Security Triage</span>
          </h1>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Alert List */}
          <div className="col-span-3">
            <div className="bg-slate-800 rounded-lg border border-slate-700 p-4">
              <h2 className="text-lg font-semibold mb-4 text-white">Security Alerts</h2>
              <div className="space-y-3">
                {alerts.map(alert => (
                  <div
                    key={alert.id}
                    onClick={() => handleAlertClick(alert)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      selectedAlert?.id === alert.id
                        ? 'border-blue-500 bg-slate-700'
                        : 'border-slate-600 bg-slate-750 hover:border-slate-500'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <span className={`text-xs px-2 py-1 rounded ${getSeverityColor(alert.severity)}`}>
                        {alert.severity.toUpperCase()}
                      </span>
                      <span className="text-xs text-slate-400">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <h3 className="font-medium text-sm text-white mb-1">{alert.title}</h3>
                    <p className="text-xs text-slate-400">{alert.source} • {alert.event_type}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Agent Infrastructure Panel */}
            <div className="bg-slate-800 rounded-lg border border-slate-700 p-4 mt-6">
              <h2 className="text-sm font-semibold mb-3 text-white flex items-center gap-2">
                <span>⚙️</span> Agent Infrastructure
              </h2>
              <div className="space-y-2 text-xs">
                <div className="flex items-center gap-2 text-slate-300">
                  <span className="text-blue-400">●</span>
                  <span>Orchestrator</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300">
                  <span className="text-green-400">●</span>
                  <span>Tool Registry</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300">
                  <span className="text-yellow-400">●</span>
                  <span>Risk State Manager</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300">
                  <span className="text-purple-400">●</span>
                  <span>Action Selector</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300">
                  <span className="text-cyan-400">●</span>
                  <span>Execution Trace</span>
                </div>
              </div>
            </div>

            {/* Runtime State Panel */}
            {investigation && (
              <div className="bg-slate-800 rounded-lg border border-slate-700 p-4 mt-6">
                <h2 className="text-sm font-semibold mb-3 text-white flex items-center gap-2">
                  <span>📊</span> Runtime State
                  {currentStatus !== 'completed' && currentStatus !== 'idle' && (
                    <span className="ml-auto">
                      <span className="inline-flex items-center gap-1 text-xs text-yellow-400">
                        <span className="animate-pulse">●</span> running
                      </span>
                    </span>
                  )}
                </h2>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Investigation ID:</span>
                    <span className="text-white font-mono">#{investigation.id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Status:</span>
                    <span className={`font-medium ${getStatusDisplay(currentStatus).color}`}>
                      {getStatusDisplay(currentStatus).text}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Tools Invoked:</span>
                    <span className="text-white font-medium">
                      {toolsInvoked}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Current Risk:</span>
                    <span className={`font-bold ${getRiskColor(currentRisk)}`}>
                      {currentRisk}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Severity:</span>
                    <span className={`font-medium ${getRiskColor(currentRisk)}`}>
                      {getRiskLabel(currentRisk)}
                    </span>
                  </div>
                  {investigation.finding && currentStatus === 'completed' && (
                    <div className="flex justify-between pt-2 border-t border-slate-700">
                      <span className="text-slate-400">Action:</span>
                      <span className="text-blue-400 font-medium text-xs">
                        {investigation.finding.recommended_action.replace(/_/g, ' ')}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Investigation Panel */}
          <div className="col-span-9">
            {!selectedAlert ? (
              <div className="bg-slate-800 rounded-lg border border-slate-700 p-8 text-center">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-xl font-semibold text-white mb-2">Select an Alert</h3>
                <p className="text-slate-400">Choose a security alert from the list to begin autonomous investigation</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Alert Details */}
                <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h2 className="text-xl font-bold text-white mb-2">{selectedAlert.title}</h2>
                      <p className="text-slate-300">{selectedAlert.description}</p>
                    </div>
                    <span className={`text-sm px-3 py-1 rounded ${getSeverityColor(selectedAlert.severity)}`}>
                      {selectedAlert.severity.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                    <div>
                      <span className="text-slate-400">Source:</span>
                      <span className="ml-2 text-white">{selectedAlert.source}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Event Type:</span>
                      <span className="ml-2 text-white">{selectedAlert.event_type}</span>
                    </div>
                  </div>

                  {!investigation && (
                    <button
                      onClick={startInvestigation}
                      disabled={loading}
                      className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white font-medium py-3 px-4 rounded-lg transition-colors"
                    >
                      {loading ? '🔄 Investigating...' : '🚀 Start Autonomous Investigation'}
                    </button>
                  )}
                </div>

                {/* Investigation Timeline */}
                {investigation && (
                  <>
                    <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-white">Agent Execution Trace</h3>
                        <span className="text-xs text-slate-400 bg-slate-900 px-3 py-1 rounded">
                          {investigation.step_count} steps • {investigation.steps.reduce((acc, step) => acc + step.tool_invocations.length, 0)} tool calls
                        </span>
                      </div>
                      
                      <div className="space-y-4">
                        {investigation.steps.map((step, idx) => (
                          <div
                            key={idx}
                            className={`transition-all duration-500 ${
                              idx < animatingStep ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
                            }`}
                          >
                            <div className="flex gap-4">
                              <div className="flex flex-col items-center">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                                  idx === animatingStep - 1 && currentStatus !== 'completed'
                                    ? 'bg-yellow-500 text-white animate-pulse ring-2 ring-yellow-400'
                                    : idx < animatingStep 
                                    ? 'bg-blue-600 text-white' 
                                    : 'bg-slate-700 text-slate-400'
                                }`}>
                                  {idx === animatingStep - 1 && currentStatus !== 'completed' ? '⚡' : step.step_number}
                                </div>
                                {idx < investigation.steps.length - 1 && (
                                  <div className="w-0.5 h-full bg-slate-700 mt-2"></div>
                                )}
                              </div>
                              
                              <div className="flex-1 pb-6">
                                <div className="flex items-center justify-between mb-2">
                                  <div className="flex items-center gap-2">
                                    <span className="text-sm font-semibold text-blue-400">
                                      {getStepInfrastructureLabel(step.step_type)}
                                    </span>
                                    <span className="text-xs text-slate-500">
                                      {getInfrastructureDescription(step.step_type)}
                                    </span>
                                  </div>
                                  <span className={`text-sm font-bold ${getRiskColor(step.risk_score)}`}>
                                    Risk: {step.risk_score} ({getRiskLabel(step.risk_score)})
                                  </span>
                                </div>
                                
                                <p className="text-white mb-3">{step.reasoning}</p>
                                
                                {step.tool_invocations.map((tool, toolIdx) => (
                                  <div key={toolIdx} className="bg-slate-900 rounded p-3 mt-2 border border-slate-700">
                                    <div className="flex items-center justify-between mb-2">
                                      <span className="text-sm font-medium text-green-400">
                                        🔧 Tool Registry → {tool.tool_name}
                                      </span>
                                      <span className="text-xs text-slate-500">{tool.duration_ms}ms</span>
                                    </div>
                                    <div className="text-xs text-slate-300">
                                      {Object.entries(tool.result).map(([key, value]) => (
                                        <div key={key} className="mb-1">
                                          <span className="text-slate-400">{key}:</span>{' '}
                                          <span className="text-white">
                                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                          </span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Final Finding */}
                    {animatingStep >= investigation.steps.length && (
                      <div className="bg-slate-800 rounded-lg border-2 border-blue-500 p-6 animate-pulse-once">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                          <span>🎬</span> Action Engine Output
                        </h3>
                        
                        <div className="mb-4">
                          <span className={`text-sm px-3 py-1 rounded ${getSeverityColor(investigation.finding.priority)}`}>
                            {investigation.finding.priority.toUpperCase()} PRIORITY
                          </span>
                        </div>
                        
                        <h4 className="text-xl font-bold text-white mb-3">{investigation.finding.title}</h4>
                        <p className="text-slate-300 mb-4">{investigation.finding.description}</p>
                        
                        <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
                          <h5 className="font-semibold text-white mb-2 flex items-center gap-2">
                            <span>⚡</span>
                            Recommended Action: {investigation.finding.recommended_action.replace('_', ' ').toUpperCase()}
                          </h5>
                          <pre className="text-sm text-slate-300 whitespace-pre-wrap">{investigation.finding.action_details}</pre>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
