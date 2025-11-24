import { useState } from "react"

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

interface PredictionResult {
  winner: string
  red_fighter: string
  blue_fighter: string
  red_win_probability: number
  blue_win_probability: number
  confidence: number
}

async function predictFight(red_fighter: string, blue_fighter: string): Promise<PredictionResult> {
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      red_fighter,
      blue_fighter,
    }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(
      errorData.detail || `Failed to get prediction: ${response.statusText}`
    )
  }

  return await response.json()
}

export default function App() {
  const [fighter1, setFighter1] = useState("")
  const [fighter2, setFighter2] = useState("")
  const [loading, setLoading] = useState(false)
  const [prediction, setPrediction] = useState<PredictionResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handlePredict = async () => {
    if (!fighter1.trim() || !fighter2.trim()) {
      setError("Please enter both fighter names")
      return
    }

    setLoading(true)
    setError(null)
    setPrediction(null)

    try {
      const result = await predictFight(fighter1.trim(), fighter2.trim())
      setPrediction(result)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to get prediction"
      setError(errorMessage)
      console.error("Prediction error:", err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-background flex items-center justify-center px-4 w-full">
      {/* Background accent */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-accent opacity-5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-secondary opacity-5 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10 w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-block mb-4">
            <span className="text-6xl font-black tracking-tighter">⚔️</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-black text-balance mb-2">
            <span className="text-primary">UFC</span> <span className="text-accent">FIGHT</span>{" "}
            <span className="text-foreground">PREDICTOR</span>
          </h1>
          <p className="text-muted-foreground text-lg">Advanced ML Predictions</p>
        </div>

        {/* Main Card */}
        <div className="bg-card border-border p-8 md:p-12 shadow-2xl rounded-lg border">
          <div className="space-y-8">
            {/* Fighter Inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Fighter 1 */}
              <div className="space-y-3">
                <label className="block text-sm font-bold text-primary uppercase tracking-wider">Fighter 1</label>
                <input
                  placeholder="Enter fighter name"
                  value={fighter1}
                  onChange={(e) => setFighter1(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handlePredict()}
                  className="bg-input border-border placeholder-muted-foreground/50 text-foreground h-12 text-base w-full px-4 py-2 border rounded-md"
                />
              </div>

              {/* Fighter 2 */}
              <div className="space-y-3">
                <label className="block text-sm font-bold text-primary uppercase tracking-wider">Fighter 2</label>
                <input
                  placeholder="Enter fighter name"
                  value={fighter2}
                  onChange={(e) => setFighter2(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handlePredict()}
                  className="bg-input border-border placeholder-muted-foreground/50 text-foreground h-12 text-base w-full px-4 py-2 border rounded-md"
                />
              </div>
            </div>

            {/* VS Divider */}
            <div className="flex items-center gap-4">
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-primary to-transparent"></div>
              <span className="text-primary font-black text-xl">VS</span>
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-primary to-transparent"></div>
            </div>

            {/* Predict Button */}
            <button
              onClick={handlePredict}
              disabled={loading || !fighter1.trim() || !fighter2.trim()}
              className="w-full bg-accent hover:bg-accent/90 text-accent-foreground font-black text-lg h-14 uppercase tracking-wider rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="inline-block animate-spin">⚡</span>
                  Predicting...
                </span>
              ) : (
                "PREDICT"
              )}
            </button>

            {/* Error Display */}
            {error && !loading && (
              <div className="mt-8 p-6 bg-destructive/10 border border-destructive/30 rounded-lg animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="text-center">
                  <p className="text-destructive font-bold text-lg">Error</p>
                  <p className="text-destructive/80 mt-2">{error}</p>
                </div>
              </div>
            )}

            {/* Prediction Result */}
            {prediction && !loading && (
              <div className="mt-8 p-6 bg-gradient-to-r from-accent/10 to-primary/10 border border-accent/30 rounded-lg animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="text-center">
                  <p className="text-muted-foreground text-sm mb-2">PREDICTED WINNER</p>
                  <p className="text-3xl font-black text-primary mb-2 uppercase text-balance">{prediction.winner}</p>

                  {/* Detailed Stats */}
                  <div className="mt-6 grid grid-cols-2 gap-4 text-left mb-6">
                    <div className="p-3 bg-card rounded border border-border">
                      <p className="text-muted-foreground text-xs uppercase tracking-wider">Red Fighter</p>
                      <p className="text-sm font-bold text-foreground">{prediction.red_fighter}</p>
                      <p className="text-xs text-accent mt-1">{(prediction.red_win_probability * 100).toFixed(1)}% win</p>
                    </div>
                    <div className="p-3 bg-card rounded border border-border">
                      <p className="text-muted-foreground text-xs uppercase tracking-wider">Blue Fighter</p>
                      <p className="text-sm font-bold text-foreground">{prediction.blue_fighter}</p>
                      <p className="text-xs text-accent mt-1">{(prediction.blue_win_probability * 100).toFixed(1)}% win</p>
                    </div>
                  </div>

                  {/* Confidence Bar */}
                  <div className="flex items-center justify-center gap-2">
                    <div className="flex-1 bg-border rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-primary to-accent h-2 rounded-full transition-all duration-500"
                        style={{ width: `${prediction.confidence * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-accent font-bold text-lg min-w-fit">
                      {(prediction.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer Info */}
        <p className="text-center text-muted-foreground text-sm mt-8">
          Predictions powered by advanced machine learning models
        </p>
      </div>
    </main>
  )
}
